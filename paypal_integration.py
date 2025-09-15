"""
PayPal Payout Integration System
Handles automated payouts to users
"""

import os
import logging
import paypalrestsdk
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import User, Payout
from dotenv import load_dotenv

load_dotenv()

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # 'sandbox' or 'live'

# Payout Settings
MINIMUM_PAYOUT_AMOUNT = float(os.getenv("MINIMUM_PAYOUT_AMOUNT", "5.00"))
MAXIMUM_PAYOUT_AMOUNT = float(os.getenv("MAXIMUM_PAYOUT_AMOUNT", "10000.00"))
PAYOUT_FEE_PERCENTAGE = float(os.getenv("PAYOUT_FEE_PERCENTAGE", "0.02"))  # 2% platform fee

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PayoutRequest:
    """Payout request data structure"""
    user_id: int
    email: str
    amount: float
    currency: str = "USD"
    note: str = ""

@dataclass 
class PayoutResult:
    """Payout processing result"""
    success: bool
    batch_id: Optional[str] = None
    payout_item_id: Optional[str] = None
    error_message: Optional[str] = None
    transaction_fee: Optional[float] = None

class PayPalPayoutManager:
    """Manages PayPal payout operations"""
    
    def __init__(self):
        self.client_id = PAYPAL_CLIENT_ID
        self.client_secret = PAYPAL_CLIENT_SECRET
        self.mode = PAYPAL_MODE
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": self.mode,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("PayPal credentials not fully configured")
    
    def validate_payout_request(self, user: User, amount: float) -> Dict[str, Any]:
        """Validate a payout request"""
        errors = []
        
        # Check minimum amount
        if amount < MINIMUM_PAYOUT_AMOUNT:
            errors.append(f"Minimum payout amount is ${MINIMUM_PAYOUT_AMOUNT:.2f}")
        
        # Check maximum amount
        if amount > MAXIMUM_PAYOUT_AMOUNT:
            errors.append(f"Maximum payout amount is ${MAXIMUM_PAYOUT_AMOUNT:.2f}")
        
        # Check user balance
        if amount > user.balance:
            errors.append(f"Insufficient balance. Available: ${user.balance:.2f}")
        
        # Check PayPal email
        if not user.paypal_email or "@" not in user.paypal_email:
            errors.append("Valid PayPal email required")
        
        # Calculate fees
        transaction_fee = round(amount * PAYOUT_FEE_PERCENTAGE, 2)
        net_amount = round(amount - transaction_fee, 2)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "gross_amount": amount,
            "transaction_fee": transaction_fee,
            "net_amount": net_amount
        }
    
    def create_single_payout(self, payout_request: PayoutRequest) -> PayoutResult:
        """Create a single PayPal payout"""
        
        if not self.client_id or self.client_id == "your_paypal_client_id_here":
            logger.warning("PayPal credentials not configured - using demo mode")
            return self._create_demo_payout(payout_request)
        
        try:
            # Calculate net amount after fee
            transaction_fee = round(payout_request.amount * PAYOUT_FEE_PERCENTAGE, 2)
            net_amount = round(payout_request.amount - transaction_fee, 2)
            
            # Create unique sender batch ID
            sender_batch_id = f"PAYOUT_{payout_request.user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Create payout batch
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": sender_batch_id,
                    "email_subject": "You have received a payout from OfferEarner!",
                    "email_message": "Thank you for using our platform. Here's your payment!"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{net_amount:.2f}",
                        "currency": payout_request.currency
                    },
                    "receiver": payout_request.email,
                    "note": payout_request.note or f"Offerwall earnings payout - ${net_amount:.2f}",
                    "sender_item_id": f"ITEM_{payout_request.user_id}_{int(datetime.utcnow().timestamp())}"
                }]
            })
            
            # Execute the payout
            if payout.create(sync_mode=True):
                logger.info(f"Payout created successfully: {payout.batch_header.payout_batch_id}")
                
                return PayoutResult(
                    success=True,
                    batch_id=payout.batch_header.payout_batch_id,
                    payout_item_id=payout.items[0].payout_item_id if payout.items else None,
                    transaction_fee=transaction_fee
                )
            else:
                logger.error(f"Payout creation failed: {payout.error}")
                return PayoutResult(
                    success=False,
                    error_message=str(payout.error)
                )
                
        except Exception as e:
            logger.error(f"PayPal payout error: {e}")
            return PayoutResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_demo_payout(self, payout_request: PayoutRequest) -> PayoutResult:
        """Create a demo payout for testing without real PayPal API"""
        import uuid
        
        logger.info(f"Creating demo payout for user {payout_request.user_id}")
        
        # Simulate processing delay
        import time
        time.sleep(1)
        
        # Calculate fees like real system
        transaction_fee = round(payout_request.amount * PAYOUT_FEE_PERCENTAGE, 2)
        
        return PayoutResult(
            success=True,
            batch_id=f"DEMO_BATCH_{uuid.uuid4().hex[:8]}",
            payout_item_id=f"DEMO_ITEM_{uuid.uuid4().hex[:8]}",
            transaction_fee=transaction_fee
        )
    
    def create_batch_payout(self, payout_requests: List[PayoutRequest]) -> Dict[str, Any]:
        """Create a batch payout for multiple users"""
        
        if len(payout_requests) > 15000:
            raise ValueError("PayPal supports maximum 15,000 payments per batch")
        
        try:
            sender_batch_id = f"BATCH_{int(datetime.utcnow().timestamp())}"
            
            # Prepare payout items
            items = []
            total_fees = 0.0
            
            for req in payout_requests:
                transaction_fee = round(req.amount * PAYOUT_FEE_PERCENTAGE, 2)
                net_amount = round(req.amount - transaction_fee, 2)
                total_fees += transaction_fee
                
                items.append({
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{net_amount:.2f}",
                        "currency": req.currency
                    },
                    "receiver": req.email,
                    "note": req.note or f"Offerwall earnings payout - ${net_amount:.2f}",
                    "sender_item_id": f"ITEM_{req.user_id}_{int(datetime.utcnow().timestamp())}"
                })
            
            # Create batch payout
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": sender_batch_id,
                    "email_subject": "You have received a payout from OfferEarner!",
                    "email_message": "Thank you for using our platform. Here's your payment!"
                },
                "items": items
            })
            
            if payout.create(sync_mode=True):
                return {
                    "success": True,
                    "batch_id": payout.batch_header.payout_batch_id,
                    "total_amount": sum(req.amount for req in payout_requests),
                    "total_fees": total_fees,
                    "item_count": len(payout_requests)
                }
            else:
                return {
                    "success": False,
                    "error": str(payout.error)
                }
                
        except Exception as e:
            logger.error(f"Batch payout error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payout_status(self, batch_id: str) -> Dict[str, Any]:
        """Get the status of a payout batch"""
        try:
            payout = paypalrestsdk.Payout.find(batch_id)
            
            return {
                "success": True,
                "batch_id": batch_id,
                "batch_status": payout.batch_header.batch_status,
                "time_created": payout.batch_header.time_created,
                "time_completed": getattr(payout.batch_header, 'time_completed', None),
                "items": [
                    {
                        "payout_item_id": item.payout_item_id,
                        "transaction_status": item.transaction_status,
                        "receiver": item.receiver,
                        "amount": item.amount.value,
                        "currency": item.amount.currency
                    }
                    for item in payout.items
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting payout status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def process_payout_request(db: Session, user_id: int, amount: float) -> Dict[str, Any]:
    """Process a payout request from a user"""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
    # Initialize PayPal manager
    paypal_manager = PayPalPayoutManager()
    
    # Validate request
    validation = paypal_manager.validate_payout_request(user, amount)
    if not validation["valid"]:
        return {
            "success": False,
            "error": "Validation failed",
            "errors": validation["errors"]
        }
    
    try:
        # Check for pending payouts
        pending_payout = db.query(Payout).filter(
            Payout.user_id == user_id,
            Payout.status.in_(["pending", "processing"])
        ).first()
        
        if pending_payout:
            return {
                "success": False,
                "error": "You have a pending payout request. Please wait for it to complete."
            }
        
        # Create payout record in database
        payout_record = Payout(
            user_id=user_id,
            amount=amount,
            method="paypal",
            status="pending",
            payment_details={
                "paypal_email": user.paypal_email,
                "gross_amount": validation["gross_amount"],
                "transaction_fee": validation["transaction_fee"],
                "net_amount": validation["net_amount"]
            }
        )
        db.add(payout_record)
        db.flush()  # Get the ID
        
        # Create PayPal payout
        payout_request = PayoutRequest(
            user_id=user_id,
            email=user.paypal_email,
            amount=amount,
            note=f"Offerwall earnings payout - Request #{payout_record.id}"
        )
        
        result = paypal_manager.create_single_payout(payout_request)
        
        if result.success:
            # Update payout record with PayPal details
            payout_record.status = "processing"
            payout_record.transaction_id = result.batch_id
            payout_record.payment_details.update({
                "paypal_batch_id": result.batch_id,
                "paypal_item_id": result.payout_item_id,
                "transaction_fee_actual": result.transaction_fee
            })
            
            # Deduct amount from user balance
            user.balance -= amount
            
            db.commit()
            
            logger.info(f"Payout processed for user {user_id}: ${amount:.2f}")
            
            return {
                "success": True,
                "message": f"Payout of ${validation['net_amount']:.2f} sent to {user.paypal_email}",
                "payout_id": payout_record.id,
                "batch_id": result.batch_id,
                "gross_amount": validation["gross_amount"],
                "transaction_fee": validation["transaction_fee"],
                "net_amount": validation["net_amount"]
            }
            
        else:
            # Payout failed - update record
            payout_record.status = "failed"
            payout_record.notes = result.error_message
            db.commit()
            
            return {
                "success": False,
                "error": f"Payout failed: {result.error_message}"
            }
            
    except Exception as e:
        db.rollback()
        logger.error(f"Payout processing error: {e}")
        return {
            "success": False,
            "error": "Internal error processing payout"
        }

def get_user_payout_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Get payout history for a user"""
    
    payouts = db.query(Payout).filter(
        Payout.user_id == user_id
    ).order_by(Payout.created_at.desc()).all()
    
    return [
        {
            "id": payout.id,
            "amount": payout.amount,
            "method": payout.method,
            "status": payout.status,
            "requested_at": payout.requested_at.isoformat() if payout.requested_at else None,
            "processed_at": payout.processed_at.isoformat() if payout.processed_at else None,
            "transaction_id": payout.transaction_id,
            "payment_details": payout.payment_details
        }
        for payout in payouts
    ]

def get_platform_payout_stats(db: Session) -> Dict[str, Any]:
    """Get platform payout statistics (admin only)"""
    from sqlalchemy import func
    
    # Total payouts by status
    payout_stats = db.query(
        Payout.status,
        func.count(Payout.id).label('count'),
        func.sum(Payout.amount).label('total_amount')
    ).group_by(Payout.status).all()
    
    stats = {}
    for status, count, total in payout_stats:
        stats[status] = {
            "count": count,
            "total_amount": float(total or 0)
        }
    
    # Recent payouts
    recent_payouts = db.query(Payout).order_by(
        Payout.created_at.desc()
    ).limit(10).all()
    
    return {
        "payout_stats": stats,
        "recent_payouts": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in recent_payouts
        ]
    }
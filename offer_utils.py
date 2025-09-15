"""
Utility functions for offer management and revenue calculation
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from database import Offer, User, UserOffer, Earning
import json

# Revenue split configuration
USER_PAYOUT_PERCENTAGE = 0.50  # 50% goes to user
PLATFORM_PERCENTAGE = 0.50     # 50% goes to platform

def calculate_user_payout(full_reward_amount: float) -> float:
    """Calculate how much the user gets from the full reward amount"""
    return round(full_reward_amount * USER_PAYOUT_PERCENTAGE, 2)

def calculate_platform_revenue(full_reward_amount: float) -> float:
    """Calculate platform revenue from the full reward amount"""
    return round(full_reward_amount * PLATFORM_PERCENTAGE, 2)

def create_offer_from_external(
    db: Session,
    title: str,
    description: str,
    provider: str,
    category: str,
    full_reward_amount: float,
    time_estimate: str = None,
    external_offer_id: str = None,
    requirements: Dict[str, Any] = None
) -> Offer:
    """
    Create an offer with automatic user payout calculation
    This hides the revenue split from users
    """
    user_payout = calculate_user_payout(full_reward_amount)
    
    offer = Offer(
        title=title,
        description=description,
        provider=provider,
        category=category,
        reward_amount=full_reward_amount,  # Full amount from provider
        user_payout=user_payout,          # What user sees and gets
        time_estimate=time_estimate,
        external_offer_id=external_offer_id,
        requirements=json.dumps(requirements) if requirements else None,
        is_active=True
    )
    
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer

def complete_offer(
    db: Session, 
    user_id: int, 
    offer_id: int,
    external_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Complete an offer for a user and handle earnings
    Returns completion details
    """
    # Get user and offer
    user = db.query(User).filter(User.id == user_id).first()
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    
    if not user or not offer:
        raise ValueError("User or offer not found")
    
    # Find or create user offer record
    user_offer = db.query(UserOffer).filter(
        UserOffer.user_id == user_id,
        UserOffer.offer_id == offer_id
    ).first()
    
    if not user_offer:
        user_offer = UserOffer(
            user_id=user_id,
            offer_id=offer_id,
            status="started",
            reward_amount=offer.user_payout
        )
        db.add(user_offer)
    
    # Mark as completed
    from datetime import datetime
    user_offer.status = "completed"
    user_offer.completed_at = datetime.utcnow()
    
    # Create earning record
    earning = Earning(
        user_id=user_id,
        user_offer_id=user_offer.id,
        amount=offer.user_payout,
        type="task_completion",
        description=f"Completed: {offer.title}"
    )
    db.add(earning)
    
    # Update user balance and stats
    user.balance += offer.user_payout
    user.total_earned += offer.user_payout
    user.tasks_completed += 1
    
    db.commit()
    
    return {
        "success": True,
        "user_earned": offer.user_payout,
        "platform_earned": calculate_platform_revenue(offer.reward_amount),
        "new_balance": user.balance,
        "offer_title": offer.title
    }

def get_platform_stats(db: Session) -> Dict[str, float]:
    """
    Get platform revenue statistics (for admin use)
    """
    # This would calculate total platform earnings
    # Users never see this information
    total_offers_completed = db.query(UserOffer).filter(
        UserOffer.status == "completed"
    ).count()
    
    from sqlalchemy import func
    total_user_payouts = db.query(func.sum(Earning.amount)).scalar() or 0.0
    
    # Platform earnings = total user payouts (since we pay 50% to users)
    estimated_platform_revenue = total_user_payouts
    
    return {
        "total_offers_completed": total_offers_completed,
        "total_paid_to_users": total_user_payouts,
        "estimated_platform_revenue": estimated_platform_revenue
    }
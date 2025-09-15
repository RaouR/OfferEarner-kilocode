"""
OfferEarner - Main Application
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import uvicorn

# Import our modules
from database import init_db, get_db, User, Offer, UserOffer, Earning, Payout
from auth import (
    authenticate_user, 
    create_user, 
    create_access_token, 
    get_current_user,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import *
from offer_utils import complete_offer, get_platform_stats
from lootably_integration import sync_lootably_offers_to_database, process_lootably_postback, LootablyAPI
from demo_lootably import create_demo_lootably_offers
from paypal_integration import (
    process_payout_request, 
    get_user_payout_history, 
    get_platform_payout_stats,
    PayPalPayoutManager,
    MINIMUM_PAYOUT_AMOUNT
)

app = FastAPI(
    title="OfferEarner", 
    version="1.0.0",
    # Handle HTTPS behind proxy
    root_path=""
)

# Initialize database
init_db()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Web Routes (Templates)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Homepage"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """User registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """User login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: User = Depends(get_current_user)):
    """User dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user
    })

@app.get("/offers", response_class=HTMLResponse)
async def offers_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Available offers page"""
    return templates.TemplateResponse("offers.html", {
        "request": request,
        "current_user": current_user
    })

# Authentication API Routes
@app.post("/api/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        # Create user in database
        db_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            paypal_email=user_data.paypal_email
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(db_user)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

# Dashboard API Routes
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    # Get recent earnings (last 10)
    recent_earnings = db.query(Earning).filter(
        Earning.user_id == current_user.id
    ).order_by(Earning.created_at.desc()).limit(10).all()
    
    # Get recent offers (last 10)
    recent_offers = db.query(UserOffer).filter(
        UserOffer.user_id == current_user.id
    ).order_by(UserOffer.created_at.desc()).limit(10).all()
    
    # Count pending offers
    pending_offers = db.query(UserOffer).filter(
        UserOffer.user_id == current_user.id,
        UserOffer.status.in_(["started", "in_progress"])
    ).count()
    
    return DashboardStats(
        total_earnings=current_user.total_earned,
        completed_offers=current_user.tasks_completed,
        pending_offers=pending_offers,
        account_balance=current_user.balance,
        recent_earnings=[EarningResponse.model_validate(e) for e in recent_earnings],
        recent_offers=[UserOfferResponse.model_validate(o) for o in recent_offers]
    )

# Offers API Routes
@app.get("/api/offers", response_model=List[OfferResponse])
async def get_available_offers(
    provider: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available offers"""
    query = db.query(Offer).filter(Offer.is_active == True)
    
    if provider:
        query = query.filter(Offer.provider == provider)
    if category:
        query = query.filter(Offer.category == category)
    
    offers = query.order_by(Offer.user_payout.desc()).all()
    return [OfferResponse.model_validate(offer) for offer in offers]

@app.post("/api/offers/{offer_id}/complete")
async def complete_offer_endpoint(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete an offer for a user (for future offerwall callback integration)
    This endpoint will be called by offerwall providers when users complete offers
    """
    try:
        result = complete_offer(db, current_user.id, offer_id)
        return {
            "success": True,
            "message": f"Offer completed! You earned ${result['user_earned']:.2f}",
            "earned_amount": result['user_earned'],
            "new_balance": result['new_balance']
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete offer"
        )

# Admin endpoint (hidden from users) - for platform revenue tracking
@app.get("/api/admin/platform-stats")
async def get_platform_revenue_stats(db: Session = Depends(get_db)):
    """
    Get platform statistics - ADMIN ONLY
    Users should never see this endpoint or its data
    """
    return get_platform_stats(db)

# Lootably Integration Endpoints

@app.post("/api/admin/sync-lootably-offers")
async def sync_lootably_offers_endpoint(db: Session = Depends(get_db)):
    """
    Manually sync offers from Lootably (ADMIN ONLY)
    In production, this would be called by a scheduled task every 10-20 minutes
    """
    try:
        synced_count = sync_lootably_offers_to_database(db)
        return {
            "success": True,
            "message": f"Successfully synchronized {synced_count} offers from Lootably",
            "synced_count": synced_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync offers: {str(e)}"
        )

@app.post("/api/admin/create-demo-offers") 
async def create_demo_offers_endpoint(db: Session = Depends(get_db)):
    """
    Create demo Lootably offers for testing (ADMIN ONLY)
    This simulates what real API integration would look like
    """
    try:
        created_count = create_demo_lootably_offers(db)
        return {
            "success": True,
            "message": f"Successfully created {created_count} demo offers",
            "created_count": created_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demo offers: {str(e)}"
        )

@app.get("/api/callback/lootably")
async def lootably_postback_handler(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Lootably postback/callback when users complete offers
    This endpoint will be called by Lootably's servers
    """
    # Get all query parameters from the postback
    postback_data = dict(request.query_params)
    
    try:
        result = process_lootably_postback(db, postback_data)
        
        if result["success"]:
            # Return "1" as required by Lootably for successful processing
            return "1"
        else:
            # Return error message for failed processing
            return f"ERROR: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        # Log error and return failure response
        import logging
        logging.error(f"Lootably postback processing failed: {e}")
        return f"ERROR: {str(e)}"

@app.get("/api/offers/lootably/user/{user_id}")
async def get_personalized_lootably_offers(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized offers from Lootably for a specific user
    This provides real-time offers tailored to the user
    """
    # Ensure user can only access their own offers
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's offers"
        )
    
    try:
        api = LootablyAPI()
        
        # Get user's IP and user agent from request
        user_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Fetch personalized offers
        lootably_offers = api.fetch_user_offers(
            user_id=str(user_id),
            ip_address=user_ip,
            user_agent=user_agent
        )
        
        # Convert to our standard format
        formatted_offers = []
        for offer in lootably_offers:
            formatted_offers.append({
                "external_id": offer.offer_id,
                "title": offer.name,
                "description": offer.description,
                "user_payout": offer.currency_reward,
                "categories": offer.categories,
                "tracking_link": offer.link,
                "image": offer.image,
                "provider": "lootably",
                "conversion_rate": offer.conversion_rate
            })
        
        return {
            "success": True,
            "offers": formatted_offers,
            "count": len(formatted_offers)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch personalized offers: {str(e)}"
        )

# PayPal Payout Endpoints

@app.post("/api/payouts/request")
async def request_payout(
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a payout to PayPal
    """
    try:
        result = process_payout_request(
            db=db,
            user_id=current_user.id,
            amount=payout_data.amount
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "payout_details": {
                    "payout_id": result["payout_id"],
                    "gross_amount": result["gross_amount"],
                    "transaction_fee": result["transaction_fee"],
                    "net_amount": result["net_amount"],
                    "paypal_email": current_user.paypal_email
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payout request failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payout: {str(e)}"
        )

@app.get("/api/payouts/history")
async def get_payout_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's payout history
    """
    try:
        history = get_user_payout_history(db, current_user.id)
        return {
            "success": True,
            "payouts": history
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payout history: {str(e)}"
        )

@app.get("/api/payouts/info")
async def get_payout_info(current_user: User = Depends(get_current_user)):
    """
    Get payout information and limits
    """
    return {
        "minimum_payout": MINIMUM_PAYOUT_AMOUNT,
        "available_balance": current_user.balance,
        "paypal_email": current_user.paypal_email,
        "can_payout": current_user.balance >= MINIMUM_PAYOUT_AMOUNT
    }

@app.get("/api/admin/payouts/stats")
async def get_admin_payout_stats(db: Session = Depends(get_db)):
    """
    Get platform payout statistics (ADMIN ONLY)
    """
    try:
        stats = get_platform_payout_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payout stats: {str(e)}"
        )

# API Routes for offerwall callbacks
@app.post("/api/callback/adgem")
async def adgem_callback(request: Request):
    """Handle AdGem completion callbacks"""
    # This will be implemented when we integrate with AdGem
    return {"status": "received"}

@app.post("/api/callback/lootably") 
async def lootably_callback(request: Request):
    """Handle Lootably completion callbacks"""
    # This will be implemented when we integrate with Lootably
    return {"status": "received"}

@app.post("/api/callback/adgatemedia")
async def adgatemedia_callback(request: Request):
    """Handle AdGateMedia completion callbacks"""
    # This will be implemented when we integrate with AdGateMedia
    return {"status": "received"}

@app.post("/api/callback/cpalead")
async def cpalead_callback(request: Request):
    """Handle CPALead completion callbacks"""
    # This will be implemented when we integrate with CPALead
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
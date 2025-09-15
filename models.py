"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# User Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    paypal_email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    paypal_email: str
    balance: float
    total_earned: float
    tasks_completed: int
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Offer Models
class OfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    provider: str
    category: str
    user_payout: float
    time_estimate: Optional[str]
    is_active: bool

# User Offer Models
class StartOfferRequest(BaseModel):
    offer_id: int

class UserOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    offer: OfferResponse
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    reward_amount: Optional[float]

# Earnings Models
class EarningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    amount: float
    type: str
    description: str
    created_at: datetime

# Payout Models
class PayoutRequest(BaseModel):
    amount: float
    method: str = "paypal"

class PayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    amount: float
    method: str
    status: str
    requested_at: datetime
    processed_at: Optional[datetime]

# Dashboard Stats
class DashboardStats(BaseModel):
    total_earnings: float
    completed_offers: int
    pending_offers: int
    account_balance: float
    recent_earnings: List[EarningResponse]
    recent_offers: List[UserOfferResponse]
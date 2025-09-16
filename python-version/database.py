"""
Database models and configuration
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./offerwall.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    paypal_email = Column(String(100), nullable=False)
    balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_offers = relationship("UserOffer", back_populates="user")
    earnings = relationship("Earning", back_populates="user")
    payouts = relationship("Payout", back_populates="user")

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)  # lootably, adgem, etc.
    category = Column(String(50), nullable=False)  # survey, app, signup, video
    reward_amount = Column(Float, nullable=False)  # Full reward amount
    user_payout = Column(Float, nullable=False)   # 50% of reward amount
    time_estimate = Column(String(20))  # "5 mins", "15 mins"
    requirements = Column(JSON)  # JSON requirements
    external_offer_id = Column(String(100))  # Provider's offer ID
    callback_url = Column(String(500))  # Callback URL for tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_offers = relationship("UserOffer", back_populates="offer")

class UserOffer(Base):
    __tablename__ = "user_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    status = Column(String(20), default="started")  # started, in_progress, completed, failed
    progress_data = Column(JSON)  # Store progress information
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    reward_amount = Column(Float)  # Amount user will receive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_offers")
    offer = relationship("Offer", back_populates="user_offers")
    earning = relationship("Earning", back_populates="user_offer", uselist=False)

class Earning(Base):
    __tablename__ = "earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_offer_id = Column(Integer, ForeignKey("user_offers.id"))
    amount = Column(Float, nullable=False)
    type = Column(String(30), nullable=False)  # task_completion, bonus, referral
    description = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="earnings")
    user_offer = relationship("UserOffer", back_populates="earning")

class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(20), nullable=False)  # paypal, gift_card, crypto
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    payment_details = Column(JSON)  # Payment-specific details
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    transaction_id = Column(String(100))  # PayPal transaction ID, etc.
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payouts")

class OfferCallback(Base):
    __tablename__ = "offer_callbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    external_offer_id = Column(String(100))
    external_user_id = Column(String(100))
    status = Column(String(20))  # completed, failed, etc.
    reward_amount = Column(Float)
    callback_data = Column(JSON)  # Raw callback data
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
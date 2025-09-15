"""
Seed database with sample offers
"""

from sqlalchemy.orm import sessionmaker
from database import engine, Offer, init_db
import json

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_offers():
    """Add sample offers to database"""
    # Initialize database first
    init_db()
    
    db = SessionLocal()
    
    # Check if offers already exist
    if db.query(Offer).first():
        print("Offers already exist in database")
        return
    
    sample_offers = [
        {
            "title": "Survey: Shopping Habits",
            "description": "Complete a 5-minute survey about your shopping preferences and earn money.",
            "provider": "lootably",
            "category": "survey",
            "reward_amount": 1.00,
            "user_payout": 0.50,  # Automatically calculated as 50% of reward_amount
            "time_estimate": "5 mins",
            "external_offer_id": "LOOT_SURVEY_001",
            "requirements": {"age_min": 18, "country": ["US", "CA", "UK"]},
            "is_active": True
        },
        {
            "title": "App Install: Mobile Game",
            "description": "Download and play this popular mobile game for 2 minutes to earn rewards.",
            "provider": "adgem",
            "category": "app",
            "reward_amount": 2.50,
            "user_payout": 1.25,
            "time_estimate": "2 mins",
            "external_offer_id": "ADGEM_APP_001",
            "requirements": {"device": ["iOS", "Android"], "play_time": 120},
            "is_active": True
        },
        {
            "title": "Sign Up: Streaming Service",
            "description": "Sign up for a free trial of a popular streaming service and get rewarded.",
            "provider": "adgatemedia",
            "category": "signup",
            "reward_amount": 4.00,
            "user_payout": 2.00,
            "time_estimate": "3 mins",
            "external_offer_id": "AGM_STREAM_001",
            "requirements": {"email_verification": True, "credit_card": False},
            "is_active": True
        },
        {
            "title": "Email Submit: Newsletter",
            "description": "Subscribe to a newsletter and confirm your email address to earn.",
            "provider": "cpalead",
            "category": "email",
            "reward_amount": 0.60,
            "user_payout": 0.30,
            "time_estimate": "1 min",
            "external_offer_id": "CPL_EMAIL_001",
            "requirements": {"email_confirmation": True},
            "is_active": True
        },
        {
            "title": "Watch Video: Product Demo",
            "description": "Watch a 3-minute product demonstration video to completion.",
            "provider": "lootably",
            "category": "video",
            "reward_amount": 0.80,
            "user_payout": 0.40,
            "time_estimate": "3 mins",
            "external_offer_id": "LOOT_VIDEO_001",
            "requirements": {"watch_percentage": 100},
            "is_active": True
        },
        {
            "title": "Survey: Food Preferences",
            "description": "Share your opinions about food and dining habits in this quick survey.",
            "provider": "adgem",
            "category": "survey",
            "reward_amount": 1.50,
            "user_payout": 0.75,
            "time_estimate": "7 mins",
            "external_offer_id": "ADGEM_FOOD_001",
            "requirements": {"age_min": 21, "completion_rate": 95},
            "is_active": True
        },
        {
            "title": "App Install: Fitness Tracker",
            "description": "Download a fitness tracking app and create an account.",
            "provider": "cpalead",
            "category": "app",
            "reward_amount": 3.00,
            "user_payout": 1.50,
            "time_estimate": "5 mins",
            "external_offer_id": "CPL_FITNESS_001",
            "requirements": {"account_creation": True, "profile_completion": 80},
            "is_active": True
        },
        {
            "title": "Sign Up: Financial Service",
            "description": "Register for a financial planning service and receive a welcome bonus.",
            "provider": "adgatemedia",
            "category": "signup",
            "reward_amount": 6.00,
            "user_payout": 3.00,
            "time_estimate": "10 mins",
            "external_offer_id": "AGM_FINANCE_001",
            "requirements": {"age_min": 25, "income_verification": False},
            "is_active": True
        }
    ]
    
    # Add offers to database
    for offer_data in sample_offers:
        # Convert requirements dict to JSON string
        requirements_json = json.dumps(offer_data["requirements"])
        offer_data["requirements"] = requirements_json
        
        db_offer = Offer(**offer_data)
        db.add(db_offer)
    
    db.commit()
    db.close()
    print(f"Added {len(sample_offers)} sample offers to database")

if __name__ == "__main__":
    seed_offers()
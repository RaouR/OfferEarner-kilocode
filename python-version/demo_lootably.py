"""
Demo Lootably Integration - Works without real API credentials
"""

from typing import List
from sqlalchemy.orm import Session
from database import Offer
from offer_utils import create_offer_from_external
from lootably_integration import LootablyOffer

def create_demo_lootably_offers(db: Session) -> int:
    """
    Create demo Lootably offers for testing the integration
    This simulates what would happen when syncing from the real API
    """
    
    demo_offers = [
        {
            "offer_id": "LOOT_DEMO_001",
            "name": "Download FitTracker Pro",
            "description": "Download and open this popular fitness tracking app. Create an account to earn your reward.",
            "revenue": 3.00,  # What we'd receive from Lootably
            "currency_reward": 1.50,  # What user sees (our 50% split)
            "categories": ["app", "health"],
            "countries": ["US", "CA", "UK"],
            "devices": ["android", "iphone"],
            "link": "https://lootably.com/track/demo001",
            "image": "https://example.com/fittracker.png",
            "type": "singlestep",
            "conversion_rate": 85.5
        },
        {
            "offer_id": "LOOT_DEMO_002", 
            "name": "Netflix Premium Trial",
            "description": "Sign up for Netflix Premium and watch for 3 days. Cancel anytime during the trial period.",
            "revenue": 8.00,
            "currency_reward": 4.00,
            "categories": ["freetrial", "video"],
            "countries": ["US", "CA", "UK", "AU"],
            "devices": ["*"],
            "link": "https://lootably.com/track/demo002",
            "image": "https://example.com/netflix.png",
            "type": "singlestep",
            "conversion_rate": 67.2
        },
        {
            "offer_id": "LOOT_DEMO_003",
            "name": "Gaming Survey - 15 minutes",
            "description": "Share your gaming preferences in this detailed survey. Must complete all questions to earn reward.",
            "revenue": 2.50,
            "currency_reward": 1.25,
            "categories": ["survey", "game"],
            "countries": ["US", "CA", "UK", "AU", "DE", "FR"],
            "devices": ["*"],
            "link": "https://lootably.com/track/demo003",
            "image": "https://example.com/gaming-survey.png",
            "type": "singlestep",
            "conversion_rate": 92.1
        },
        {
            "offer_id": "LOOT_DEMO_004",
            "name": "Crypto Learning Course",
            "description": "Complete this interactive cryptocurrency course. Finish all 5 modules and pass the final quiz.",
            "revenue": 12.00,
            "currency_reward": 6.00,
            "categories": ["signup", "quiz"],
            "countries": ["US", "CA", "UK"],
            "devices": ["*"],
            "link": "https://lootably.com/track/demo004", 
            "image": "https://example.com/crypto-course.png",
            "type": "multistep",
            "conversion_rate": 45.8
        },
        {
            "offer_id": "LOOT_DEMO_005",
            "name": "Watch Advertising Videos",
            "description": "Watch 10 short video advertisements. Each video is 30 seconds long.",
            "revenue": 1.00,
            "currency_reward": 0.50,
            "categories": ["video"],
            "countries": ["*"],
            "devices": ["*"],
            "link": "https://lootably.com/track/demo005",
            "image": "https://example.com/video-ads.png",
            "type": "singlestep",
            "conversion_rate": 98.5
        }
    ]
    
    synced_count = 0
    
    for demo_data in demo_offers:
        try:
            # Check if offer already exists
            existing_offer = db.query(Offer).filter(
                Offer.external_offer_id == demo_data["offer_id"],
                Offer.provider == "lootably"
            ).first()
            
            if existing_offer:
                # Update existing demo offer
                existing_offer.title = demo_data["name"]
                existing_offer.description = demo_data["description"]
                existing_offer.reward_amount = demo_data["revenue"]
                existing_offer.user_payout = demo_data["currency_reward"]
                existing_offer.is_active = True
                print(f"Updated demo offer: {demo_data['name']}")
            else:
                # Create new demo offer
                create_offer_from_external(
                    db=db,
                    title=demo_data["name"],
                    description=demo_data["description"],
                    provider="lootably",
                    category=demo_data["categories"][0],
                    full_reward_amount=demo_data["revenue"],
                    external_offer_id=demo_data["offer_id"],
                    requirements={
                        "countries": demo_data["countries"],
                        "devices": demo_data["devices"],
                        "conversion_rate": demo_data["conversion_rate"],
                        "tracking_link": demo_data["link"],
                        "image": demo_data["image"],
                        "type": demo_data["type"],
                        "demo": True  # Mark as demo offer
                    }
                )
                print(f"Created demo offer: {demo_data['name']}")
            
            synced_count += 1
            
        except Exception as e:
            print(f"Error creating demo offer {demo_data['offer_id']}: {e}")
            continue
    
    db.commit()
    print(f"Created {synced_count} demo Lootably offers")
    return synced_count

if __name__ == "__main__":
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        create_demo_lootably_offers(db)
    finally:
        db.close()
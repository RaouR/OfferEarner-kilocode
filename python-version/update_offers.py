"""
Update existing offers to ensure proper user payout calculation
"""

from sqlalchemy.orm import sessionmaker
from database import engine, Offer
from offer_utils import calculate_user_payout

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_offer_payouts():
    """Update all offers to ensure user payouts are exactly 50% of reward amount"""
    db = SessionLocal()
    
    offers = db.query(Offer).all()
    print(f"Updating {len(offers)} offers...")
    
    for offer in offers:
        # Recalculate user payout to ensure it's exactly 50%
        correct_user_payout = calculate_user_payout(offer.reward_amount)
        
        if abs(offer.user_payout - correct_user_payout) > 0.001:  # Allow for tiny floating point differences
            print(f"Updating {offer.title}: ${offer.user_payout} -> ${correct_user_payout}")
            offer.user_payout = correct_user_payout
    
    db.commit()
    db.close()
    print("All offers updated!")

if __name__ == "__main__":
    update_offer_payouts()
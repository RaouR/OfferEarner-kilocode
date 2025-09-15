"""
Quick script to check database content
"""

from sqlalchemy.orm import sessionmaker
from database import engine, User, Offer
import json

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    """Check what's in the database"""
    db = SessionLocal()
    
    # Count offers
    offer_count = db.query(Offer).count()
    print(f"Total offers in database: {offer_count}")
    
    # Show first 3 offers
    if offer_count > 0:
        offers = db.query(Offer).limit(3).all()
        print("\nFirst 3 offers:")
        for offer in offers:
            print(f"- {offer.title} | ${offer.user_payout} | {offer.provider}")
    
    # Count users
    user_count = db.query(User).count()
    print(f"\nTotal users in database: {user_count}")
    
    db.close()

if __name__ == "__main__":
    check_database()
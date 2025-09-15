#!/usr/bin/env python3
"""
Lootably Management Script
Use this to test and manage Lootably integration
"""

import sys
import argparse
from sqlalchemy.orm import sessionmaker
from database import engine, Offer
from lootably_integration import sync_lootably_offers_to_database, LootablyAPI

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    """Test connection to Lootably API"""
    print("Testing Lootably API connection...")
    
    api = LootablyAPI()
    
    if not api.placement_id or not api.api_key:
        print("❌ ERROR: Lootably credentials not configured!")
        print("Please set LOOTABLY_PLACEMENT_ID and LOOTABLY_API_KEY in your .env file")
        return False
    
    print(f"✅ Placement ID: {api.placement_id}")
    print(f"✅ API Key: {api.api_key[:8]}...")
    
    # Test fetching offers
    offers = api.fetch_catalogue_offers()
    if offers:
        print(f"✅ Successfully fetched {len(offers)} offers from Lootably!")
        
        # Show first few offers
        print("\nSample offers:")
        for i, offer in enumerate(offers[:3]):
            print(f"  {i+1}. {offer.name} - ${offer.currency_reward:.2f}")
        
        return True
    else:
        print("❌ Failed to fetch offers. Check your credentials and network connection.")
        return False

def sync_offers():
    """Sync offers from Lootably to database"""
    print("Syncing offers from Lootably...")
    
    db = SessionLocal()
    try:
        synced_count = sync_lootably_offers_to_database(db)
        print(f"✅ Successfully synchronized {synced_count} offers!")
        
        # Show database stats
        total_offers = db.query(Offer).count()
        lootably_offers = db.query(Offer).filter(Offer.provider == "lootably").count()
        
        print(f"📊 Database now has {total_offers} total offers ({lootably_offers} from Lootably)")
        
    except Exception as e:
        print(f"❌ Error syncing offers: {e}")
    finally:
        db.close()

def list_offers():
    """List all offers in database"""
    db = SessionLocal()
    try:
        offers = db.query(Offer).order_by(Offer.user_payout.desc()).all()
        
        print(f"📋 Total offers in database: {len(offers)}")
        print("-" * 80)
        print(f"{'Title':<40} {'Provider':<12} {'Payout':<8} {'Status'}")
        print("-" * 80)
        
        for offer in offers:
            status = "Active" if offer.is_active else "Inactive"
            print(f"{offer.title:<40} {offer.provider:<12} ${offer.user_payout:<7.2f} {status}")
            
    except Exception as e:
        print(f"❌ Error listing offers: {e}")
    finally:
        db.close()

def test_postback_validation():
    """Test postback validation logic"""
    print("Testing postback validation...")
    
    api = LootablyAPI()
    
    if not api.postback_secret:
        print("⚠️  Warning: No postback secret configured - validation will be skipped")
        return
    
    # Test with sample data
    test_data = {
        "userID": "123",
        "ip": "192.168.1.1",
        "revenue": "1.00",
        "currencyReward": "0.50"
    }
    
    # Generate expected hash
    import hashlib
    hash_string = f"{test_data['userID']}{test_data['ip']}{test_data['revenue']}{test_data['currencyReward']}{api.postback_secret}"
    expected_hash = hashlib.sha256(hash_string.encode()).hexdigest()
    
    # Test validation
    is_valid = api.validate_postback(
        test_data["userID"],
        test_data["ip"],
        test_data["revenue"],
        test_data["currencyReward"],
        expected_hash
    )
    
    if is_valid:
        print("✅ Postback validation working correctly!")
        print(f"Expected hash: {expected_hash}")
    else:
        print("❌ Postback validation failed!")

def main():
    parser = argparse.ArgumentParser(description="Lootably Management Script")
    parser.add_argument("command", choices=[
        "test", "sync", "list", "validate"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "test":
        test_connection()
    elif args.command == "sync":
        sync_offers()
    elif args.command == "list":
        list_offers()
    elif args.command == "validate":
        test_postback_validation()

if __name__ == "__main__":
    main()
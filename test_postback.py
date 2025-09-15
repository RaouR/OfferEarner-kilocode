"""
Test Lootably postback simulation
"""

import requests
import hashlib
from database import SessionLocal, User

def simulate_lootably_postback():
    """Simulate a Lootably postback for testing"""
    
    db = SessionLocal()
    
    # Get our test user (created during registration)
    user = db.query(User).first()
    if not user:
        print("❌ No test user found. Please register a user first.")
        return
    
    print(f"🧪 Testing postback for user: {user.username} (ID: {user.id})")
    
    # Test postback data (simulating what Lootably would send)
    postback_data = {
        "userID": str(user.id),
        "transactionID": "DEMO_TXN_67890",
        "offerID": "LOOT_DEMO_003",  # Gaming Survey
        "offerName": "Gaming Survey - 15 minutes", 
        "revenue": "2.50",  # What we receive
        "currencyReward": "1.25",  # What user gets
        "status": "1",  # Completed
        "ip": "192.168.1.100"
    }
    
    # For demo purposes, we'll skip hash validation by not including it
    # In production, you'd generate the proper hash
    
    # Construct callback URL
    base_url = "http://localhost:8001"
    callback_url = f"{base_url}/api/callback/lootably"
    
    # Add parameters to URL
    params = "&".join([f"{k}={v}" for k, v in postback_data.items()])
    full_url = f"{callback_url}?{params}"
    
    print(f"🔗 Callback URL: {full_url}")
    
    try:
        # Send the postback
        response = requests.get(full_url)
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.text.strip('"') == "1":
            print("✅ Postback processed successfully!")
            
            # Check user's balance
            db.refresh(user)
            print(f"💰 User's new balance: ${user.balance:.2f}")
            print(f"📈 Total earned: ${user.total_earned:.2f}")
            print(f"🎯 Tasks completed: {user.tasks_completed}")
            
        else:
            print("❌ Postback processing failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending postback: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    simulate_lootably_postback()
#!/usr/bin/env python3
"""
Complete Offerwall Flow Demo
Demonstrates the entire user journey from registration to earnings
"""

import requests
import json
import time
from database import SessionLocal, User

BASE_URL = "http://localhost:8001"

def demo_complete_flow():
    """Demonstrate the complete offerwall user flow"""
    print("🚀 Starting Complete Offerwall Flow Demo")
    print("=" * 60)
    
    # Step 1: Register a new demo user
    print("\n📝 Step 1: User Registration")
    register_data = {
        "username": "demouser",
        "email": "demo@example.com", 
        "password": "demopass123",
        "paypal_email": "demo.paypal@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data["access_token"]
            user_info = auth_data["user"]
            print(f"✅ User registered: {user_info['username']}")
            print(f"📧 Email: {user_info['email']}")
            print(f"💰 Initial balance: ${user_info['balance']:.2f}")
        else:
            print("❌ Registration failed - user might already exist")
            # Try to login instead
            login_data = {"email": register_data["email"], "password": register_data["password"]}
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data["access_token"]
                user_info = auth_data["user"]
                print(f"✅ User logged in: {user_info['username']}")
            else:
                print("❌ Login also failed")
                return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Step 2: Browse available offers
    print("\n🎯 Step 2: Browse Available Offers")
    try:
        response = requests.get(f"{BASE_URL}/api/offers")
        offers = response.json()
        
        print(f"📋 Found {len(offers)} total offers")
        lootably_offers = [o for o in offers if o["provider"] == "lootably"]
        print(f"🏷️  Lootably offers: {len(lootably_offers)}")
        
        # Show top 3 offers
        print("\n💎 Top Offers:")
        for i, offer in enumerate(offers[:3]):
            print(f"  {i+1}. {offer['title']} - ${offer['user_payout']:.2f} ({offer['provider']})")
    
    except Exception as e:
        print(f"❌ Error fetching offers: {e}")
        return
    
    # Step 3: Get dashboard stats (before completing offers)
    print("\n📊 Step 3: Check Dashboard (Before)")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        stats = response.json()
        print(f"💰 Current balance: ${stats['account_balance']:.2f}")
        print(f"📈 Total earned: ${stats['total_earnings']:.2f}")
        print(f"✅ Completed offers: {stats['completed_offers']}")
        print(f"⏳ Pending offers: {stats['pending_offers']}")
    except Exception as e:
        print(f"❌ Error fetching dashboard: {e}")
    
    # Step 4: Simulate completing multiple offers
    print("\n🎮 Step 4: Complete Offers (Simulated)")
    
    demo_completions = [
        {
            "offer_id": "LOOT_DEMO_001",
            "offer_name": "Download FitTracker Pro",
            "revenue": "3.00",
            "reward": "1.50"
        },
        {
            "offer_id": "LOOT_DEMO_002", 
            "offer_name": "Netflix Premium Trial",
            "revenue": "8.00",
            "reward": "4.00"
        },
        {
            "offer_id": "LOOT_DEMO_005",
            "offer_name": "Watch Advertising Videos",
            "revenue": "1.00", 
            "reward": "0.50"
        }
    ]
    
    for i, completion in enumerate(demo_completions):
        print(f"\n  🔄 Completing offer {i+1}/3: {completion['offer_name']}")
        
        # Simulate postback from Lootably
        postback_params = {
            "userID": str(user_info["id"]),
            "transactionID": f"DEMO_TXN_{int(time.time())}_{i}",
            "offerID": completion["offer_id"],
            "offerName": completion["offer_name"],
            "revenue": completion["revenue"],
            "currencyReward": completion["reward"],
            "status": "1",
            "ip": "192.168.1.100"
        }
        
        # Build callback URL
        params_str = "&".join([f"{k}={v}" for k, v in postback_params.items()])
        callback_url = f"{BASE_URL}/api/callback/lootably?{params_str}"
        
        try:
            response = requests.get(callback_url)
            if response.text.strip('"') == "1":
                print(f"    ✅ Completed! User earned ${completion['reward']}")
            else:
                print(f"    ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between completions
    
    # Step 5: Check final dashboard stats
    print("\n📊 Step 5: Final Dashboard Stats")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        final_stats = response.json()
        print(f"💰 Final balance: ${final_stats['account_balance']:.2f}")
        print(f"📈 Total earned: ${final_stats['total_earnings']:.2f}")
        print(f"✅ Completed offers: {final_stats['completed_offers']}")
        print(f"⏳ Pending offers: {final_stats['pending_offers']}")
        
        if final_stats["recent_earnings"]:
            print("\n🏆 Recent Earnings:")
            for earning in final_stats["recent_earnings"][:3]:
                print(f"  • {earning['description']} - ${earning['amount']:.2f}")
                
    except Exception as e:
        print(f"❌ Error fetching final dashboard: {e}")
    
    # Step 6: Platform revenue summary (admin view)
    print("\n💼 Step 6: Platform Revenue (Admin View)")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/platform-stats")
        platform_stats = response.json()
        print(f"🏢 Total paid to users: ${platform_stats['total_paid_to_users']:.2f}")
        print(f"💰 Estimated platform revenue: ${platform_stats['estimated_platform_revenue']:.2f}")
        print(f"🎯 Total offers completed: {platform_stats['total_offers_completed']}")
    except Exception as e:
        print(f"❌ Error fetching platform stats: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete! The offerwall system is working perfectly!")
    print("Users can now register, browse offers, complete tasks, and earn money.")
    print("The platform automatically handles the 50/50 revenue split behind the scenes.")

if __name__ == "__main__":
    demo_complete_flow()
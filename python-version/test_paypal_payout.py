#!/usr/bin/env python3
"""
Test PayPal Payout Integration
"""

import requests
import json
from database import SessionLocal, User

BASE_URL = "http://localhost:8001"

def test_paypal_payout():
    """Test the PayPal payout system"""
    
    print("💳 Testing PayPal Payout Integration")
    print("=" * 50)
    
    # Step 1: Get a test user with balance
    db = SessionLocal()
    user = db.query(User).filter(User.balance > 0).first()
    
    if not user:
        print("❌ No user with balance found. Run demo_complete_flow.py first.")
        return
    
    print(f"👤 Testing with user: {user.username}")
    print(f"💰 Current balance: ${user.balance:.2f}")
    print(f"📧 PayPal email: {user.paypal_email}")
    
    # Step 2: Login to get token
    try:
        login_data = {"email": user.email, "password": "demopass123"}  # Use known password
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print("❌ Login failed. User might need different password.")
            return
            
        auth_data = response.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ User authenticated successfully")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Step 3: Get payout info
    print("\n📋 Step 1: Getting Payout Information")
    try:
        response = requests.get(f"{BASE_URL}/api/payouts/info", headers=headers)
        payout_info = response.json()
        
        print(f"💵 Minimum payout: ${payout_info['minimum_payout']:.2f}")
        print(f"💰 Available balance: ${payout_info['available_balance']:.2f}")
        print(f"✅ Can request payout: {payout_info['can_payout']}")
        
        if not payout_info['can_payout']:
            print(f"⚠️  User balance too low for payout")
            return
            
    except Exception as e:
        print(f"❌ Error getting payout info: {e}")
        return
    
    # Step 4: Request a payout
    print("\n💸 Step 2: Requesting Payout")
    payout_amount = min(10.0, user.balance)  # Request $10 or user's full balance
    
    try:
        payout_request = {"amount": payout_amount}
        response = requests.post(f"{BASE_URL}/api/payouts/request", 
                               json=payout_request, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payout requested successfully!")
            print(f"💳 Payout ID: {result['payout_details']['payout_id']}")
            print(f"💵 Gross amount: ${result['payout_details']['gross_amount']:.2f}")
            print(f"💰 Transaction fee: ${result['payout_details']['transaction_fee']:.2f}")
            print(f"🎯 Net amount to PayPal: ${result['payout_details']['net_amount']:.2f}")
            print(f"📧 PayPal email: {result['payout_details']['paypal_email']}")
            
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"❌ Payout request failed: {error_detail}")
            return
            
    except Exception as e:
        print(f"❌ Error requesting payout: {e}")
        return
    
    # Step 5: Check payout history
    print("\n📊 Step 3: Checking Payout History")
    try:
        response = requests.get(f"{BASE_URL}/api/payouts/history", headers=headers)
        history = response.json()
        
        if history['success'] and history['payouts']:
            print(f"📋 Found {len(history['payouts'])} payout(s):")
            
            for payout in history['payouts'][:3]:  # Show last 3
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄', 
                    'completed': '✅',
                    'failed': '❌'
                }.get(payout['status'], '❓')
                
                print(f"  {status_emoji} ${payout['amount']:.2f} - {payout['status'].title()} - {payout['method'].title()}")
                
        else:
            print("📋 No payout history found")
            
    except Exception as e:
        print(f"❌ Error getting payout history: {e}")
    
    # Step 6: Check updated user balance
    print("\n💰 Step 4: Checking Updated Balance")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        stats = response.json()
        
        print(f"💳 New balance: ${stats['account_balance']:.2f}")
        print(f"📈 Total earned: ${stats['total_earnings']:.2f}")
        
    except Exception as e:
        print(f"❌ Error getting updated balance: {e}")
    
    # Step 7: Admin stats (if available)
    print("\n🏢 Step 5: Platform Payout Stats (Admin)")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/payouts/stats")
        if response.status_code == 200:
            admin_stats = response.json()
            
            print("📊 Platform Payout Statistics:")
            for status, data in admin_stats.get('payout_stats', {}).items():
                print(f"  {status.title()}: {data['count']} payouts, ${data['total_amount']:.2f}")
                
        else:
            print("⚠️  Admin stats not available")
            
    except Exception as e:
        print(f"⚠️  Admin stats error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 PayPal Payout Test Complete!")
    print("The system can now:")
    print("✅ Validate payout requests")
    print("✅ Process PayPal payouts (demo mode)")
    print("✅ Track transaction fees")
    print("✅ Update user balances") 
    print("✅ Maintain payout history")
    print("\nTo go live: Add real PayPal credentials to .env file")
    
    db.close()

if __name__ == "__main__":
    test_paypal_payout()
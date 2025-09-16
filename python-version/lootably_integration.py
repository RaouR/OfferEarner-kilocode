"""
Lootably Offerwall API Integration
"""

import os
import hashlib
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from database import Offer, User, OfferCallback
from offer_utils import create_offer_from_external
from dotenv import load_dotenv

load_dotenv()

# Lootably API Configuration
LOOTABLY_API_URL = "https://api.lootably.com/api/v2/offers/get"
LOOTABLY_PLACEMENT_ID = os.getenv("LOOTABLY_PLACEMENT_ID", "")
LOOTABLY_API_KEY = os.getenv("LOOTABLY_API_KEY", "")
LOOTABLY_POSTBACK_SECRET = os.getenv("LOOTABLY_POSTBACK_SECRET", "")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LootablyOffer:
    """Lootably offer data structure"""
    offer_id: str
    name: str
    description: str
    revenue: float  # What we receive from Lootably
    currency_reward: float  # What user receives (should be 50% of revenue)
    categories: List[str]
    countries: List[str]
    devices: List[str]
    link: str
    image: str
    type: str  # "singlestep" or "multistep"
    conversion_rate: float

class LootablyAPI:
    """Handle Lootably API interactions"""
    
    def __init__(self):
        self.placement_id = LOOTABLY_PLACEMENT_ID
        self.api_key = LOOTABLY_API_KEY
        self.postback_secret = LOOTABLY_POSTBACK_SECRET
        
        if not all([self.placement_id, self.api_key]):
            logger.warning("Lootably credentials not configured. Integration disabled.")
    
    def fetch_catalogue_offers(self, 
                              categories: Optional[List[str]] = None,
                              countries: Optional[List[str]] = None,
                              devices: Optional[List[str]] = None) -> List[LootablyOffer]:
        """
        Fetch offers from Lootably Catalogue API
        This should be called every 10-20 minutes to keep offers updated
        """
        if not self.placement_id or not self.api_key:
            logger.error("Lootably credentials not configured")
            return []
        
        payload = {
            "apiKey": self.api_key,
            "placementID": self.placement_id
        }
        
        # Add optional filters
        if categories:
            payload["categories"] = categories
        if countries:
            payload["countries"] = countries
        if devices:
            payload["devices"] = devices
        
        try:
            response = requests.post(LOOTABLY_API_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"Lootably API error: {data.get('message', 'Unknown error')}")
                return []
            
            offers = []
            for offer_data in data.get("data", {}).get("offers", []):
                try:
                    # Parse offer data
                    lootably_offer = self._parse_offer_data(offer_data)
                    offers.append(lootably_offer)
                except Exception as e:
                    logger.error(f"Error parsing offer {offer_data.get('offerID', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Fetched {len(offers)} offers from Lootably")
            return offers
            
        except requests.RequestException as e:
            logger.error(f"Error fetching offers from Lootably: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def _parse_offer_data(self, offer_data: Dict[str, Any]) -> LootablyOffer:
        """Parse raw offer data from Lootably API"""
        
        # Handle both singlestep and multistep offers
        if offer_data["type"] == "singlestep":
            revenue = float(offer_data["revenue"]) if offer_data["revenue"] != "variable" else 0.0
            currency_reward = float(offer_data["currencyReward"]) if offer_data["currencyReward"] != "variable" else 0.0
        else:
            # For multistep, sum up all goal revenues
            revenue = sum(float(goal["revenue"]) for goal in offer_data.get("goals", []))
            currency_reward = sum(float(goal["currencyReward"]) for goal in offer_data.get("goals", []))
        
        return LootablyOffer(
            offer_id=offer_data["offerID"],
            name=offer_data["name"],
            description=offer_data["description"],
            revenue=revenue,
            currency_reward=currency_reward,
            categories=offer_data.get("categories", []),
            countries=offer_data.get("countries", []),
            devices=offer_data.get("devices", []),
            link=offer_data["link"],
            image=offer_data.get("image", ""),
            type=offer_data["type"],
            conversion_rate=float(offer_data.get("conversionRate", 0))
        )
    
    def fetch_user_offers(self, user_id: str, ip_address: str, user_agent: str) -> List[LootablyOffer]:
        """
        Fetch personalized offers for a specific user
        This provides real-time, user-specific results
        """
        if not self.placement_id or not self.api_key:
            logger.error("Lootably credentials not configured")
            return []
        
        payload = {
            "apiKey": self.api_key,
            "placementID": self.placement_id,
            "userData": {
                "userID": user_id,
                "userAgentHeader": user_agent,
                "ipAddress": ip_address
            }
        }
        
        try:
            response = requests.post(LOOTABLY_API_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"Lootably API error: {data.get('message', 'Unknown error')}")
                return []
            
            offers = []
            for offer_data in data.get("data", {}).get("offers", []):
                try:
                    lootably_offer = self._parse_offer_data(offer_data)
                    offers.append(lootably_offer)
                except Exception as e:
                    logger.error(f"Error parsing user offer {offer_data.get('offerID', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Fetched {len(offers)} personalized offers for user {user_id}")
            return offers
            
        except requests.RequestException as e:
            logger.error(f"Error fetching user offers from Lootably: {e}")
            return []
    
    def validate_postback(self, user_id: str, ip: str, revenue: str, 
                         currency_reward: str, received_hash: str) -> bool:
        """
        Validate that a postback request came from Lootably
        """
        if not self.postback_secret or self.postback_secret == "your_postback_secret_here":
            logger.warning("Postback secret not configured - allowing for demo/development")
            return True  # Allow for development without secret
        
        # Skip validation if no hash provided (demo mode)
        if not received_hash:
            logger.info("No hash provided - demo mode")
            return True
        
        # Concatenate values for hashing
        hash_string = f"{user_id}{ip}{revenue}{currency_reward}{self.postback_secret}"
        
        # Generate SHA256 hash
        expected_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        return expected_hash == received_hash

def sync_lootably_offers_to_database(db: Session) -> int:
    """
    Sync offers from Lootably to our database
    Returns number of offers synchronized
    """
    api = LootablyAPI()
    
    # Fetch all offers from Lootably
    lootably_offers = api.fetch_catalogue_offers()
    
    if not lootably_offers:
        logger.warning("No offers received from Lootably")
        return 0
    
    synced_count = 0
    
    for lootably_offer in lootably_offers:
        try:
            # Check if offer already exists
            existing_offer = db.query(Offer).filter(
                Offer.external_offer_id == lootably_offer.offer_id,
                Offer.provider == "lootably"
            ).first()
            
            if existing_offer:
                # Update existing offer
                existing_offer.title = lootably_offer.name
                existing_offer.description = lootably_offer.description
                existing_offer.reward_amount = lootably_offer.revenue
                existing_offer.user_payout = lootably_offer.currency_reward
                existing_offer.is_active = True
                logger.info(f"Updated existing offer: {lootably_offer.name}")
            else:
                # Create new offer using our utility function
                create_offer_from_external(
                    db=db,
                    title=lootably_offer.name,
                    description=lootably_offer.description,
                    provider="lootably",
                    category=lootably_offer.categories[0] if lootably_offer.categories else "other",
                    full_reward_amount=lootably_offer.revenue,
                    external_offer_id=lootably_offer.offer_id,
                    requirements={
                        "countries": lootably_offer.countries,
                        "devices": lootably_offer.devices,
                        "conversion_rate": lootably_offer.conversion_rate,
                        "tracking_link": lootably_offer.link,
                        "image": lootably_offer.image,
                        "type": lootably_offer.type
                    }
                )
                logger.info(f"Created new offer: {lootably_offer.name}")
            
            synced_count += 1
            
        except Exception as e:
            logger.error(f"Error syncing offer {lootably_offer.offer_id}: {e}")
            continue
    
    db.commit()
    logger.info(f"Synchronized {synced_count} offers from Lootably")
    return synced_count

def process_lootably_postback(db: Session, postback_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a postback/callback from Lootably when user completes an offer
    """
    api = LootablyAPI()
    
    # Extract postback parameters
    user_id = postback_data.get("userID", "")
    transaction_id = postback_data.get("transactionID", "")
    offer_id = postback_data.get("offerID", "")
    offer_name = postback_data.get("offerName", "")
    revenue = postback_data.get("revenue", "0")
    currency_reward = postback_data.get("currencyReward", "0")
    status = postback_data.get("status", "0")
    ip_address = postback_data.get("ip", "")
    received_hash = postback_data.get("hash", "")
    
    # Validate postback
    if not api.validate_postback(user_id, ip_address, revenue, currency_reward, received_hash):
        logger.error(f"Invalid postback hash for transaction {transaction_id}")
        return {"success": False, "error": "Invalid postback signature"}
    
    # Check if this is a completed conversion
    if status != "1":
        logger.warning(f"Received postback with non-completion status: {status}")
        return {"success": False, "error": "Non-completion status"}
    
    try:
        # Find the user in our database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            logger.error(f"User {user_id} not found for postback")
            return {"success": False, "error": "User not found"}
        
        # Find the offer
        offer = db.query(Offer).filter(
            Offer.external_offer_id == offer_id,
            Offer.provider == "lootably"
        ).first()
        
        if not offer:
            logger.error(f"Offer {offer_id} not found for postback")
            return {"success": False, "error": "Offer not found"}
        
        # Record the callback
        callback = OfferCallback(
            provider="lootably",
            user_id=int(user_id),
            external_offer_id=offer_id,
            external_user_id=user_id,
            status="completed",
            reward_amount=float(currency_reward),
            callback_data={
                "transaction_id": transaction_id,
                "offer_name": offer_name,
                "revenue": float(revenue),
                "ip_address": ip_address,
                "hash": received_hash
            },
            processed=False
        )
        db.add(callback)
        
        # Complete the offer for the user
        from offer_utils import complete_offer
        result = complete_offer(db, int(user_id), offer.id, {
            "lootably_transaction_id": transaction_id,
            "lootably_revenue": float(revenue)
        })
        
        # Mark callback as processed
        from datetime import datetime
        callback.processed = True
        callback.processed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Successfully processed Lootably postback for user {user_id}, offer {offer_id}")
        
        return {
            "success": True,
            "user_earned": result["user_earned"],
            "platform_earned": result["platform_earned"],
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing Lootably postback: {e}")
        return {"success": False, "error": str(e)}
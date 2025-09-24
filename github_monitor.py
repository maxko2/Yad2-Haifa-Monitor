import requests
import json
import logging
import os
import time
import random
from datetime import datetime
from yad2_database import Yad2Database
from yad2_notification_manager import send_property_notifications

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubYad2Monitor:
    """
    Clean Yad2 monitor for GitHub Actions using the working Next.js endpoint.
    Fetches ~20 properties every 10 minutes to build a comprehensive database over time.
    """
    
    def __init__(self):
        self.db = Yad2Database()
        
        # Working Next.js API endpoint
        self.api_url = "https://www.yad2.co.il/realestate/_next/data/gtPYHLspEBp8Prnb6dWsk/rent.json"
        
        # Search parameters for Haifa rentals
        self.params = {
            'maxPrice': '5000',      # Max ₪5,000
            'minRooms': '2.5',       # At least 2.5 rooms 
            'maxRooms': '5',         # Max 5 rooms
            'topArea': '25',         # Haifa area
            'area': '5'              # Haifa sub-area
        }
        
        # Headers to look like a real browser with randomization
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]
        
        self.headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Email recipients - get from environment or use defaults
        self.email_recipients = [
            os.getenv('EMAIL_RECIPIENT_1', 'maxkobzer@gmail.com'),
            os.getenv('EMAIL_RECIPIENT_2', 'yaelbrgr2@gmail.com')
        ]
    
    def fetch_properties(self) -> list:
        """Fetch properties from the Next.js API endpoint with anti-detection measures."""
        try:
            # Add random delay to seem more human-like
            delay = random.uniform(2, 8)
            logger.info(f"Waiting {delay:.1f}s before request...")
            time.sleep(delay)
            
            logger.info(f"Fetching properties from Next.js API...")
            
            # Use session for better connection handling
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(
                self.api_url,
                params=self.params,
                timeout=45
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code != 200:
                logger.error(f"HTTP error {response.status_code}")
                logger.error(f"Response content (first 200 chars): {response.text[:200]}")
                return []
            
            # Check if we got CAPTCHA'd
            if 'ShieldSquare' in response.text or 'captcha' in response.text.lower():
                logger.warning("🛡️ CAPTCHA detected - request blocked by anti-bot protection")
                logger.info("This is normal behavior from cloud servers. System will retry in next cycle.")
                return []
            
            # Parse JSON response
            try:
                data = response.json()
                logger.info("✅ Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Response content (first 500 chars): {response.text[:500]}")
                return []
            
            # Extract properties from Next.js response structure
            properties = []
            
            if 'pageProps' in data and 'searchResults' in data['pageProps']:
                search_results = data['pageProps']['searchResults']
                
                if 'feed' in search_results and 'feed_items' in search_results['feed']:
                    feed_items = search_results['feed']['feed_items']
                    
                    for item in feed_items:
                        if item.get('type') == 'ad':
                            prop = self.parse_property(item)
                            if prop:
                                properties.append(prop)
                
                logger.info(f"✅ Found {len(properties)} properties")
            else:
                logger.warning("Unexpected API response structure")
            
            return properties
            
        except requests.exceptions.Timeout:
            logger.error("⏰ Request timeout - server taking too long to respond")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def parse_property(self, item: dict) -> dict:
        """Parse a single property from the API response."""
        try:
            # Extract basic info
            property_data = {
                'id': str(item.get('id', '')),
                'title': item.get('title', ''),
                'price': int(item.get('price', 0)),
                'rooms': float(item.get('rooms', 0)),
                'floor': int(item.get('floor', 0)),
                'size': int(item.get('square_meter', 0)),
                'images': item.get('images', []),
                'description': item.get('description_text', ''),
                'contact_name': item.get('contact_name', ''),
                'phones': item.get('phones', [])
            }
            
            # Extract location
            if 'address_info' in item:
                addr_info = item['address_info']
                property_data['address'] = addr_info.get('address', '')
                property_data['neighborhood'] = addr_info.get('neighborhood', '')
            
            # Extract amenities
            amenities = []
            if 'additional_info_text' in item:
                amenities.append(item['additional_info_text'])
            if 'tags' in item:
                amenities.extend([tag.get('text', '') for tag in item['tags']])
            property_data['amenities'] = amenities
            
            # Contact info
            property_data['phone'] = property_data['phones'][0] if property_data['phones'] else ''
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error parsing property: {e}")
            return None
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        logger.info("🏠 Starting Yad2 Haifa monitoring cycle...")
        start_time = datetime.now()
        
        try:
            # Clean up old properties (mark as inactive after 2 weeks)
            self.db.cleanup_old_properties(days=14)
            
            # Fetch current properties
            properties = self.fetch_properties()
            
            if not properties:
                logger.warning("No properties fetched - cycle aborted")
                return
            
            # Process each property
            new_count = 0
            price_change_count = 0
            
            for prop in properties:
                is_new, price_changed = self.db.add_or_update_property(prop)
                
                if is_new:
                    new_count += 1
                    logger.info(f"✨ New: {prop['title']} - ₪{prop['price']:,}")
                
                if price_changed:
                    price_change_count += 1
                    logger.info(f"💰 Price change: {prop['title']} - ₪{prop['price']:,}")
            
            # Send email notifications for changes
            total_changes = new_count + price_change_count
            if total_changes > 0:
                logger.info(f"📧 Sending notifications for {new_count} new + {price_change_count} price changes")
                
                try:
                    send_property_notifications(
                        new_properties=self.db.get_new_properties(hours=1),
                        price_changes=self.db.get_price_changes(hours=1),
                        recipients=self.email_recipients
                    )
                    logger.info("✅ Email notifications sent successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Email error: {e}")
            
            else:
                logger.info("📧 No changes - no notifications sent")
            
            # Get database statistics
            stats = self.db.get_property_count()
            
            # Log summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Cycle completed in {duration:.1f}s")
            logger.info(f"📊 Processed: {len(properties)} properties")
            logger.info(f"📊 Database: {stats['active']} active properties, {stats['total']} total")
            
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
            raise

def main():
    """Main entry point for GitHub Actions."""
    monitor = GitHubYad2Monitor()
    monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
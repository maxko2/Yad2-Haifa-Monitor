import requests
import json
import logging
import os
import time
import random
from datetime import datetime
import urllib.parse
from yad2_database import Yad2Database
from yad2_notification_manager import send_property_notifications

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedYad2Monitor:
    """
    Advanced Yad2 monitor with sophisticated anti-detection techniques
    """
    
    def __init__(self):
        self.db = Yad2Database()
        
        # Working Next.js API endpoint
        self.api_url = "https://www.yad2.co.il/realestate/_next/data/gtPYHLspEBp8Prnb6dWsk/rent.json"
        
        # Search parameters for Haifa rentals
        self.params = {
            'maxPrice': '5000',
            'minRooms': '2.5',
            'maxRooms': '5',
            'topArea': '25',
            'area': '5'
        }
        
        # Email recipients
        self.email_recipients = [
            os.getenv('EMAIL_RECIPIENT_1', 'maxkobzer@gmail.com'),
            os.getenv('EMAIL_RECIPIENT_2', 'yaelbrgr2@gmail.com')
        ]
        
        # Create session with advanced settings
        self.session = requests.Session()
        self.setup_advanced_session()
    
    def setup_advanced_session(self):
        """Setup session with advanced anti-detection measures"""
        
        # Realistic user agents (latest Chrome versions)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        selected_ua = random.choice(user_agents)
        
        # Build realistic headers that match what a real browser sends
        headers = {
            'User-Agent': selected_ua,
            'Accept': '*/*',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.yad2.co.il/',
            'Origin': 'https://www.yad2.co.il',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors', 
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        self.session.headers.update(headers)
        
        # Add common cookies that browsers have
        self.session.cookies.update({
            'lang': 'he',
            'currency': 'NIS',
        })
    
    def simulate_human_browsing(self):
        """Simulate human browsing patterns before making the API call"""
        try:
            logger.info("🤖 Simulating human browsing behavior...")
            
            # Step 1: Visit main page first
            main_page_delay = random.uniform(1, 3)
            time.sleep(main_page_delay)
            
            main_response = self.session.get(
                'https://www.yad2.co.il/',
                timeout=10
            )
            logger.info(f"📄 Visited main page: {main_response.status_code}")
            
            # Step 2: Visit real estate section
            realestate_delay = random.uniform(2, 5)
            time.sleep(realestate_delay)
            
            realestate_response = self.session.get(
                'https://www.yad2.co.il/realestate/rent',
                timeout=10
            )
            logger.info(f"🏠 Visited realestate section: {realestate_response.status_code}")
            
            # Step 3: Random delay before API call
            api_delay = random.uniform(3, 8)
            logger.info(f"⏳ Final delay before API call: {api_delay:.1f}s")
            time.sleep(api_delay)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not complete browsing simulation: {e}")
            time.sleep(random.uniform(2, 5))  # Fallback delay
            return False
    
    def fetch_properties_with_stealth(self):
        """Fetch properties using stealth techniques"""
        try:
            # Step 1: Simulate human browsing
            self.simulate_human_browsing()
            
            # Step 2: Update headers to match Next.js request
            api_headers = self.session.headers.copy()
            api_headers.update({
                'Accept': 'application/json',
                'x-nextjs-data': '1',
                'Referer': 'https://www.yad2.co.il/realestate/rent'
            })
            
            logger.info("🔍 Making stealth API request...")
            
            # Step 3: Make the actual API request
            response = self.session.get(
                self.api_url,
                params=self.params,
                headers=api_headers,
                timeout=30
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Check response
            if response.status_code != 200:
                logger.error(f"❌ HTTP error {response.status_code}")
                return []
            
            # Check for CAPTCHA
            content_preview = response.text[:500].lower()
            if any(keyword in content_preview for keyword in ['shieldsquare', 'captcha', 'blocked']):
                logger.warning("🛡️ CAPTCHA detected despite stealth measures")
                return []
            
            # Try to parse JSON
            try:
                data = response.json()
                logger.info("✅ Successfully parsed JSON response!")
                return self.extract_properties_from_response(data)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error: {e}")
                logger.error(f"Response preview: {response.text[:200]}")
                return []
            
        except requests.exceptions.Timeout:
            logger.error("⏰ Request timeout")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def extract_properties_from_response(self, data):
        """Extract properties from the API response"""
        properties = []
        
        try:
            # The actual structure is pageProps.feed.private for property listings
            if 'pageProps' in data and 'feed' in data['pageProps']:
                feed = data['pageProps']['feed']
                
                # Check for private listings (main property feed)
                if 'private' in feed:
                    private_listings = feed['private']
                    logger.info(f"📊 Found {len(private_listings)} private listings")
                    
                    for item in private_listings:
                        prop = self.parse_property_new_structure(item)
                        if prop:
                            properties.append(prop)
                
                # Also check for other feed types if they exist
                for feed_type in ['business', 'promoted']:
                    if feed_type in feed and isinstance(feed[feed_type], list):
                        logger.info(f"📊 Found {len(feed[feed_type])} {feed_type} listings")
                        for item in feed[feed_type]:
                            prop = self.parse_property_new_structure(item)
                            if prop:
                                properties.append(prop)
                
                logger.info(f"🏠 Successfully extracted {len(properties)} total properties")
            else:
                logger.warning("⚠️ No feed data found in response")
                
        except Exception as e:
            logger.error(f"❌ Error extracting properties: {e}")
        
        return properties
    
    def parse_property_new_structure(self, item):
        """Parse a single property from the new API response structure"""
        try:
            # Extract basic property info - using token as ID since it's more unique
            property_data = {
                'id': str(item.get('token', item.get('orderId', ''))),
                'title': '',
                'price': 0,
                'rooms': 0,
                'floor': 0,
                'size': 0,
                'images': [],
                'description': '',
                'contact_name': '',
                'phone': '',
                'address': '',
                'neighborhood': '',
                'amenities': []
            }
            
            # Extract price
            if 'price' in item:
                try:
                    property_data['price'] = int(item['price'])
                except:
                    property_data['price'] = 0
            
            # Extract rooms from additionalDetails
            if 'additionalDetails' in item:
                details = item['additionalDetails']
                if 'roomsCount' in details:
                    try:
                        property_data['rooms'] = float(details['roomsCount'])
                    except:
                        property_data['rooms'] = 0
                
                # Extract size
                if 'squareMeter' in details:
                    try:
                        property_data['size'] = int(details['squareMeter'])
                    except:
                        property_data['size'] = 0
            
            # Extract floor from address
            if 'address' in item and 'house' in item['address'] and 'floor' in item['address']['house']:
                try:
                    property_data['floor'] = int(item['address']['house']['floor'])
                except:
                    property_data['floor'] = 0
            
            # Extract address information
            if 'address' in item:
                addr = item['address']
                address_parts = []
                
                if 'street' in addr and 'text' in addr['street']:
                    street = addr['street']['text']
                    if 'house' in addr and 'number' in addr['house']:
                        street += f" {addr['house']['number']}"
                    address_parts.append(street)
                
                if 'neighborhood' in addr and 'text' in addr['neighborhood']:
                    property_data['neighborhood'] = addr['neighborhood']['text']
                    address_parts.append(property_data['neighborhood'])
                
                if 'city' in addr and 'text' in addr['city']:
                    address_parts.append(addr['city']['text'])
                
                property_data['address'] = ', '.join(address_parts)
            
            # Extract images from metaData
            if 'metaData' in item and 'images' in item['metaData']:
                property_data['images'] = item['metaData']['images']
            
            # Extract amenities from tags
            if 'tags' in item:
                property_data['amenities'] = [tag.get('name', '') for tag in item['tags'] if tag.get('name')]
            
            # Build title
            room_text = f"{property_data['rooms']} חדרים" if property_data['rooms'] > 0 else ""
            location_text = property_data['neighborhood'] or 'חיפה'
            property_type = ""
            
            if 'additionalDetails' in item and 'property' in item['additionalDetails'] and 'text' in item['additionalDetails']['property']:
                property_type = item['additionalDetails']['property']['text']
            
            title_parts = []
            if room_text:
                title_parts.append(room_text)
            if property_type:
                title_parts.append(property_type)
            if location_text:
                title_parts.append(f"ב{location_text}")
            
            property_data['title'] = ' '.join(title_parts) or f"נכס ב{location_text}"
            
            # Extract description from various sources
            description_parts = []
            if property_type and property_type not in property_data['title']:
                description_parts.append(property_type)
            if property_data['amenities']:
                description_parts.extend(property_data['amenities'][:3])  # First 3 amenities
            property_data['description'] = ', '.join(description_parts)
            
            # Only return properties with essential data
            if property_data['id'] and property_data['price'] > 0 and property_data['address']:
                logger.info(f"✨ Parsed: {property_data['title']} - ₪{property_data['price']:,}")
                return property_data
            else:
                logger.debug(f"⚠️ Skipping property with missing data: ID={property_data['id']}, Price={property_data['price']}, Address={property_data['address']}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error parsing property: {e}")
            return None
    
    def run_monitoring_cycle(self):
        """Run monitoring cycle with advanced techniques"""
        logger.info("🏠 Starting Advanced Yad2 Haifa monitoring cycle...")
        start_time = datetime.now()
        
        try:
            # Clean up old properties
            self.db.cleanup_old_properties(days=14)
            
            # Fetch properties with stealth
            properties = self.fetch_properties_with_stealth()
            
            if not properties:
                logger.warning("❌ No properties fetched - cycle aborted")
                return
            
            # Process properties
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
            
            # Send notifications
            total_changes = new_count + price_change_count
            if total_changes > 0:
                logger.info(f"📧 Sending notifications: {new_count} new + {price_change_count} changes")
                
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
            
            # Log summary
            stats = self.db.get_property_count()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Cycle completed in {duration:.1f}s")
            logger.info(f"📊 Processed: {len(properties)} properties")
            logger.info(f"📊 Database: {stats['active']} active properties, {stats['total']} total")
            
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
            raise

def main():
    """Main entry point"""
    monitor = AdvancedYad2Monitor()
    monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()

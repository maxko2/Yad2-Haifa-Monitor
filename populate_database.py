"""
One-time database population script
Goes through 20 pages of Yad2 pagination to populate the database with existing properties
This creates a baseline so future monitoring can detect truly new properties
"""

import requests
import json
import logging
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from yad2_database import Yad2Database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabasePopulator:
    """
    Populates database with existing properties from multiple pages
    """
    
    def __init__(self):
        self.db = Yad2Database()
        
        # Working Next.js API endpoint
        self.api_url = "https://www.yad2.co.il/realestate/_next/data/gtPYHLspEBp8Prnb6dWsk/rent.json"
        
        # Base search parameters for Haifa rentals
        self.base_params = {
            'maxPrice': '5000',
            'minRooms': '2.5',
            'maxRooms': '5',
            'topArea': '25',
            'area': '5'
        }
        
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
            realestate_delay = random.uniform(2, 4)
            time.sleep(realestate_delay)
            
            realestate_response = self.session.get(
                'https://www.yad2.co.il/realestate/rent',
                timeout=10
            )
            logger.info(f"🏠 Visited realestate section: {realestate_response.status_code}")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not complete browsing simulation: {e}")
            time.sleep(random.uniform(2, 5))  # Fallback delay
            return False
    
    def fetch_page_properties(self, page_number):
        """Fetch properties from a specific page"""
        try:
            # Add page parameter to base params
            params = self.base_params.copy()
            if page_number > 1:
                params['page'] = str(page_number)
            
            # For each new page, simulate browsing behavior again
            if page_number > 1:
                # Longer delays for pagination to avoid detection
                delay = random.uniform(10, 20)  # Much longer delays
                logger.info(f"⏳ Extended delay before page {page_number}: {delay:.1f}s")
                time.sleep(delay)
                
                # Re-visit sections to simulate real browsing
                if page_number % 3 == 0:  # Every 3rd page, simulate more browsing
                    logger.info(f"🤖 Simulating additional browsing for page {page_number}")
                    try:
                        # Visit a few property details pages to look more human
                        browse_response = self.session.get(
                            'https://www.yad2.co.il/realestate/rent',
                            timeout=10
                        )
                        time.sleep(random.uniform(2, 4))
                    except:
                        pass
            
            # Update headers for API request with fresh referrer
            api_headers = self.session.headers.copy()
            api_headers.update({
                'Accept': 'application/json',
                'x-nextjs-data': '1',
                'Referer': f'https://www.yad2.co.il/realestate/rent{"?page=" + str(page_number) if page_number > 1 else ""}'
            })
            
            logger.info(f"🔍 Fetching page {page_number} with stealth measures...")
            
            # Make the API request
            response = self.session.get(
                self.api_url,
                params=params,
                headers=api_headers,
                timeout=30
            )
            
            logger.info(f"📡 Page {page_number} response: {response.status_code}")
            
            # Check response
            if response.status_code != 200:
                logger.error(f"❌ HTTP error {response.status_code} on page {page_number}")
                return []
            
            # Check for CAPTCHA more thoroughly
            content_preview = response.text[:1000].lower()
            if any(keyword in content_preview for keyword in ['shieldsquare', 'captcha', 'blocked', 'bot', 'verification']):
                logger.warning(f"🛡️ CAPTCHA/Bot detection on page {page_number}")
                logger.info(f"Response preview: {response.text[:200]}")
                return []
            
            # Try to parse JSON
            try:
                data = response.json()
                return self.extract_properties_from_response(data, page_number)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error on page {page_number}: {e}")
                logger.info(f"Response preview: {response.text[:300]}")
                return []
            
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Request timeout on page {page_number}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error on page {page_number}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error on page {page_number}: {e}")
            return []
    
    def extract_properties_from_response(self, data, page_number):
        """Extract properties from the API response"""
        properties = []
        
        try:
            # The actual structure is pageProps.feed.private for property listings
            if 'pageProps' in data and 'feed' in data['pageProps']:
                feed = data['pageProps']['feed']
                
                # Check for private listings (main property feed)
                if 'private' in feed:
                    private_listings = feed['private']
                    
                    for item in private_listings:
                        prop = self.parse_property(item)
                        if prop:
                            properties.append(prop)
                
                # Also check for other feed types if they exist
                for feed_type in ['business', 'promoted']:
                    if feed_type in feed and isinstance(feed[feed_type], list):
                        for item in feed[feed_type]:
                            prop = self.parse_property(item)
                            if prop:
                                properties.append(prop)
                
                logger.info(f"🏠 Page {page_number}: extracted {len(properties)} properties")
            else:
                logger.warning(f"⚠️ No feed data found on page {page_number}")
                
        except Exception as e:
            logger.error(f"❌ Error extracting properties from page {page_number}: {e}")
        
        return properties
    
    def parse_property(self, item):
        """Parse a single property from the API response"""
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
                return property_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error parsing property: {e}")
            return None
    
    def populate_database(self, max_pages=20):
        """Main function to populate database with properties from multiple pages"""
        logger.info("🏠 Starting Yad2 Haifa Database Population")
        logger.info("=" * 60)
        start_time = datetime.now()
        
        try:
            # Initial browsing simulation
            self.simulate_human_browsing()
            
            all_properties = []
            pages_processed = 0
            consecutive_empty_pages = 0
            
            for page in range(1, max_pages + 1):
                properties = self.fetch_page_properties(page)
                
                if properties:
                    all_properties.extend(properties)
                    pages_processed += 1
                    consecutive_empty_pages = 0
                    
                    logger.info(f"✅ Page {page}: Found {len(properties)} properties")
                else:
                    consecutive_empty_pages += 1
                    logger.warning(f"⚠️ Page {page}: No properties found")
                    
                    # If we get 3 consecutive empty pages, likely reached the end
                    if consecutive_empty_pages >= 3:
                        logger.info(f"🛑 Reached end of results after {page} pages (3 consecutive empty pages)")
                        break
                
                # Show progress
                total_found = len(all_properties)
                logger.info(f"📊 Progress: Page {page}/{max_pages} - Total properties: {total_found}")
            
            # Process all found properties
            if all_properties:
                logger.info(f"💾 Processing {len(all_properties)} total properties...")
                
                new_count = 0
                updated_count = 0
                
                for prop in all_properties:
                    is_new, price_changed = self.db.add_or_update_property(prop)
                    
                    if is_new:
                        new_count += 1
                    elif price_changed:
                        updated_count += 1
                
                # Get final statistics
                stats = self.db.get_property_count()
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info("=" * 60)
                logger.info("🎉 DATABASE POPULATION COMPLETED!")
                logger.info(f"⏱️  Total time: {duration:.1f} seconds")
                logger.info(f"📄 Pages processed: {pages_processed}")
                logger.info(f"🏠 Properties found: {len(all_properties)}")
                logger.info(f"✨ New properties added: {new_count}")
                logger.info(f"💰 Price updates: {updated_count}")
                logger.info(f"📊 Database totals: {stats['active']} active, {stats['total']} total")
                logger.info("=" * 60)
                logger.info("🎯 Database is now populated! Future monitoring will detect new properties.")
                
            else:
                logger.error("❌ No properties found across all pages!")
                
        except Exception as e:
            logger.error(f"❌ Error during database population: {e}")
            raise

def main():
    """Main entry point"""
    try:
        populator = DatabasePopulator()
        populator.populate_database(max_pages=20)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()

import requests
import json
import hashlib
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from yad2_database import Yad2Database

class SmartYad2APISampler:
    """
    Smart Yad2 API sampler with database storage and anti-detection features.
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.api_config = config_manager.get_api_config()
        self.monitoring_config = config_manager.get_monitoring_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.db = Yad2Database()
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
    
    def get_random_headers(self) -> Dict[str, str]:
        """Generate randomized headers to avoid detection."""
        base_headers = self.api_config.get('headers', {}).copy()
        
        # Only randomize user agent if configured, keep other headers intact
        if self.monitoring_config.get('random_user_agents', True):
            base_headers['User-Agent'] = random.choice(self.user_agents)
        
        # Keep the language setting stable to avoid CAPTCHA
        # base_headers['Accept-Language'] already set from config
        
        # Sometimes add cache control
        if random.random() < 0.3:
            base_headers['Cache-Control'] = 'no-cache'
        
        return base_headers
    
    def add_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay between requests."""
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"Adding random delay: {delay:.1f}s")
        time.sleep(delay)
    
    def extract_properties_from_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract property listings from Yad2 API response."""
        try:
            data_path = self.monitoring_config.get('data_path', 'pageProps.feed.private')
            
            current = data
            for path_part in data_path.split('.'):
                if isinstance(current, dict) and path_part in current:
                    current = current[path_part]
                else:
                    self.logger.warning(f"Path '{data_path}' not found in response")
                    return []
            
            if isinstance(current, list):
                return current
            else:
                self.logger.warning(f"Expected list at '{data_path}', got {type(current)}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error extracting properties: {e}")
            return []
    
    def format_property_for_database(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format a Yad2 property for database storage."""
        try:
            formatted = {
                'id': property_data.get('token', 'N/A'),
                'price': property_data.get('price', None),
                'property_type': property_data.get('additionalDetails', {}).get('property', {}).get('text', 'N/A'),
                'rooms': property_data.get('additionalDetails', {}).get('roomsCount', None),
                'size_sqm': property_data.get('additionalDetails', {}).get('squareMeter', None),
                'url': f"https://www.yad2.co.il/realestate/rent/{property_data.get('token', '')}"
            }
            
            # Extract address
            address_data = property_data.get('address', {})
            address_parts = []
            
            if 'street' in address_data and 'text' in address_data['street']:
                street = address_data['street']['text']
                house_num = address_data.get('house', {}).get('number', '')
                if house_num:
                    address_parts.append(f"{street} {house_num}")
                else:
                    address_parts.append(street)
            
            if 'neighborhood' in address_data and 'text' in address_data['neighborhood']:
                address_parts.append(address_data['neighborhood']['text'])
            
            if 'city' in address_data and 'text' in address_data['city']:
                address_parts.append(address_data['city']['text'])
            
            formatted['address'] = ', '.join(address_parts) if address_parts else 'N/A'
            
            # Floor information
            if 'house' in address_data and 'floor' in address_data['house']:
                formatted['floor'] = str(address_data['house']['floor'])
            else:
                formatted['floor'] = 'N/A'
            
            # Property condition
            condition = property_data.get('additionalDetails', {}).get('propertyCondition', {})
            if isinstance(condition, dict) and 'id' in condition:
                condition_map = {1: 'חדש', 2: 'משופץ', 3: 'דרוש שיפוץ', 4: 'במצב רע'}
                formatted['condition'] = condition_map.get(condition['id'], 'לא צוין')
            else:
                formatted['condition'] = 'לא צוין'
            
            # Image
            formatted['image_url'] = property_data.get('metaData', {}).get('coverImage', '')
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Error formatting property: {e}")
            return {'id': property_data.get('token', 'unknown'), 'error': 'Format error'}
    
    def fetch_and_store_properties(self) -> Tuple[bool, Dict[str, int], str]:
        """
        Fetch properties from API and store in database.
        
        Returns:
            Tuple of (success, stats, error_message)
        """
        error_message = None
        
        try:
            # Add longer random delay before request (2-8 seconds)
            self.add_random_delay(2.0, 8.0)
            
            url = self.api_config.get('url')
            headers = self.get_random_headers()
            method = self.api_config.get('method', 'GET')
            timeout = self.api_config.get('timeout', 30)
            
            if not url:
                raise ValueError("API URL not configured")
            
            self.logger.info(f"Fetching Yad2 data from API...")
            
            # Add session for connection reuse and better bot detection avoidance
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.request(
                method=method,
                url=url,
                timeout=timeout
            )
            
            # Handle different response codes
            if response.status_code == 403:
                error_message = "Access forbidden - Yad2 anti-bot protection triggered. Try again later."
                self.logger.error(error_message)
                # Don't raise_for_status() to avoid generic error message
            elif response.status_code == 429:
                error_message = "Rate limited by Yad2. Waiting longer between requests."
                self.logger.error(error_message)
            else:
                response.raise_for_status()
                raw_data = response.json()
                
                # Calculate response hash for logging
                response_hash = hashlib.md5(
                    json.dumps(raw_data, sort_keys=True).encode()
                ).hexdigest()[:10]
                
                # Extract properties from the nested structure
                properties = self.extract_properties_from_response(raw_data)
                
                if properties:
                    # Format properties for database
                    formatted_properties = []
                    for prop in properties:
                        formatted = self.format_property_for_database(prop)
                        if formatted.get('id') != 'N/A':
                            formatted_properties.append(formatted)
                    
                    # Save to database
                    stats = self.db.save_properties(formatted_properties)
                    
                    # Log the run
                    self.db.log_monitoring_run(
                        properties_found=len(formatted_properties),
                        new_properties=stats['new'],
                        success=True,
                        api_response_hash=response_hash
                    )
                    
                    # Handle removed properties (cleanup sold/unavailable ones)
                    removed_properties = self.db.remove_sold_properties(hours=24)
                    if removed_properties:
                        stats['removed_properties'] = removed_properties
                        self.logger.info(f"🗑️ Removed {len(removed_properties)} sold/unavailable properties")
                    
                    self.logger.info(f"✅ Successfully processed {len(formatted_properties)} properties")
                    self.logger.info(f"📊 Stats: {stats['new']} new, {stats['updated']} updated")
                    if stats.get('price_changes'):
                        self.logger.info(f"💰 Price changes: {len(stats['price_changes'])}")
                    if stats.get('removed_properties'):
                        self.logger.info(f"🗑️ Removed: {len(stats['removed_properties'])}")
                    
                    return True, stats, None
                else:
                    error_message = "No properties found in API response"
                    self.logger.warning(error_message)
                    
                    self.db.log_monitoring_run(
                        properties_found=0,
                        new_properties=0,
                        success=False,
                        error_message=error_message
                    )
                    
                    return False, {'new': 0, 'updated': 0, 'total': 0}, error_message
            
        except requests.exceptions.RequestException as e:
            if "403" in str(e):
                error_message = f"Blocked by Yad2 anti-bot (403). Will retry later with different approach."
            elif "429" in str(e):
                error_message = f"Rate limited (429). Reduce monitoring frequency."
            else:
                error_message = f"API request failed: {e}"
            self.logger.error(error_message)
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse JSON response: {e}"
            self.logger.error(error_message)
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            self.logger.error(error_message)
        
        # Log failed run
        self.db.log_monitoring_run(
            properties_found=0,
            new_properties=0,
            success=False,
            error_message=error_message
        )
        
        return False, {'new': 0, 'updated': 0, 'total': 0}, error_message
    
    def get_new_properties_for_notification(self) -> List[Dict[str, Any]]:
        """Get new properties that need notification."""
        return self.db.get_new_properties_for_notification()
    
    def mark_properties_notified(self, property_ids: List[str]):
        """Mark properties as notified."""
        self.db.mark_properties_as_notified(property_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return self.db.get_property_statistics()
    
    def cleanup_old_data(self):
        """Clean up old properties."""
        cleanup_days = self.monitoring_config.get('cleanup_old_properties_days', 30)
        return self.db.cleanup_old_properties(cleanup_days)
    
    def get_next_check_interval(self) -> float:
        """Get randomized next check interval in minutes."""
        interval_config = self.monitoring_config.get('check_interval_minutes', 10)
        
        if isinstance(interval_config, dict):
            min_interval = interval_config.get('min', 7)
            max_interval = interval_config.get('max', 13)
            next_interval = random.uniform(min_interval, max_interval)
        else:
            # Fallback to fixed interval with small random variation
            base = float(interval_config)
            next_interval = random.uniform(base * 0.8, base * 1.2)
        
        self.logger.info(f"⏰ Next check in {next_interval:.1f} minutes")
        return next_interval

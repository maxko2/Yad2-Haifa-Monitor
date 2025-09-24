#!/usr/bin/env python3
"""
Smart Yad2 Monitor - Database-Driven with Anti-Detection

Efficient apartment monitoring that:
- Uses SQLite database (no 24/7 running needed)
- Randomized check intervals (7-13 minutes) to avoid blocks  
- Rotates user agents and headers
- Only sends notifications for truly NEW properties
- Can run as scheduled task, not continuously
"""

import sys
import time
import schedule
import signal
import logging
import random
from datetime import datetime, timedelta
from typing import Optional

from config_manager import ConfigManager
from smart_yad2_sampler import SmartYad2APISampler
from yad2_notification_manager import Yad2NotificationManager
from logger_setup import setup_logging, APIMonitorLogger

class SmartYad2Monitor:
    """Database-driven Yad2 monitor with smart scheduling."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_manager = None
        self.api_sampler = None
        self.notification_manager = None
        self.running = False
        self.logger = None
        self.next_check_time = None
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self) -> bool:
        """Initialize the smart monitoring service."""
        try:
            self.config_manager = ConfigManager(self.config_file)
            
            # Set up logging
            logging_config = self.config_manager.get_logging_config()
            setup_logging(logging_config)
            self.logger = logging.getLogger(__name__)
            
            # Startup banner
            self._log_startup_banner()
            
            # Initialize components
            self.api_sampler = SmartYad2APISampler(self.config_manager)
            self.notification_manager = Yad2NotificationManager(self.config_manager)
            
            # Log configuration
            self._log_configuration_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Smart Yad2 Monitor: {e}")
            if self.logger:
                self.logger.error(f"Initialization failed: {e}")
            return False
    
    def _log_startup_banner(self):
        """Log startup banner."""
        self.logger.info("🔥" * 20)
        self.logger.info("🏠 SMART YAD2 MONITOR - STARTING 🏠")
        self.logger.info("✨ Database-Driven | Anti-Detection | Smart Scheduling")
        self.logger.info("🔥" * 20)
    
    def _log_configuration_summary(self):
        """Log configuration summary."""
        try:
            interval_config = self.config_manager.get('monitoring.check_interval_minutes', {})
            if isinstance(interval_config, dict):
                min_int = interval_config.get('min', 7)
                max_int = interval_config.get('max', 13)
                interval_text = f"{min_int}-{max_int} min (randomized)"
            else:
                interval_text = f"{interval_config} min (fixed)"
            
            self.logger.info(f"⏰ Check Interval: {interval_text}")
            self.logger.info(f"🛡️  Anti-Detection: User-Agent rotation, random delays")
            self.logger.info(f"💾 Database: SQLite with smart change tracking")
            self.logger.info(f"📧 Email: {'✅ Enabled' if self.config_manager.is_email_enabled() else '❌ Disabled'}")
            self.logger.info(f"📱 SMS: {'✅ Enabled' if self.config_manager.is_sms_enabled() else '❌ Disabled'}")
        except Exception as e:
            self.logger.error(f"Error logging configuration: {e}")
    
    def perform_smart_check(self) -> bool:
        """Perform a single smart property check."""
        try:
            self.logger.info("🔍 Starting smart property check...")
            
            # Fetch and store properties
            success, stats, error = self.api_sampler.fetch_and_store_properties()
            
            if success:
                self.logger.info(f"📊 Properties processed: {stats['total']} total, {stats['new']} new, {stats['updated']} updated")
                
                # Handle new properties
                new_properties = self.api_sampler.get_new_properties_for_notification()
                
                if new_properties:
                    self.logger.info(f"🚨 Found {len(new_properties)} NEW properties for notification!")
                    
                    # Send notifications
                    notification_results = self.notification_manager.send_yad2_notification(new_properties)
                    
                    # Log notification results
                    for notification_type, result in notification_results.items():
                        status = "✅" if result else "❌"
                        self.logger.info(f"   {status} {notification_type.upper()}")
                    
                    # Mark as notified
                    property_ids = [prop['id'] for prop in new_properties]
                    self.api_sampler.mark_properties_notified(property_ids)
                    
                    self.logger.info(f"🎉 Notifications sent for {len(new_properties)} properties!")
                else:
                    self.logger.info("😴 No new properties found - all good!")
                
                # Handle price changes
                price_changes = stats.get('price_changes', [])
                if price_changes:
                    self.logger.info(f"💰 Found {len(price_changes)} price changes!")
                    
                    # Send price change notifications
                    price_notification_results = self.notification_manager.send_price_change_notification(price_changes)
                    
                    # Log price notification results
                    for notification_type, result in price_notification_results.items():
                        if result:
                            status = "✅" if result else "❌"
                            self.logger.info(f"   {status} PRICE CHANGE {notification_type.upper()}")
                
                # Handle removed properties
                removed_properties = stats.get('removed_properties', [])
                if removed_properties:
                    self.logger.info(f"🗑️ {len(removed_properties)} properties removed from market")
                    
                    # Send removal notifications (if significant number)
                    removal_notification_results = self.notification_manager.send_removed_properties_notification(removed_properties)
                    
                    # Log removal notification results
                    for notification_type, result in removal_notification_results.items():
                        if result:
                            status = "✅" if result else "❌"
                            self.logger.info(f"   {status} MARKET UPDATE {notification_type.upper()}")
                
                return True
            else:
                self.logger.error(f"❌ Property check failed: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error during smart check: {e}")
            return False
    
    def run_continuous_smart(self):
        """Run with smart randomized scheduling."""
        if not self.initialize():
            sys.exit(1)
        
        self.logger.info("🚀 Starting continuous smart monitoring...")
        self.logger.info("💡 Using randomized intervals to avoid detection")
        
        # Perform initial check
        self.perform_smart_check()
        
        # Schedule next check with randomized interval
        self._schedule_next_check()
        
        # Main monitoring loop
        self.running = True
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            self.logger.info("⌨️  Keyboard interrupt received")
        finally:
            self._shutdown()
    
    def _schedule_next_check(self):
        """Schedule the next check with randomized interval."""
        try:
            # Clear any existing scheduled jobs
            schedule.clear()
            
            # Get randomized interval
            next_interval = self.api_sampler.get_next_check_interval()
            
            # Schedule next check
            schedule.every(next_interval).minutes.do(self._perform_check_and_reschedule)
            
            # Calculate next check time
            self.next_check_time = datetime.now() + timedelta(minutes=next_interval)
            self.logger.info(f"📅 Next check scheduled for: {self.next_check_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling next check: {e}")
    
    def _perform_check_and_reschedule(self):
        """Perform check and automatically schedule the next one."""
        # Perform the check
        self.perform_smart_check()
        
        # Schedule the next check with new random interval
        self._schedule_next_check()
        
        # Optional: cleanup old data occasionally (5% chance)
        if random.random() < 0.05:
            try:
                cleaned = self.api_sampler.cleanup_old_data()
                if cleaned > 0:
                    self.logger.info(f"🧹 Cleaned up {cleaned} old properties")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
    
    def run_single_check(self):
        """Run a single property check (good for cron jobs)."""
        if not self.initialize():
            sys.exit(1)
        
        self.logger.info("🎯 Performing single property check...")
        success = self.perform_smart_check()
        
        if success:
            self.logger.info("✅ Single check completed successfully")
        else:
            self.logger.error("❌ Single check failed")
        
        self._shutdown()
        return success
    
    def show_statistics(self):
        """Show monitoring statistics."""
        if not self.initialize():
            sys.exit(1)
        
        self.logger.info("📊 YALD2 MONITORING STATISTICS")
        self.logger.info("=" * 40)
        
        try:
            stats = self.api_sampler.get_statistics()
            
            self.logger.info(f"🏠 Total Properties Tracked: {stats['total_properties']}")
            self.logger.info(f"📈 Active Properties (24h): {stats['active_properties']}")
            self.logger.info(f"🆕 New Properties Today: {stats['new_today']}")
            self.logger.info(f"🔄 Monitoring Runs Today: {stats['runs_today']}")
            self.logger.info(f"📊 Avg Properties/Run: {stats['avg_properties_per_run']}")
            self.logger.info(f"✅ Success Rate: {stats['success_rate']}%")
            
            # Show recent properties
            recent = self.api_sampler.db.get_recent_properties(5)
            if recent:
                self.logger.info("\n🕐 Recent Properties:")
                for prop in recent:
                    price = f"₪{prop['price']:,}" if prop['price'] else "N/A"
                    self.logger.info(f"   • {price} - {prop['address']} ({prop['rooms']} rooms)")
            
        except Exception as e:
            self.logger.error(f"Error showing statistics: {e}")
        
        self._shutdown()
    
    def test_system(self):
        """Test all system components."""
        if not self.initialize():
            sys.exit(1)
        
        self.logger.info("🧪 TESTING SMART YAD2 MONITOR SYSTEM")
        self.logger.info("=" * 45)
        
        # Test 1: API Connection
        self.logger.info("1️⃣ Testing API connection...")
        success, stats, error = self.api_sampler.fetch_and_store_properties()
        if success:
            self.logger.info(f"   ✅ API works! Found {stats['total']} properties")
        else:
            self.logger.error(f"   ❌ API failed: {error}")
        
        # Test 2: Database
        self.logger.info("2️⃣ Testing database...")
        try:
            db_stats = self.api_sampler.get_statistics()
            self.logger.info(f"   ✅ Database works! {db_stats['total_properties']} properties stored")
        except Exception as e:
            self.logger.error(f"   ❌ Database error: {e}")
        
        # Test 3: Notifications
        self.logger.info("3️⃣ Testing notifications...")
        test_properties = [{
            'id': 'test-smart-123',
            'price': 4200,
            'address': 'Smart Test Street 1, Haifa',
            'rooms': 3,
            'size_sqm': 75,
            'floor': '2',
            'property_type': 'דירה',
            'condition': 'משופץ',
            'url': 'https://www.yad2.co.il/realestate/rent/test-smart-123'
        }]
        
        results = self.notification_manager.send_yad2_notification(test_properties)
        for notification_type, success in results.items():
            status = "✅" if success else "❌"
            self.logger.info(f"   {status} {notification_type.upper()}")
        
        self.logger.info("🎉 System test completed!")
        self._shutdown()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        if self.logger:
            self.logger.info(f"📡 Signal {signum} received, shutting down...")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown."""
        if self.logger:
            self.logger.info("🔥" * 20)
            self.logger.info("🏠 SMART YAD2 MONITOR - SHUTDOWN")
            self.logger.info("👋 Thank you for using Smart Monitor!")
            self.logger.info("🔥" * 20)
        else:
            print("🏠 Smart Yad2 Monitor shutting down...")

def main():
    """Main entry point with enhanced options."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🏠 Smart Yad2 Monitor - Database-driven with anti-detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Smart Features:
  • Database storage (SQLite)
  • Randomized intervals (7-13 min)
  • User-Agent rotation
  • Smart change detection
  
🏠 Examples:
  python smart_yad2_main.py                # Smart continuous monitoring
  python smart_yad2_main.py --once        # Single check (for cron)
  python smart_yad2_main.py --test        # Test all systems
  python smart_yad2_main.py --stats       # Show statistics
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run single check (perfect for cron jobs)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test all system components'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show monitoring statistics'
    )
    
    args = parser.parse_args()
    
    # Create smart monitor
    monitor = SmartYad2Monitor(args.config)
    
    # Route to appropriate function
    if args.test:
        monitor.test_system()
    elif args.stats:
        monitor.show_statistics()
    elif args.once:
        success = monitor.run_single_check()
        sys.exit(0 if success else 1)
    else:
        monitor.run_continuous_smart()

if __name__ == "__main__":
    main()

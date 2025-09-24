#!/usr/bin/env python3
"""
GitHub Actions compatible version of Smart Yad2 Monitor.
Uses environment variables for configuration.
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from github_config import GitHubConfig
from smart_yad2_sampler import SmartYad2APISampler
from yad2_notification_manager import Yad2NotificationManager

def setup_github_logging():
    """Setup logging for GitHub Actions."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def main():
    """Main function for GitHub Actions."""
    logger = setup_github_logging()
    
    logger.info("🔥 Starting Smart Yad2 Monitor on GitHub Actions")
    logger.info("📍 Monitoring: Haifa and surrounding areas")
    logger.info("💰 Budget: Up to ₪5,000/month")
    logger.info("🏠 Rooms: 2.5 - 5 rooms")
    
    try:
        # Initialize with GitHub config
        config = GitHubConfig()
        
        # Verify email configuration
        if not config.is_email_enabled():
            logger.error("❌ Email not configured! Check GitHub secrets:")
            logger.error("   - PROTON_EMAIL")
            logger.error("   - PROTON_PASSWORD") 
            logger.error("   - RECIPIENT_EMAILS")
            sys.exit(1)
        
        logger.info("✅ Email configuration verified")
        
        # Initialize components
        sampler = SmartYad2APISampler(config)
        notifier = Yad2NotificationManager(config)
        
        # Perform single check
        logger.info("🔍 Starting property check...")
        success, stats, error = sampler.fetch_and_store_properties()
        
        if success:
            logger.info(f"📊 Properties: {stats['total']} total, {stats['new']} new, {stats['updated']} updated")
            
            # Handle new properties
            new_properties = sampler.get_new_properties_for_notification()
            if new_properties:
                logger.info(f"🚨 Found {len(new_properties)} NEW properties!")
                
                # Send notifications
                results = notifier.send_yad2_notification(new_properties)
                
                if results.get('email'):
                    logger.info("✅ Email notification sent successfully")
                else:
                    logger.error("❌ Failed to send email notification")
                
                # Mark as notified
                property_ids = [prop['id'] for prop in new_properties]
                sampler.mark_properties_notified(property_ids)
                
            else:
                logger.info("😴 No new properties - all good!")
            
            # Handle price changes
            price_changes = stats.get('price_changes', [])
            if price_changes:
                logger.info(f"💰 Found {len(price_changes)} price changes")
                results = notifier.send_price_change_notification(price_changes)
                if results.get('email'):
                    logger.info("✅ Price change notification sent")
            
            # Handle removed properties  
            removed_properties = stats.get('removed_properties', [])
            if removed_properties:
                logger.info(f"🗑️ {len(removed_properties)} properties removed from market")
                results = notifier.send_removed_properties_notification(removed_properties)
                if results.get('email'):
                    logger.info("✅ Market update notification sent")
            
            logger.info("🎉 Monitoring completed successfully!")
            
        else:
            logger.error(f"❌ Monitoring failed: {error}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

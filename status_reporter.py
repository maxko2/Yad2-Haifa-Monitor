import logging
import os
from datetime import datetime
from yad2_database import Yad2Database
from yad2_notification_manager import send_property_notifications

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_status_report():
    """Send a status report about the monitoring system."""
    try:
        db = Yad2Database()
        stats = db.get_property_count()
        
        # Get recent activity
        new_24h = db.get_new_properties(hours=24)
        changes_24h = db.get_price_changes(hours=24)
        
        # Email recipients
        recipients = [
            os.getenv('EMAIL_RECIPIENT_1', 'maxkobzer@gmail.com'),
            os.getenv('EMAIL_RECIPIENT_2', 'yaelbrgr2@gmail.com')
        ]
        
        # Send status if we have any activity
        if new_24h or changes_24h or stats['active'] > 0:
            logger.info(f"Sending status report: {len(new_24h)} new, {len(changes_24h)} changes")
            
            send_property_notifications(
                new_properties=new_24h,
                price_changes=changes_24h,
                recipients=recipients
            )
            
            logger.info("Status report sent successfully")
        else:
            logger.info("No activity to report")
            
    except Exception as e:
        logger.error(f"Error sending status report: {e}")

if __name__ == "__main__":
    send_status_report()

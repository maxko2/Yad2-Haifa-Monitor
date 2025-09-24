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
        
        # Email recipients from environment variables
        recipients = [
            os.getenv('EMAIL_RECIPIENT_1'),
            os.getenv('EMAIL_RECIPIENT_2')
        ]
        # Filter out None values
        recipients = [email for email in recipients if email]
        
        # Send status ONLY if we have new activity (not just existing properties)
        if new_24h or changes_24h:
            logger.info(f"📊 Sending status report: {len(new_24h)} new, {len(changes_24h)} changes")
            
            send_property_notifications(
                new_properties=new_24h,
                price_changes=changes_24h,
                recipients=recipients
            )
            
            logger.info("✅ Status report sent successfully")
        else:
            logger.info("📧 No new activity in last 24h - no status report sent")
            
    except Exception as e:
        logger.error(f"Error sending status report: {e}")

if __name__ == "__main__":
    send_status_report()

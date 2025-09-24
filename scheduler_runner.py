"""
Single-run Yad2 monitor for Windows Task Scheduler
Runs once, does the monitoring, then exits - perfect for scheduled tasks
"""

import sys
import os
import logging
from datetime import datetime

# Add the script directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_monitor import AdvancedYad2Monitor

def setup_logging():
    """Setup logging to file with proper error handling."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'yad2_scheduler.log')
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup file handler with error handling
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")
        file_handler = None
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    if file_handler:
        logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """Main function - run once and exit."""
    logger = setup_logging()
    
    try:
        logger.info("🏠 Yad2 Haifa Monitor - Task Scheduler Run")
        logger.info("=" * 50)
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
        
        # Load environment variables from .env file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, '.env')
        
        if os.path.exists(env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                logger.info("✅ Loaded environment variables from .env")
            except ImportError:
                logger.warning("⚠️ python-dotenv not available - using system environment variables")
        else:
            logger.warning(f"⚠️ No .env file found at {env_path}")
            logger.info("Using system environment variables")
        
        # Check if required environment variables are set
        required_vars = ['GMAIL_EMAIL', 'GMAIL_APP_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please check your .env file or system environment variables")
            sys.exit(1)
        
        logger.info(f"✅ Gmail configured for: {os.getenv('GMAIL_EMAIL')}")
        
        # Run the monitoring cycle
        logger.info("🔄 Starting advanced monitoring cycle...")
        monitor = AdvancedYad2Monitor()
        monitor.run_monitoring_cycle()
        
        logger.info("✅ Task Scheduler run completed successfully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Error in Task Scheduler run: {e}")
        logger.exception("Full error details:")
        sys.exit(1)

if __name__ == "__main__":
    main()

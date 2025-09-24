"""
Database population script using your exact filters
Runs multiple cycles to populate database with more properties over time
"""

import time
import logging
from datetime import datetime
from advanced_monitor import AdvancedYad2Monitor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_database_multiple_runs(num_runs=10):
    """
    Populate database by running multiple monitoring cycles
    Uses your exact search filters: maxPrice=5000, rooms=2.5-5, Haifa area
    """
    
    logger.info("🏠 Starting Database Population with Your Exact Filters")
    logger.info("=" * 60)
    logger.info(f"📋 Filters: Max ₪5,000, 2.5-5 rooms, Haifa area")
    logger.info(f"🔄 Running {num_runs} cycles to populate database")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    total_new = 0
    total_updates = 0
    all_unique_properties = set()
    
    monitor = AdvancedYad2Monitor()
    
    for run in range(1, num_runs + 1):
        try:
            logger.info(f"🔄 Starting run {run}/{num_runs}")
            
            # Get initial stats
            initial_stats = monitor.db.get_property_count()
            
            # Run monitoring cycle (this gets ~20 properties per run)
            monitor.run_monitoring_cycle()
            
            # Get final stats
            final_stats = monitor.db.get_property_count()
            
            # Calculate what was added this run
            run_new = final_stats['active'] - initial_stats['active']
            total_new += run_new
            
            logger.info(f"✅ Run {run} completed: {run_new} new properties")
            logger.info(f"📊 Database now has: {final_stats['active']} active properties")
            
            # Wait between runs (important to avoid CAPTCHA)
            if run < num_runs:
                delay = 30  # 30 second delay between runs
                logger.info(f"⏳ Waiting {delay}s before next run...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"❌ Error in run {run}: {e}")
            # Continue with next run
            time.sleep(60)  # Longer delay on error
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    final_stats = monitor.db.get_property_count()
    
    logger.info("=" * 60)
    logger.info("🎉 DATABASE POPULATION COMPLETED!")
    logger.info(f"⏱️  Total time: {duration/60:.1f} minutes")
    logger.info(f"🔄 Runs completed: {num_runs}")
    logger.info(f"✨ Total new properties: {total_new}")
    logger.info(f"📊 Final database: {final_stats['active']} active, {final_stats['total']} total")
    logger.info("=" * 60)
    logger.info("🎯 Database is now well-populated! Future monitoring will detect new properties.")

def main():
    """Main entry point"""
    try:
        # Run 10 cycles to get a good baseline (should get ~200 properties)
        populate_database_multiple_runs(num_runs=10)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()

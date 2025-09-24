"""
GitHub-optimized version of the advanced monitor
Uses the baseline database from GitHub and implements artifact persistence
"""

import os
import shutil
from advanced_monitor import AdvancedYad2Monitor

class GitHubAdvancedYad2Monitor(AdvancedYad2Monitor):
    """
    GitHub Actions optimized version with database persistence
    """
    
    def __init__(self):
        # Initialize the baseline database from GitHub if local doesn't exist
        self.setup_github_database()
        super().__init__()
    
    def setup_github_database(self):
        """Setup database with GitHub baseline data"""
        local_db = 'yad2_properties.db'
        github_baseline = 'github_yad2_properties.db'
        
        # If no local database exists but GitHub baseline does, use it
        if not os.path.exists(local_db) and os.path.exists(github_baseline):
            print(f"🔄 Initializing from GitHub baseline database...")
            shutil.copy2(github_baseline, local_db)
            print(f"✅ Database initialized with baseline data")
        elif os.path.exists(local_db):
            print(f"📊 Using existing local database")
        else:
            print(f"🆕 No database found - will create new one")

def main():
    """GitHub Actions entry point"""
    try:
        print("🏠 Starting GitHub Advanced Yad2 Monitor...")
        print("=" * 50)
        
        monitor = GitHubAdvancedYad2Monitor()
        monitor.run_monitoring_cycle()
        
        print("✅ GitHub monitoring cycle completed successfully")
        
    except Exception as e:
        print(f"⚠️ GitHub monitor completed with issues: {e}")
        # Don't raise - let GitHub Actions continue
        
if __name__ == "__main__":
    main()

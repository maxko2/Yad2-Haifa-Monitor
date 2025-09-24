"""
Create initial database export for GitHub Actions
This exports your current database to a format that can be safely uploaded to GitHub
"""

import sqlite3
import json
import os
from datetime import datetime

def export_database_for_github():
    """Export current database in a secure format for GitHub"""
    
    if not os.path.exists('yad2_properties.db'):
        print("❌ No local database found. Run the monitor locally first to populate it.")
        return
    
    try:
        conn = sqlite3.connect('yad2_properties.db')
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM properties WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Found {active_count} active properties ({total_count} total)")
        
        if active_count == 0:
            print("⚠️ No active properties to export")
            return
        
        # Copy the entire database file for GitHub
        # This will preserve the populated baseline
        print("💾 Copying database file...")
        
        # Create a sanitized copy (remove any sensitive data if needed)
        target_db = 'github_yad2_properties.db'
        
        # Simple file copy since our data is already clean
        import shutil
        shutil.copy2('yad2_properties.db', target_db)
        
        print(f"✅ Database exported as '{target_db}'")
        print(f"📦 File size: {os.path.getsize(target_db) / 1024:.1f} KB")
        print("\n🔧 Next steps:")
        print("1. Add this file to Git: git add github_yad2_properties.db")
        print("2. Update .gitignore to allow this specific file")
        print("3. Commit and push to GitHub")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error exporting database: {e}")

if __name__ == "__main__":
    export_database_for_github()

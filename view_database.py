import sqlite3
import json
from datetime import datetime

def view_database():
    """Simple database viewer for Yad2 properties"""
    try:
        conn = sqlite3.connect('yad2_properties.db')
        cursor = conn.cursor()
        
        # Check if database exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("📝 Database is empty - no tables found")
            return
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        print(f"📊 Database Summary:")
        print(f"   Total Properties: {total_count}")
        print(f"   Active Properties: {active_count}")
        
        if total_count == 0:
            print("📝 No properties found - database is empty")
            return
        
        # Show recent properties
        cursor.execute("""
            SELECT id, yad2_id, title, price, rooms, address, first_seen, is_active
            FROM properties 
            ORDER BY first_seen DESC 
            LIMIT 10
        """)
        
        properties = cursor.fetchall()
        
        print(f"\n🏠 Recent Properties (Last 10):")
        print("=" * 80)
        
        for i, prop in enumerate(properties, 1):
            prop_id, yad2_id, title, price, rooms, address, first_seen, is_active = prop
            status = "🟢" if is_active else "🔴"
            
            print(f"{i}. {status} {title}")
            print(f"   💰 ₪{price:,} | 🏠 {rooms} rooms")
            print(f"   📍 {address}")
            print(f"   📅 {first_seen}")
            print()
        
        # Show price changes if any
        cursor.execute("SELECT COUNT(*) FROM price_changes")
        changes_count = cursor.fetchone()[0]
        
        if changes_count > 0:
            print(f"💰 Price Changes: {changes_count}")
            
            cursor.execute("""
                SELECT p.title, pc.old_price, pc.new_price, pc.change_date
                FROM price_changes pc
                JOIN properties p ON pc.property_id = p.id
                ORDER BY pc.change_date DESC
                LIMIT 5
            """)
            
            changes = cursor.fetchall()
            for change in changes:
                title, old_price, new_price, change_date = change
                direction = "📈" if new_price > old_price else "📉"
                print(f"   {direction} {title[:40]}...")
                print(f"      ₪{old_price:,} → ₪{new_price:,} ({change_date})")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except FileNotFoundError:
        print("📝 Database file not found - run the monitor first to create it")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🏠 Yad2 Property Database Viewer")
    print("=" * 40)
    view_database()
    print("\n" + "=" * 40)
    input("Press Enter to close...")

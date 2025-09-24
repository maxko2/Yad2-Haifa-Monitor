import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import hashlib

class Yad2Database:
    """Clean SQLite database handler for Yad2 property monitoring."""
    
    def __init__(self, db_path: str = 'yad2_properties.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with necessary tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Properties table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS properties (
                        id TEXT PRIMARY KEY,
                        yad2_id TEXT UNIQUE,
                        title TEXT,
                        price INTEGER,
                        rooms REAL,
                        floor INTEGER,
                        size INTEGER,
                        address TEXT,
                        neighborhood TEXT,
                        contact_name TEXT,
                        phone TEXT,
                        description TEXT,
                        images TEXT,
                        amenities TEXT,
                        first_seen TIMESTAMP,
                        last_seen TIMESTAMP,
                        price_history TEXT,
                        raw_data TEXT,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Price changes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_id TEXT,
                        old_price INTEGER,
                        new_price INTEGER,
                        change_date TIMESTAMP,
                        FOREIGN KEY (property_id) REFERENCES properties (id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def generate_property_id(self, property_data: Dict[str, Any]) -> str:
        """Generate a unique ID for a property based on key characteristics."""
        # Use address and title for unique identification
        key_data = f"{property_data.get('title', '')}{property_data.get('address', '')}{property_data.get('rooms', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def add_or_update_property(self, property_data: Dict[str, Any]) -> Tuple[bool, bool]:
        """Add or update property in database. Returns: (is_new, price_changed)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Generate unique ID
                property_id = self.generate_property_id(property_data)
                yad2_id = str(property_data.get('id', ''))
                
                # Check if property exists
                cursor.execute('SELECT id, price FROM properties WHERE id = ? OR yad2_id = ?', 
                             (property_id, yad2_id))
                existing = cursor.fetchone()
                
                current_price = int(property_data.get('price', 0))
                current_time = datetime.now()
                
                if existing:
                    # Property exists - check for price change
                    existing_id, existing_price = existing
                    price_changed = existing_price != current_price
                    
                    if price_changed:
                        # Record price change
                        cursor.execute('''
                            INSERT INTO price_changes (property_id, old_price, new_price, change_date)
                            VALUES (?, ?, ?, ?)
                        ''', (existing_id, existing_price, current_price, current_time))
                    
                    # Update existing property
                    cursor.execute('''
                        UPDATE properties SET
                            title = ?, price = ?, rooms = ?, floor = ?, size = ?,
                            address = ?, neighborhood = ?, contact_name = ?, phone = ?,
                            description = ?, images = ?, amenities = ?, last_seen = ?,
                            is_active = 1 WHERE id = ?
                    ''', (
                        property_data.get('title', ''),
                        current_price,
                        float(property_data.get('rooms', 0)),
                        int(property_data.get('floor', 0)),
                        int(property_data.get('size', 0)),
                        property_data.get('address', ''),
                        property_data.get('neighborhood', ''),
                        property_data.get('contact_name', ''),
                        property_data.get('phone', ''),
                        property_data.get('description', ''),
                        json.dumps(property_data.get('images', [])),
                        json.dumps(property_data.get('amenities', [])),
                        current_time,
                        existing_id
                    ))
                    
                    conn.commit()
                    return False, price_changed
                
                else:
                    # New property
                    cursor.execute('''
                        INSERT INTO properties (
                            id, yad2_id, title, price, rooms, floor, size,
                            address, neighborhood, contact_name, phone,
                            description, images, amenities, first_seen,
                            last_seen, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        property_id, yad2_id, property_data.get('title', ''),
                        current_price, float(property_data.get('rooms', 0)),
                        int(property_data.get('floor', 0)), int(property_data.get('size', 0)),
                        property_data.get('address', ''), property_data.get('neighborhood', ''),
                        property_data.get('contact_name', ''), property_data.get('phone', ''),
                        property_data.get('description', ''), json.dumps(property_data.get('images', [])),
                        json.dumps(property_data.get('amenities', [])), current_time, current_time, 1
                    ))
                    
                    conn.commit()
                    return True, False
                    
        except Exception as e:
            self.logger.error(f"Error adding/updating property: {e}")
            return False, False
    
    def get_new_properties(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get properties added in the last N hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT * FROM properties 
                    WHERE first_seen >= ? AND is_active = 1
                    ORDER BY first_seen DESC
                ''', (cutoff_time,))
                
                return [self._row_to_dict(cursor, row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting new properties: {e}")
            return []
    
    def get_price_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get properties with price changes in the last N hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT p.*, pc.old_price, pc.new_price, pc.change_date
                    FROM properties p
                    JOIN price_changes pc ON p.id = pc.property_id
                    WHERE pc.change_date >= ? AND p.is_active = 1
                    ORDER BY pc.change_date DESC
                ''', (cutoff_time,))
                
                return [self._row_to_dict(cursor, row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting price changes: {e}")
            return []
    
    def cleanup_old_properties(self, days: int = 14):
        """Mark properties as inactive if not seen for N days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    UPDATE properties SET is_active = 0 
                    WHERE last_seen < ? AND is_active = 1
                ''', (cutoff_time,))
                
                updated_count = cursor.rowcount
                conn.commit()
                
                if updated_count > 0:
                    self.logger.info(f"Marked {updated_count} properties as inactive")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old properties: {e}")
    
    def get_property_count(self) -> Dict[str, int]:
        """Get statistics about properties in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM properties WHERE is_active = 1')
                active_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM properties')
                total_count = cursor.fetchone()[0]
                
                return {
                    'active': active_count,
                    'total': total_count,
                    'recent_price_changes': 0
                }
                
        except Exception as e:
            self.logger.error(f"Error getting property count: {e}")
            return {'active': 0, 'total': 0, 'recent_price_changes': 0}
    
    def _row_to_dict(self, cursor, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))
        
        # Parse JSON fields
        json_fields = ['images', 'amenities']
        for field in json_fields:
            if field in row_dict and row_dict[field]:
                try:
                    row_dict[field] = json.loads(row_dict[field])
                except (json.JSONDecodeError, TypeError):
                    row_dict[field] = []
        
        return row_dict
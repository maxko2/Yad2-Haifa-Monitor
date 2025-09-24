import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class Yad2Database:
    """SQLite database handler for Yad2 property monitoring."""
    
    def __init__(self, db_path: str = "yad2_properties.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Properties table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id TEXT PRIMARY KEY,
                    price INTEGER,
                    address TEXT,
                    rooms REAL,
                    size_sqm INTEGER,
                    floor TEXT,
                    property_type TEXT,
                    condition_text TEXT,
                    url TEXT,
                    image_url TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data TEXT,
                    is_notified BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Monitoring runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    properties_found INTEGER,
                    new_properties INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    api_response_hash TEXT
                )
            ''')
            
            conn.commit()
            self.logger.info("Database tables initialized")
    
    def save_properties(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save properties to database and return statistics.
        
        Args:
            properties: List of formatted property data
            
        Returns:
            Dictionary with counts and lists of changes
        """
        stats = {
            'new': 0, 
            'updated': 0, 
            'total': len(properties),
            'price_changes': [],
            'removed_properties': []
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Get current property IDs from API response
            current_property_ids = {prop.get('id') for prop in properties if prop.get('id')}
            
            # Find properties that are no longer in the API response (removed/sold)
            cursor.execute('SELECT id, address, price FROM properties WHERE last_seen > datetime("now", "-1 day")')
            active_properties = cursor.fetchall()
            
            for prop_id, address, price in active_properties:
                if prop_id not in current_property_ids:
                    # Property no longer exists - mark as removed
                    cursor.execute('UPDATE properties SET last_seen = ? WHERE id = ?', 
                                 (current_time, prop_id))
                    stats['removed_properties'].append({
                        'id': prop_id,
                        'address': address,
                        'price': price,
                        'removed_time': current_time
                    })
            
            for prop in properties:
                prop_id = prop.get('id')
                if not prop_id:
                    continue
                
                # Check if property exists
                cursor.execute('SELECT id, last_seen, price FROM properties WHERE id = ?', (prop_id,))
                existing = cursor.fetchone()
                
                if existing:
                    old_price = existing[2]
                    new_price = prop.get('price')
                    
                    # Check for price changes
                    if old_price and new_price and old_price != new_price:
                        stats['price_changes'].append({
                            'id': prop_id,
                            'address': prop.get('address'),
                            'old_price': old_price,
                            'new_price': new_price,
                            'price_diff': new_price - old_price,
                            'change_time': current_time
                        })
                    
                    # Update existing property
                    cursor.execute('''
                        UPDATE properties 
                        SET price=?, address=?, rooms=?, size_sqm=?, floor=?, 
                            property_type=?, condition_text=?, url=?, image_url=?,
                            last_seen=?, raw_data=?
                        WHERE id=?
                    ''', (
                        prop.get('price'),
                        prop.get('address'),
                        prop.get('rooms'),
                        prop.get('size_sqm'),
                        prop.get('floor'),
                        prop.get('property_type'),
                        prop.get('condition'),
                        prop.get('url'),
                        prop.get('image_url'),
                        current_time,
                        json.dumps(prop),
                        prop_id
                    ))
                    stats['updated'] += 1
                else:
                    # Insert new property
                    cursor.execute('''
                        INSERT INTO properties 
                        (id, price, address, rooms, size_sqm, floor, property_type, 
                         condition_text, url, image_url, first_seen, last_seen, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        prop_id,
                        prop.get('price'),
                        prop.get('address'),
                        prop.get('rooms'),
                        prop.get('size_sqm'),
                        prop.get('floor'),
                        prop.get('property_type'),
                        prop.get('condition'),
                        prop.get('url'),
                        prop.get('image_url'),
                        current_time,
                        current_time,
                        json.dumps(prop)
                    ))
                    stats['new'] += 1
            
            conn.commit()
        
        self.logger.info(f"Database updated: {stats['new']} new, {stats['updated']} updated, "
                        f"{len(stats['price_changes'])} price changes, "
                        f"{len(stats['removed_properties'])} removed")
        return stats
    
    def get_new_properties_for_notification(self) -> List[Dict[str, Any]]:
        """
        Get new properties that haven't been notified yet.
        
        Returns:
            List of new property data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM properties 
                WHERE is_notified = FALSE 
                ORDER BY first_seen DESC
            ''')
            
            rows = cursor.fetchall()
            properties = []
            
            for row in rows:
                prop = dict(row)
                # Parse raw_data back to dict if needed
                if prop['raw_data']:
                    try:
                        raw_data = json.loads(prop['raw_data'])
                        prop.update(raw_data)
                    except:
                        pass
                properties.append(prop)
            
            return properties
    
    def mark_properties_as_notified(self, property_ids: List[str]):
        """Mark properties as notified to avoid duplicate notifications."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for prop_id in property_ids:
                cursor.execute(
                    'UPDATE properties SET is_notified = TRUE WHERE id = ?', 
                    (prop_id,)
                )
            
            conn.commit()
            self.logger.info(f"Marked {len(property_ids)} properties as notified")
    
    def log_monitoring_run(self, properties_found: int, new_properties: int, 
                          success: bool, error_message: str = None, 
                          api_response_hash: str = None):
        """Log a monitoring run for statistics and debugging."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_runs 
                (properties_found, new_properties, success, error_message, api_response_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (properties_found, new_properties, success, error_message, api_response_hash))
            
            conn.commit()
    
    def get_property_statistics(self) -> Dict[str, Any]:
        """Get statistics about monitored properties."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total properties
            cursor.execute('SELECT COUNT(*) FROM properties')
            total_properties = cursor.fetchone()[0]
            
            # Properties seen in last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM properties 
                WHERE last_seen > datetime('now', '-1 day')
            ''')
            active_properties = cursor.fetchone()[0]
            
            # New properties in last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM properties 
                WHERE first_seen > datetime('now', '-1 day')
            ''')
            new_today = cursor.fetchone()[0]
            
            # Monitoring runs in last 24 hours
            cursor.execute('''
                SELECT COUNT(*), AVG(properties_found) FROM monitoring_runs 
                WHERE run_time > datetime('now', '-1 day')
            ''')
            runs_data = cursor.fetchone()
            runs_today = runs_data[0] or 0
            avg_properties = runs_data[1] or 0
            
            # Success rate
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM monitoring_runs 
                WHERE run_time > datetime('now', '-1 day')
            ''')
            success_data = cursor.fetchone()
            success_rate = (success_data[1] / success_data[0] * 100) if success_data[0] > 0 else 0
            
            return {
                'total_properties': total_properties,
                'active_properties': active_properties,
                'new_today': new_today,
                'runs_today': runs_today,
                'avg_properties_per_run': round(avg_properties, 1),
                'success_rate': round(success_rate, 1)
            }
    
    def cleanup_old_properties(self, days: int = 30):
        """Remove properties not seen for specified days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM properties 
                WHERE last_seen < datetime('now', '-{} days')
            '''.format(days))
            
            deleted = cursor.rowcount
            conn.commit()
            
            self.logger.info(f"Cleaned up {deleted} old properties (>{days} days)")
            return deleted
    
    def remove_sold_properties(self, hours: int = 24):
        """Remove properties that haven't been seen in the last X hours (likely sold/removed)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get properties to be removed for logging
            cursor.execute('''
                SELECT id, address, price FROM properties 
                WHERE last_seen < datetime('now', '-{} hours')
            '''.format(hours))
            
            removed_properties = cursor.fetchall()
            
            # Remove them
            cursor.execute('''
                DELETE FROM properties 
                WHERE last_seen < datetime('now', '-{} hours')
            '''.format(hours))
            
            deleted = cursor.rowcount
            conn.commit()
            
            self.logger.info(f"Removed {deleted} sold/unavailable properties (>{hours} hours)")
            return [{'id': p[0], 'address': p[1], 'price': p[2]} for p in removed_properties]
    
    def get_recent_properties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent properties for debugging."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, price, address, rooms, first_seen, last_seen 
                FROM properties 
                ORDER BY last_seen DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]

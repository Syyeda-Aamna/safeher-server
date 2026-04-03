import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from config import DATABASE_NAME

class LocalDB:
    """Local SQLite database for offline data storage"""
    
    def __init__(self):
        self.db_name = DATABASE_NAME
        self.connection = None
    
    def initialize(self):
        """Initialize database and create tables"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.create_tables()
            print("Local database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                jwt_token TEXT,
                settings_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Emergency contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT UNIQUE,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relationship TEXT,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Police stations cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS police_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id TEXT UNIQUE,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pending incidents table (for offline mode)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT 0
            )
        ''')
        
        # Location cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                address TEXT,
                accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # SOS history cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sos_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sos_id TEXT,
                trigger_type TEXT,
                location_json TEXT,
                triggered_at TIMESTAMP,
                resolved_at TIMESTAMP,
                synced BOOLEAN DEFAULT 0
            )
        ''')
        
        self.connection.commit()
        print("Database tables created successfully")
    
    def save_user(self, user_data: Dict[str, Any], jwt_token: str):
        """Save user data and JWT token"""
        try:
            cursor = self.connection.cursor()
            
            # Convert settings to JSON
            settings_json = json.dumps(user_data.get('settings', {}))
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', 
                         (user_data.get('id'),))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET name = ?, phone = ?, email = ?, jwt_token = ?, 
                        settings_json = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (
                    user_data.get('full_name'),
                    user_data.get('phone'),
                    user_data.get('email'),
                    jwt_token,
                    settings_json,
                    user_data.get('id')
                ))
            else:
                # Insert new user
                cursor.execute('''
                    INSERT INTO users 
                    (user_id, name, phone, email, jwt_token, settings_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_data.get('id'),
                    user_data.get('full_name'),
                    user_data.get('phone'),
                    user_data.get('email'),
                    jwt_token,
                    settings_json
                ))
            
            self.connection.commit()
            print(f"User saved: {user_data.get('full_name')}")
            
        except Exception as e:
            print(f"Error saving user: {e}")
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get current user data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT user_id, name, phone, email, jwt_token, settings_json
                FROM users 
                ORDER BY updated_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                user_id, name, phone, email, jwt_token, settings_json = row
                
                # Parse settings JSON
                settings = json.loads(settings_json) if settings_json else {}
                
                return {
                    'id': user_id,
                    'full_name': name,
                    'phone': phone,
                    'email': email,
                    'jwt_token': jwt_token,
                    'settings': settings
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def clear_user_data(self):
        """Clear all user data"""
        try:
            cursor = self.connection.cursor()
            
            # Clear all tables
            cursor.execute('DELETE FROM users')
            cursor.execute('DELETE FROM contacts')
            cursor.execute('DELETE FROM pending_incidents')
            cursor.execute('DELETE FROM sos_history')
            
            self.connection.commit()
            print("User data cleared successfully")
            
        except Exception as e:
            print(f"Error clearing user data: {e}")
    
    def save_contact(self, contact_data: Dict[str, Any]) -> bool:
        """Save emergency contact"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO contacts 
                (server_id, user_id, name, phone, relationship, is_primary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                contact_data.get('id'),
                contact_data.get('user_id'),
                contact_data.get('name'),
                contact_data.get('phone'),
                contact_data.get('relationship'),
                contact_data.get('is_primary', False)
            ))
            
            self.connection.commit()
            print(f"Contact saved: {contact_data.get('name')}")
            return True
            
        except Exception as e:
            print(f"Error saving contact: {e}")
            return False
    
    def get_contacts(self) -> List[Dict[str, Any]]:
        """Get all emergency contacts"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT server_id, name, phone, relationship, is_primary
                FROM contacts
                ORDER BY is_primary DESC, created_at ASC
            ''')
            
            contacts = []
            for row in cursor.fetchall():
                server_id, name, phone, relationship, is_primary = row
                contacts.append({
                    'id': server_id,
                    'name': name,
                    'phone': phone,
                    'relationship': relationship,
                    'is_primary': bool(is_primary)
                })
            
            return contacts
            
        except Exception as e:
            print(f"Error getting contacts: {e}")
            return []
    
    def delete_contact(self, contact_id: str) -> bool:
        """Delete emergency contact"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM contacts WHERE server_id = ?', (contact_id,))
            self.connection.commit()
            print(f"Contact deleted: {contact_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting contact: {e}")
            return False
    
    def save_pending_incident(self, incident_data: Dict[str, Any]) -> bool:
        """Save incident for later sync"""
        try:
            cursor = self.connection.cursor()
            incident_json = json.dumps(incident_data)
            
            cursor.execute('''
                INSERT INTO pending_incidents (incident_json)
                VALUES (?)
            ''', (incident_json,))
            
            self.connection.commit()
            print("Pending incident saved for sync")
            return True
            
        except Exception as e:
            print(f"Error saving pending incident: {e}")
            return False
    
    def get_pending_incidents(self) -> List[Dict[str, Any]]:
        """Get all pending incidents for sync"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT id, incident_json FROM pending_incidents WHERE synced = 0')
            
            incidents = []
            for row in cursor.fetchall():
                incident_id, incident_json = row
                incident_data = json.loads(incident_json)
                incident_data['local_id'] = incident_id
                incidents.append(incident_data)
            
            return incidents
            
        except Exception as e:
            print(f"Error getting pending incidents: {e}")
            return []
    
    def mark_incident_synced(self, local_id: int, server_id: str) -> bool:
        """Mark incident as synced"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE pending_incidents 
                SET synced = 1, server_id = ? 
                WHERE id = ?
            ''', (server_id, local_id))
            
            self.connection.commit()
            print(f"Incident marked as synced: {local_id}")
            return True
            
        except Exception as e:
            print(f"Error marking incident synced: {e}")
            return False
    
    def save_location(self, lat: float, lon: float, address: str = None, accuracy: float = None):
        """Save location to cache"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT INTO location_cache (lat, lon, address, accuracy)
                VALUES (?, ?, ?, ?)
            ''', (lat, lon, address, accuracy))
            
            # Keep only last 100 locations
            cursor.execute('''
                DELETE FROM location_cache 
                WHERE id NOT IN (
                    SELECT id FROM location_cache 
                    ORDER BY created_at DESC 
                    LIMIT 100
                )
            ''')
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Error saving location: {e}")
    
    def get_last_location(self) -> Optional[Dict[str, Any]]:
        """Get last known location"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT lat, lon, address, accuracy, created_at
                FROM location_cache
                ORDER BY created_at DESC
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                lat, lon, address, accuracy, created_at = row
                return {
                    'lat': lat,
                    'lon': lon,
                    'address': address,
                    'accuracy': accuracy,
                    'created_at': created_at
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting last location: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

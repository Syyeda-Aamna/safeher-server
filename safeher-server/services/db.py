from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[MongoClient] = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Initialize MongoDB connection"""
        try:
            cls.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test the connection
            cls.client.admin.command('ping')
            
            # Get database
            db_name = settings.MONGO_URI.split('/')[-1].split('?')[0]
            cls.db = cls.client[db_name]
            
            logger.info("Connected to MongoDB successfully")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
    
    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database"""
        if cls.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db[collection_name]
    
    @classmethod
    async def create_index(cls, collection_name: str, index_spec: Dict[str, Any], unique: bool = False):
        """Create an index on a collection"""
        collection = cls.get_collection(collection_name)
        try:
            collection.create_index(list(index_spec.items()), unique=unique)
            logger.info(f"Created index on {collection_name}: {index_spec}")
        except Exception as e:
            logger.error(f"Failed to create index on {collection_name}: {e}")

# Collection names
USERS_COLLECTION = "users"
CONTACTS_COLLECTION = "emergency_contacts"
OTPS_COLLECTION = "otps"
SOS_ALERTS_COLLECTION = "sos_alerts"
CHECKIN_TIMERS_COLLECTION = "checkin_timers"
INCIDENTS_COLLECTION = "incidents"
LOCATION_SHARES_COLLECTION = "location_shares"

async def init_db():
    """Initialize database and create indexes"""
    success = await Database.connect()
    if not success:
        raise RuntimeError("Failed to connect to database")
    
    # Create indexes for better performance and data integrity
    await Database.create_index(USERS_COLLECTION, {"phone": 1}, unique=True)
    await Database.create_index(USERS_COLLECTION, {"email": 1}, unique=True, sparse=True)
    
    await Database.create_index(CONTACTS_COLLECTION, {"user_id": 1})
    await Database.create_index(CONTACTS_COLLECTION, {"user_id": 1, "phone": 1})
    
    await Database.create_index(OTPS_COLLECTION, {"phone": 1})
    await Database.create_index(OTPS_COLLECTION, {"expires_at": 1})
    
    await Database.create_index(SOS_ALERTS_COLLECTION, {"user_id": 1})
    await Database.create_index(SOS_ALERTS_COLLECTION, {"triggered_at": -1})
    await Database.create_index(SOS_ALERTS_COLLECTION, {"is_active": 1})
    
    await Database.create_index(CHECKIN_TIMERS_COLLECTION, {"user_id": 1})
    await Database.create_index(CHECKIN_TIMERS_COLLECTION, {"deadline": 1})
    await Database.create_index(CHECKIN_TIMERS_COLLECTION, {"is_active": 1})
    
    await Database.create_index(INCIDENTS_COLLECTION, {"user_id": 1})
    await Database.create_index(INCIDENTS_COLLECTION, {"created_at": -1})
    
    await Database.create_index(LOCATION_SHARES_COLLECTION, {"token": 1}, unique=True)
    await Database.create_index(LOCATION_SHARES_COLLECTION, {"expires_at": 1})
    await Database.create_index(LOCATION_SHARES_COLLECTION, {"is_active": 1})

# Helper functions for database operations
async def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document into a collection"""
    collection = Database.get_collection(collection_name)
    result = collection.insert_one(document)
    return str(result.inserted_id)

async def find_one(collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find one document in a collection"""
    collection = Database.get_collection(collection_name)
    return collection.find_one(query)

async def find_many(collection_name: str, query: Dict[str, Any], 
                   sort: Optional[List[tuple]] = None, 
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Find multiple documents in a collection"""
    collection = Database.get_collection(collection_name)
    cursor = collection.find(query)
    
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    
    return list(cursor)

async def update_one(collection_name: str, query: Dict[str, Any], 
                    update: Dict[str, Any], upsert: bool = False) -> bool:
    """Update one document in a collection"""
    collection = Database.get_collection(collection_name)
    result = collection.update_one(query, update, upsert=upsert)
    return result.modified_count > 0 or result.upserted_id is not None

async def delete_one(collection_name: str, query: Dict[str, Any]) -> bool:
    """Delete one document from a collection"""
    collection = Database.get_collection(collection_name)
    result = collection.delete_one(query)
    return result.deleted_count > 0

async def count_documents(collection_name: str, query: Dict[str, Any]) -> int:
    """Count documents in a collection"""
    collection = Database.get_collection(collection_name)
    return collection.count_documents(query)

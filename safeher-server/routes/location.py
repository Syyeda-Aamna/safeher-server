from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.location import LocationUpdate, LocationShareCreate, LocationShareResponse, LiveLocationResponse
from services.db import find_one, insert_one, update_one, delete_one, find_many
from services.jwt_service import JWTService
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user ID"""
    token = credentials.credentials
    payload = JWTService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user_id

@router.post("/update")
async def update_location(location_data: LocationUpdate, user_id: str = Depends(get_current_user_id)):
    """Update user's current location"""
    try:
        # Prepare location data
        location_update = {
            "lat": location_data.lat,
            "lon": location_data.lon,
            "address": location_data.address,
            "accuracy": location_data.accuracy,
            "updated_at": datetime.utcnow()
        }
        
        # Update user's last location
        success = await update_one(
            "users",
            {"_id": user_id},
            {"$set": {"last_location": location_update}}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update location"
            )
        
        # Update any active location shares
        await update_one(
            "location_shares",
            {"user_id": user_id, "is_active": True},
            {"$set": {"last_location": location_update}}
        )
        
        logger.info(f"Location updated for user {user_id}: {location_data.lat}, {location_data.lon}")
        return {
            "message": "Location updated successfully",
            "location": location_update
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update location"
        )

@router.get("/current")
async def get_current_location(user_id: str = Depends(get_current_user_id)):
    """Get user's current last known location"""
    try:
        user = await find_one("users", {"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        last_location = user.get("last_location")
        if not last_location:
            return {
                "location": None,
                "message": "No location data available"
            }
        
        return {
            "location": last_location,
            "last_updated": last_location.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch current location"
        )

@router.post("/share", response_model=LocationShareResponse)
async def create_location_share(share_data: LocationShareCreate, user_id: str = Depends(get_current_user_id)):
    """Create a shareable live location link"""
    try:
        # Get user's current location
        user = await find_one("users", {"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate unique token
        token = secrets.token_urlsafe(16)
        
        # Calculate expiry
        expires_at = datetime.utcnow() + timedelta(hours=share_data.expires_hours)
        
        # Create location share record
        share_record = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "last_location": user.get("last_location"),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        share_id = await insert_one("location_shares", share_record)
        if not share_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create location share"
            )
        
        # Generate share URL (this would be your frontend URL)
        share_url = f"https://safeher-api.onrender.com/api/location/live/{token}"
        
        logger.info(f"Location share created for user {user_id}: {token}")
        return {
            "id": share_id,
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "last_location": user.get("last_location"),
            "is_active": True,
            "share_url": share_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating location share: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create location share"
        )

@router.get("/shares")
async def get_location_shares(user_id: str = Depends(get_current_user_id)):
    """Get all location shares for the current user"""
    try:
        shares = await find_many(
            "location_shares",
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        share_list = []
        for share in shares:
            share_list.append({
                "id": str(share["_id"]),
                "token": share["token"],
                "expires_at": share["expires_at"],
                "is_active": share["is_active"],
                "created_at": share["created_at"],
                "share_url": f"https://safeher-api.onrender.com/api/location/live/{share['token']}",
                "is_expired": share["expires_at"] < datetime.utcnow()
            })
        
        return {
            "shares": share_list,
            "total_count": len(share_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching location shares: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch location shares"
        )

@router.delete("/shares/{share_id}")
async def delete_location_share(share_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a location share"""
    try:
        # Check if share exists and belongs to user
        share = await find_one("location_shares", {
            "_id": share_id,
            "user_id": user_id
        })
        
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location share not found"
            )
        
        # Delete share
        success = await delete_one("location_shares", {"_id": share_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete location share"
            )
        
        logger.info(f"Location share deleted for user {user_id}: {share_id}")
        return {"message": "Location share deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting location share: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete location share"
        )

@router.get("/live/{token}", response_model=LiveLocationResponse)
async def get_live_location(token: str):
    """Public endpoint to get live location via share token"""
    try:
        # Find active location share
        share = await find_one("location_shares", {
            "token": token,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location share not found or expired"
            )
        
        # Get user details
        user = await find_one("users", {"_id": share["user_id"]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        last_location = share.get("last_location") or user.get("last_location")
        
        return {
            "user_name": user["full_name"],
            "lat": last_location["lat"] if last_location else 0,
            "lon": last_location["lon"] if last_location else 0,
            "address": last_location.get("address") if last_location else None,
            "last_updated": last_location.get("updated_at") if last_location else None,
            "is_active": share["is_active"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching live location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch live location"
        )

@router.post("/cleanup")
async def cleanup_expired_shares():
    """Clean up expired location shares (should be run periodically)"""
    try:
        result = await delete_one("location_shares", {
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        logger.info(f"Cleaned up expired location shares")
        return {
            "message": "Cleanup completed",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired shares: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired shares"
        )

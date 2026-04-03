from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from services.db import find_one, insert_one, update_one, find_many
from services.jwt_service import JWTService
from datetime import datetime, timedelta
import uuid
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

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(incident_data: IncidentCreate, user_id: str = Depends(get_current_user_id)):
    """Create a new incident report"""
    try:
        # Prepare location data
        location_data = {
            "lat": incident_data.lat,
            "lon": incident_data.lon,
            "address": incident_data.address or "Unknown location"
        }
        
        # Create incident record
        incident_record = {
            "user_id": user_id,
            "type": incident_data.type.value,
            "description": incident_data.description,
            "location": location_data,
            "photo_url": incident_data.photo_url,
            "created_at": datetime.utcnow(),
            "synced": False  # Will be synced to authorities if needed
        }
        
        incident_id = await insert_one("incidents", incident_record)
        if not incident_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create incident report"
            )
        
        logger.info(f"Incident created for user {user_id}: {incident_id}")
        return {
            "id": incident_id,
            "user_id": user_id,
            "type": incident_data.type,
            "description": incident_data.description,
            "location": location_data,
            "photo_url": incident_data.photo_url,
            "created_at": incident_record["created_at"],
            "synced": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create incident report"
        )

@router.get("/", response_model=list[IncidentResponse])
async def get_incidents(user_id: str = Depends(get_current_user_id), limit: int = 20):
    """Get all incident reports for the current user"""
    try:
        incidents = await find_many(
            "incidents",
            {"user_id": user_id},
            sort=[("created_at", -1)],
            limit=limit
        )
        
        response_incidents = []
        for incident in incidents:
            response_incidents.append({
                "id": str(incident["_id"]),
                "user_id": incident["user_id"],
                "type": incident["type"],
                "description": incident["description"],
                "location": incident["location"],
                "photo_url": incident.get("photo_url"),
                "created_at": incident["created_at"],
                "synced": incident.get("synced", False)
            })
        
        return response_incidents
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch incidents"
        )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, user_id: str = Depends(get_current_user_id)):
    """Get a specific incident report"""
    try:
        incident = await find_one("incidents", {
            "_id": incident_id,
            "user_id": user_id
        })
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        return {
            "id": str(incident["_id"]),
            "user_id": incident["user_id"],
            "type": incident["type"],
            "description": incident["description"],
            "location": incident["location"],
            "photo_url": incident.get("photo_url"),
            "created_at": incident["created_at"],
            "synced": incident.get("synced", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch incident"
        )

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, incident_data: IncidentUpdate, 
                         user_id: str = Depends(get_current_user_id)):
    """Update an incident report"""
    try:
        # Check if incident exists and belongs to user
        existing_incident = await find_one("incidents", {
            "_id": incident_id,
            "user_id": user_id
        })
        
        if not existing_incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Prepare update data
        update_data = {}
        if incident_data.type is not None:
            update_data["type"] = incident_data.type.value
        if incident_data.description is not None:
            update_data["description"] = incident_data.description
        if incident_data.photo_url is not None:
            update_data["photo_url"] = incident_data.photo_url
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            success = await update_one(
                "incidents",
                {"_id": incident_id},
                {"$set": update_data}
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update incident"
                )
        
        # Get updated incident
        updated_incident = await find_one("incidents", {"_id": incident_id})
        
        logger.info(f"Incident updated for user {user_id}: {incident_id}")
        return {
            "id": str(updated_incident["_id"]),
            "user_id": updated_incident["user_id"],
            "type": updated_incident["type"],
            "description": updated_incident["description"],
            "location": updated_incident["location"],
            "photo_url": updated_incident.get("photo_url"),
            "created_at": updated_incident["created_at"],
            "synced": updated_incident.get("synced", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update incident"
        )

@router.delete("/{incident_id}")
async def delete_incident(incident_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete an incident report"""
    try:
        # Check if incident exists and belongs to user
        incident = await find_one("incidents", {
            "_id": incident_id,
            "user_id": user_id
        })
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Delete incident
        from services.db import delete_one
        success = await delete_one("incidents", {"_id": incident_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete incident"
            )
        
        logger.info(f"Incident deleted for user {user_id}: {incident_id}")
        return {"message": "Incident deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete incident"
        )

@router.post("/{incident_id}/sync")
async def sync_incident(incident_id: str, user_id: str = Depends(get_current_user_id)):
    """Mark incident as synced to authorities"""
    try:
        # Check if incident exists and belongs to user
        incident = await find_one("incidents", {
            "_id": incident_id,
            "user_id": user_id
        })
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Mark as synced
        await update_one(
            "incidents",
            {"_id": incident_id},
            {"$set": {
                "synced": True,
                "synced_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Incident synced for user {user_id}: {incident_id}")
        return {
            "message": "Incident synced successfully",
            "incident_id": incident_id,
            "synced_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync incident"
        )

@router.get("/stats/summary")
async def get_incidents_summary(user_id: str = Depends(get_current_user_id)):
    """Get summary statistics for user's incidents"""
    try:
        # Get all incidents for user
        incidents = await find_many("incidents", {"user_id": user_id})
        
        # Calculate statistics
        total_incidents = len(incidents)
        synced_incidents = sum(1 for inc in incidents if inc.get("synced", False))
        
        # Count by type
        type_counts = {}
        for incident in incidents:
            incident_type = incident["type"]
            type_counts[incident_type] = type_counts.get(incident_type, 0) + 1
        
        # Recent incidents (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_incidents = sum(1 for inc in incidents 
                             if inc["created_at"] > thirty_days_ago)
        
        return {
            "total_incidents": total_incidents,
            "synced_incidents": synced_incidents,
            "recent_incidents": recent_incidents,
            "incidents_by_type": type_counts,
            "last_incident_date": incidents[0]["created_at"] if incidents else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching incident summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch incident summary"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.sos import SOSCreate, SOSCancel, SOSResponse, SMSResult
from services.db import find_one, insert_one, update_one, find_many, count_documents
from services.jwt_service import JWTService
from services.sms_service import SMSService
from datetime import datetime
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

@router.post("/trigger", response_model=SOSResponse, status_code=status.HTTP_201_CREATED)
async def trigger_sos(sos_data: SOSCreate, user_id: str = Depends(get_current_user_id)):
    """Trigger SOS alert to all emergency contacts"""
    try:
        # Check if there's already an active SOS
        active_sos = await find_one("sos_alerts", {
            "user_id": user_id,
            "is_active": True
        })
        
        if active_sos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An active SOS alert already exists"
            )
        
        # Get user's emergency contacts
        contacts = await find_many(
            "emergency_contacts",
            {"user_id": user_id},
            sort=[("is_primary", -1), ("created_at", 1)]
        )
        
        if not contacts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No emergency contacts found. Please add contacts first."
            )
        
        # Get user details
        user = await find_one("users", {"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare location data
        location_data = {
            "lat": sos_data.lat,
            "lon": sos_data.lon,
            "address": sos_data.address or "Unknown location"
        }
        
        # Create SOS record
        sos_record = {
            "user_id": user_id,
            "trigger_type": sos_data.trigger_type.value,
            "location": location_data,
            "contacts_notified": [contact["phone"] for contact in contacts],
            "sms_results": [],
            "is_active": True,
            "triggered_at": datetime.utcnow()
        }
        
        sos_id = await insert_one("sos_alerts", sos_record)
        if not sos_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create SOS alert"
            )
        
        # Send SMS to all contacts
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        sms_results = await SMSService.send_sos_to_contacts(
            contacts,
            user["full_name"],
            sos_data.lat,
            sos_data.lon,
            sos_data.address,
            current_time
        )
        
        # Update SOS record with SMS results
        formatted_sms_results = []
        for result in sms_results:
            formatted_sms_results.append({
                "phone": result["phone"],
                "status": result["status"],
                "sent_at": datetime.utcnow(),
                "error_message": result.get("error")
            })
        
        await update_one(
            "sos_alerts",
            {"_id": sos_id},
            {"$set": {"sms_results": formatted_sms_results}}
        )
        
        logger.info(f"SOS triggered for user {user_id}: {sos_id}")
        
        return {
            "id": sos_id,
            "user_id": user_id,
            "trigger_type": sos_data.trigger_type,
            "location": location_data,
            "contacts_notified": [contact["phone"] for contact in contacts],
            "sms_results": formatted_sms_results,
            "is_active": True,
            "triggered_at": sos_record["triggered_at"],
            "resolved_at": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering SOS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger SOS alert"
        )

@router.post("/cancel")
async def cancel_sos(cancel_data: SOSCancel, user_id: str = Depends(get_current_user_id)):
    """Cancel active SOS alert"""
    try:
        # Find active SOS
        active_sos = await find_one("sos_alerts", {
            "user_id": user_id,
            "is_active": True
        })
        
        if not active_sos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active SOS alert found"
            )
        
        # Mark SOS as resolved
        await update_one(
            "sos_alerts",
            {"_id": active_sos["_id"]},
            {"$set": {
                "is_active": False,
                "resolved_at": datetime.utcnow(),
                "resolution_reason": cancel_data.reason or "User cancelled"
            }}
        )
        
        logger.info(f"SOS cancelled for user {user_id}: {active_sos['_id']}")
        return {
            "message": "SOS alert cancelled successfully",
            "sos_id": str(active_sos["_id"]),
            "cancelled_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling SOS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel SOS alert"
        )

@router.get("/status")
async def get_sos_status(user_id: str = Depends(get_current_user_id)):
    """Get current SOS status"""
    try:
        active_sos = await find_one("sos_alerts", {
            "user_id": user_id,
            "is_active": True
        })
        
        if not active_sos:
            return {
                "active_sos": False,
                "message": "No active SOS alerts"
            }
        
        return {
            "active_sos": True,
            "sos": {
                "id": str(active_sos["_id"]),
                "trigger_type": active_sos["trigger_type"],
                "location": active_sos["location"],
                "contacts_notified": active_sos["contacts_notified"],
                "triggered_at": active_sos["triggered_at"],
                "seconds_ago": int((datetime.utcnow() - active_sos["triggered_at"]).total_seconds())
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching SOS status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch SOS status"
        )

@router.get("/history")
async def get_sos_history(user_id: str = Depends(get_current_user_id), limit: int = 10):
    """Get SOS alert history"""
    try:
        sos_alerts = await find_many(
            "sos_alerts",
            {"user_id": user_id},
            sort=[("triggered_at", -1)],
            limit=limit
        )
        
        history = []
        for alert in sos_alerts:
            history.append({
                "id": str(alert["_id"]),
                "trigger_type": alert["trigger_type"],
                "location": alert["location"],
                "contacts_notified": alert["contacts_notified"],
                "is_active": alert["is_active"],
                "triggered_at": alert["triggered_at"],
                "resolved_at": alert.get("resolved_at"),
                "duration_minutes": None
            })
            
            # Calculate duration if resolved
            if alert.get("resolved_at"):
                duration = alert["resolved_at"] - alert["triggered_at"]
                history[-1]["duration_minutes"] = int(duration.total_seconds() / 60)
        
        return {
            "history": history,
            "total_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching SOS history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch SOS history"
        )

@router.get("/active/count")
async def get_active_sos_count():
    """Get count of active SOS alerts (for monitoring)"""
    try:
        count = await count_documents("sos_alerts", {"is_active": True})
        return {
            "active_sos_count": count,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error counting active SOS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count active SOS alerts"
        )

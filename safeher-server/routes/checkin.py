from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.checkin import CheckinStart, CheckinResponse, CheckinSafe, TimerStatus
from services.db import find_one, insert_one, update_one, delete_one, find_many
from services.jwt_service import JWTService
from services.sms_service import SMSService
from datetime import datetime, timedelta
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

@router.post("/start", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def start_checkin_timer(checkin_data: CheckinStart, user_id: str = Depends(get_current_user_id)):
    """Start a check-in timer"""
    try:
        # Check if there's already an active timer
        active_timer = await find_one("checkin_timers", {
            "user_id": user_id,
            "is_active": True
        })
        
        if active_timer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An active check-in timer already exists"
            )
        
        # Calculate deadline
        deadline = datetime.utcnow() + timedelta(hours=checkin_data.hours, minutes=checkin_data.minutes)
        
        # Create timer record
        timer_record = {
            "user_id": user_id,
            "deadline": deadline,
            "is_active": True,
            "checked_in": False,
            "created_at": datetime.utcnow(),
            "status": TimerStatus.ACTIVE.value
        }
        
        timer_id = await insert_one("checkin_timers", timer_record)
        if not timer_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create check-in timer"
            )
        
        logger.info(f"Check-in timer started for user {user_id}: {timer_id}")
        return {
            "id": timer_id,
            "user_id": user_id,
            "deadline": deadline,
            "is_active": True,
            "checked_in": False,
            "created_at": timer_record["created_at"],
            "status": TimerStatus.ACTIVE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting check-in timer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start check-in timer"
        )

@router.post("/safe")
async def mark_safe(checkin_data: CheckinSafe, user_id: str = Depends(get_current_user_id)):
    """Mark user as safe and cancel active timer"""
    try:
        # Find active timer
        timer = await find_one("checkin_timers", {
            "_id": checkin_data.timer_id,
            "user_id": user_id,
            "is_active": True
        })
        
        if not timer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active check-in timer not found"
            )
        
        # Mark timer as completed
        await update_one(
            "checkin_timers",
            {"_id": checkin_data.timer_id},
            {"$set": {
                "is_active": False,
                "checked_in": True,
                "status": TimerStatus.COMPLETED.value,
                "completed_at": datetime.utcnow(),
                "completion_message": checkin_data.message
            }}
        )
        
        logger.info(f"Check-in timer marked safe for user {user_id}: {checkin_data.timer_id}")
        return {
            "message": "Check-in timer marked as safe",
            "timer_id": checkin_data.timer_id,
            "completed_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking check-in safe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark check-in as safe"
        )

@router.get("/status")
async def get_checkin_status(user_id: str = Depends(get_current_user_id)):
    """Get current check-in timer status"""
    try:
        active_timer = await find_one("checkin_timers", {
            "user_id": user_id,
            "is_active": True
        })
        
        if not active_timer:
            return {
                "active_timer": False,
                "message": "No active check-in timer"
            }
        
        # Calculate time remaining
        now = datetime.utcnow()
        time_remaining = active_timer["deadline"] - now
        seconds_remaining = max(0, int(time_remaining.total_seconds()))
        
        # Check if timer is overdue
        is_overdue = now > active_timer["deadline"]
        
        return {
            "active_timer": True,
            "timer": {
                "id": str(active_timer["_id"]),
                "deadline": active_timer["deadline"],
                "seconds_remaining": seconds_remaining,
                "is_overdue": is_overdue,
                "created_at": active_timer["created_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching check-in status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch check-in status"
        )

@router.get("/history")
async def get_checkin_history(user_id: str = Depends(get_current_user_id), limit: int = 10):
    """Get check-in timer history"""
    try:
        timers = await find_many(
            "checkin_timers",
            {"user_id": user_id},
            sort=[("created_at", -1)],
            limit=limit
        )
        
        history = []
        for timer in timers:
            history.append({
                "id": str(timer["_id"]),
                "deadline": timer["deadline"],
                "is_active": timer["is_active"],
                "checked_in": timer["checked_in"],
                "status": timer["status"],
                "created_at": timer["created_at"],
                "completed_at": timer.get("completed_at")
            })
        
        return {
            "history": history,
            "total_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching check-in history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch check-in history"
        )

@router.post("/monitor")
async def monitor_missed_checkins():
    """Check for missed check-ins and send alerts (should be run periodically)"""
    try:
        now = datetime.utcnow()
        
        # Find overdue timers that haven't been notified
        overdue_timers = await find_many("checkin_timers", {
            "is_active": True,
            "deadline": {"$lt": now},
            "status": {"$ne": TimerStatus.MISSED.value}
        })
        
        alerts_sent = 0
        
        for timer in overdue_timers:
            # Get user details
            user = await find_one("users", {"_id": timer["user_id"]})
            if not user:
                continue
            
            # Get user's emergency contacts
            contacts = await find_many(
                "emergency_contacts",
                {"user_id": timer["user_id"]},
                sort=[("is_primary", -1), ("created_at", 1)]
            )
            
            if not contacts:
                continue
            
            # Get user's last location
            last_location = user.get("last_location", {})
            lat = last_location.get("lat", 0)
            lon = last_location.get("lon", 0)
            
            # Send alerts to contacts
            deadline_str = timer["deadline"].strftime("%Y-%m-%d %H:%M:%S UTC")
            sms_results = await SMSService.send_bulk_sms(
                [contact["phone"] for contact in contacts],
                f"ALERT: {user['full_name']} has NOT checked in safe by {deadline_str}. Last location: https://maps.google.com/?q={lat},{lon}. Please check on them immediately. - SafeHer App"
            )
            
            # Mark timer as missed
            await update_one(
                "checkin_timers",
                {"_id": timer["_id"]},
                {"$set": {
                    "status": TimerStatus.MISSED.value,
                    "missed_at": now,
                    "alerts_sent": sms_results
                }}
            )
            
            alerts_sent += 1
            logger.info(f"Missed check-in alerts sent for user {timer['user_id']}")
        
        return {
            "message": "Check-in monitoring completed",
            "alerts_sent": alerts_sent,
            "timestamp": now
        }
        
    except Exception as e:
        logger.error(f"Error monitoring missed check-ins: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to monitor missed check-ins"
        )

@router.delete("/cancel/{timer_id}")
async def cancel_timer(timer_id: str, user_id: str = Depends(get_current_user_id)):
    """Cancel an active check-in timer"""
    try:
        # Find active timer
        timer = await find_one("checkin_timers", {
            "_id": timer_id,
            "user_id": user_id,
            "is_active": True
        })
        
        if not timer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active check-in timer not found"
            )
        
        # Cancel timer
        await update_one(
            "checkin_timers",
            {"_id": timer_id},
            {"$set": {
                "is_active": False,
                "status": TimerStatus.PENDING.value,
                "cancelled_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Check-in timer cancelled for user {user_id}: {timer_id}")
        return {
            "message": "Check-in timer cancelled successfully",
            "timer_id": timer_id,
            "cancelled_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling check-in timer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel check-in timer"
        )

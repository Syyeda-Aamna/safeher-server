import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings
from services.db import find_one, insert_one, update_one, delete_one, count_documents
from services.sms_service import SMSService
from models.otp import OTPPurpose
import logging

logger = logging.getLogger(__name__)

class OTPService:
    """OTP generation, hashing, and verification service"""
    
    @staticmethod
    def generate_otp(length: int = None) -> str:
        """Generate a random OTP"""
        if length is None:
            length = settings.OTP_LENGTH
        
        # Generate numeric OTP
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        logger.info(f"Generated OTP: {otp[:2]}****")  # Log only first 2 digits for security
        return otp
    
    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash OTP using bcrypt"""
        try:
            # Generate salt and hash the OTP
            salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(otp.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to hash OTP: {str(e)}")
            raise
    
    @staticmethod
    def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
        """Verify OTP against its hash"""
        try:
            return bcrypt.checkpw(plain_otp.encode('utf-8'), hashed_otp.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to verify OTP: {str(e)}")
            return False
    
    @staticmethod
    async def check_rate_limit(phone: str) -> bool:
        """Check if user has exceeded OTP rate limit"""
        try:
            # Count OTPs sent in the last hour for this phone
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            count = await count_documents("otps", {
                "phone": phone,
                "created_at": {"$gte": one_hour_ago}
            })
            
            return count < settings.MAX_OTP_PER_HOUR
            
        except Exception as e:
            logger.error(f"Failed to check rate limit for {phone}: {str(e)}")
            return False
    
    @staticmethod
    async def send_otp(phone: str, purpose: OTPPurpose = OTPPurpose.REGISTER) -> Dict[str, Any]:
        """Generate, hash, store, and send OTP"""
        try:
            # Check rate limit
            if not await OTPService.check_rate_limit(phone):
                return {
                    "success": False,
                    "message": f"Too many OTP requests. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            
            # Generate OTP
            otp = OTPService.generate_otp()
            otp_hash = OTPService.hash_otp(otp)
            
            # Calculate expiry
            expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
            
            # Store OTP in database
            otp_data = {
                "phone": phone,
                "otp_hash": otp_hash,
                "purpose": purpose.value,
                "expires_at": expires_at,
                "used": False,
                "created_at": datetime.utcnow()
            }
            
            otp_id = await insert_one("otps", otp_data)
            
            if not otp_id:
                return {
                    "success": False,
                    "message": "Failed to store OTP. Please try again.",
                    "error_code": "STORAGE_ERROR"
                }
            
            # Send OTP via SMS
            sms_result = await SMSService.send_otp(phone, otp)
            
            if sms_result["status"] != "success":
                # Delete stored OTP if SMS failed
                await delete_one("otps", {"_id": otp_id})
                return {
                    "success": False,
                    "message": "Failed to send OTP. Please try again.",
                    "error_code": "SMS_FAILED",
                    "sms_error": sms_result.get("error")
                }
            
            logger.info(f"OTP sent successfully to {phone} for purpose {purpose.value}")
            return {
                "success": True,
                "message": "OTP sent successfully",
                "otp_id": otp_id,
                "expires_in": settings.OTP_EXPIRY_MINUTES * 60  # seconds
            }
            
        except Exception as e:
            logger.error(f"Failed to send OTP to {phone}: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred while sending OTP",
                "error_code": "INTERNAL_ERROR"
            }
    
    @staticmethod
    async def verify_otp_request(phone: str, otp: str, purpose: OTPPurpose = OTPPurpose.REGISTER) -> Dict[str, Any]:
        """Verify OTP and mark as used"""
        try:
            # Find the most recent unused OTP for this phone and purpose
            otp_record = await find_one("otps", {
                "phone": phone,
                "purpose": purpose.value,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not otp_record:
                return {
                    "success": False,
                    "message": "Invalid or expired OTP",
                    "error_code": "INVALID_OTP"
                }
            
            # Verify the OTP
            if not OTPService.verify_otp(otp, otp_record["otp_hash"]):
                return {
                    "success": False,
                    "message": "Invalid OTP",
                    "error_code": "INVALID_OTP"
                }
            
            # Mark OTP as used
            await update_one("otps", 
                           {"_id": otp_record["_id"]}, 
                           {"$set": {"used": True, "used_at": datetime.utcnow()}})
            
            logger.info(f"OTP verified successfully for {phone}")
            return {
                "success": True,
                "message": "OTP verified successfully",
                "otp_id": otp_record["_id"]
            }
            
        except Exception as e:
            logger.error(f"Failed to verify OTP for {phone}: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred while verifying OTP",
                "error_code": "INTERNAL_ERROR"
            }
    
    @staticmethod
    async def cleanup_expired_otps():
        """Clean up expired OTPs (should be run periodically)"""
        try:
            result = await delete_one("otps", {
                "expires_at": {"$lt": datetime.utcnow()}
            })
            logger.info(f"Cleaned up expired OTPs")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired OTPs: {str(e)}")

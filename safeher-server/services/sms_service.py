import requests
from typing import Dict, List, Optional
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    """Fast2SMS integration for sending SMS messages"""
    
    @staticmethod
    async def send_sms(phone: str, message: str) -> Dict[str, any]:
        """
        Send SMS using Fast2SMS API
        
        Args:
            phone: 10-digit Indian mobile number (without +91)
            message: Message content (max 160 characters for standard SMS)
            
        Returns:
            Dict with status and response details
        """
        try:
            url = settings.FAST2SMS_BASE_URL
            payload = {
                "route": "q",          # Quick SMS route
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": phone,      # 10-digit Indian number
            }
            headers = {
                "authorization": settings.FAST2SMS_API_KEY,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            response_data = response.json()
            
            logger.info(f"SMS sent to {phone}: {response_data}")
            
            if response_data.get("return") == 1:
                return {
                    "status": "success",
                    "message_id": response_data.get("message", []).pop(0) if response_data.get("message") else None,
                    "response": response_data
                }
            else:
                return {
                    "status": "failed",
                    "error": response_data.get("message", "Unknown error"),
                    "response": response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")
            return {
                "status": "failed",
                "error": f"Network error: {str(e)}",
                "response": None
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone}: {str(e)}")
            return {
                "status": "failed",
                "error": f"Unexpected error: {str(e)}",
                "response": None
            }
    
    @staticmethod
    async def send_otp(phone: str, otp: str) -> Dict[str, any]:
        """Send OTP SMS"""
        message = settings.OTP_MESSAGE_TEMPLATE.format(otp=otp)
        return await SMSService.send_sms(phone, message)
    
    @staticmethod
    async def send_sos_alert(phone: str, user_name: str, lat: float, lon: float, 
                           address: str, time: str) -> Dict[str, any]:
        """Send SOS alert SMS"""
        message = settings.SOS_MESSAGE_TEMPLATE.format(
            user_name=user_name,
            lat=lat,
            lon=lon,
            address=address or "Unknown location",
            time=time
        )
        return await SMSService.send_sms(phone, message)
    
    @staticmethod
    async def send_checkin_missed_alert(phone: str, user_name: str, lat: float, 
                                       lon: float, deadline: str) -> Dict[str, any]:
        """Send check-in missed alert SMS"""
        message = settings.CHECKIN_MISSED_MESSAGE_TEMPLATE.format(
            user_name=user_name,
            lat=lat,
            lon=lon,
            deadline=deadline
        )
        return await SMSService.send_sms(phone, message)
    
    @staticmethod
    async def send_bulk_sms(phones: List[str], message: str) -> List[Dict[str, any]]:
        """Send SMS to multiple phone numbers"""
        results = []
        for phone in phones:
            result = await SMSService.send_sms(phone, message)
            results.append({
                "phone": phone,
                "status": result["status"],
                "error": result.get("error"),
                "message_id": result.get("message_id")
            })
        return results
    
    @staticmethod
    async def send_sos_to_contacts(contacts: List[Dict], user_name: str, lat: float, 
                                 lon: float, address: str, time: str) -> List[Dict[str, any]]:
        """Send SOS alert to multiple emergency contacts"""
        phones = [contact["phone"] for contact in contacts]
        message = settings.SOS_MESSAGE_TEMPLATE.format(
            user_name=user_name,
            lat=lat,
            lon=lon,
            address=address or "Unknown location",
            time=time
        )
        return await SMSService.send_bulk_sms(phones, message)
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Indian mobile number format"""
        import re
        return bool(re.match(r'^[6-9]\d{9}$', phone))
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number to 10-digit format"""
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        # Remove +91 if present
        if phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        # Return last 10 digits
        return phone[-10:] if len(phone) >= 10 else phone

# Import regex for phone formatting
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import UserCreate, UserLogin, UserResponse, UserInDB, PasswordReset
from models.otp import OTPRequest, OTPVerify, OTPPurpose
from services.db import find_one, insert_one, update_one
from services.jwt_service import JWTService
from services.otp_service import OTPService
from services.sms_service import SMSService
from utils.security import hash_password, verify_password
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = JWTService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = await find_one("users", {"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user and send OTP"""
    try:
        # Check if user already exists
        existing_user = await find_one("users", {"phone": user_data.phone})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        if user_data.email:
            existing_email = await find_one("users", {"email": user_data.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user record (not verified yet)
        user_record = {
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "email": user_data.email,
            "password_hash": password_hash,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "settings": {
                "shake_sos": True,
                "shake_sensitivity": "medium",
                "sos_alarm": True,
                "location_interval": 60
            }
        }
        
        user_id = await insert_one("users", user_record)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Send OTP
        otp_result = await OTPService.send_otp(user_data.phone, OTPPurpose.REGISTER)
        
        if not otp_result["success"]:
            # Rollback user creation if OTP fails
            await update_one("users", {"_id": user_id}, {"$set": {"status": "failed"}})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=otp_result["message"]
            )
        
        logger.info(f"User registered successfully: {user_data.phone}")
        return {
            "message": "Registration successful. Please verify your phone number with OTP.",
            "user_id": user_id,
            "phone": user_data.phone,
            "otp_expires_in": otp_result.get("expires_in")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/verify-otp")
async def verify_otp(otp_data: OTPVerify):
    """Verify OTP and activate user account"""
    try:
        # Verify OTP
        otp_result = await OTPService.verify_otp_request(
            otp_data.phone, 
            otp_data.otp, 
            otp_data.purpose
        )
        
        if not otp_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=otp_result["message"]
            )
        
        # Find and activate user
        user = await find_one("users", {"phone": otp_data.phone})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user as verified
        await update_one("users", 
                        {"_id": user["_id"]}, 
                        {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}})
        
        # Generate JWT tokens
        tokens = JWTService.create_token_pair(str(user["_id"]))
        
        logger.info(f"User verified successfully: {otp_data.phone}")
        return {
            "message": "Phone number verified successfully",
            "user": {
                "id": str(user["_id"]),
                "full_name": user["full_name"],
                "phone": user["phone"],
                "email": user.get("email"),
                "is_verified": True
            },
            "tokens": tokens
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during OTP verification"
        )

@router.post("/login")
async def login(login_data: UserLogin):
    """Login user and return JWT tokens"""
    try:
        # Find user by phone or email
        query = {}
        if login_data.phone:
            query["phone"] = login_data.phone
        elif login_data.email:
            query["email"] = login_data.email
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone or email required"
            )
        
        user = await find_one("users", query)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is verified
        if not user.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your phone number first"
            )
        
        # Generate JWT tokens
        tokens = JWTService.create_token_pair(str(user["_id"]))
        
        logger.info(f"User logged in successfully: {user.get('phone', user.get('email'))}")
        return {
            "message": "Login successful",
            "user": {
                "id": str(user["_id"]),
                "full_name": user["full_name"],
                "phone": user["phone"],
                "email": user.get("email"),
                "is_verified": user.get("is_verified", False)
            },
            "tokens": tokens
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/request-otp")
async def request_otp(otp_request: OTPRequest):
    """Request OTP for password reset"""
    try:
        # Check if user exists
        user = await find_one("users", {"phone": otp_request.phone})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not registered"
            )
        
        # Send OTP
        otp_result = await OTPService.send_otp(otp_request.phone, OTPPurpose.RESET)
        
        if not otp_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=otp_result["message"]
            )
        
        return {
            "message": "OTP sent successfully",
            "phone": otp_request.phone,
            "expires_in": otp_result.get("expires_in")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request OTP error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending OTP"
        )

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password using OTP"""
    try:
        # Verify OTP
        otp_result = await OTPService.verify_otp_request(
            reset_data.phone, 
            reset_data.otp, 
            OTPPurpose.RESET
        )
        
        if not otp_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=otp_result["message"]
            )
        
        # Find user
        user = await find_one("users", {"phone": reset_data.phone})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        new_password_hash = hash_password(reset_data.new_password)
        
        # Update password
        await update_one("users", 
                        {"_id": user["_id"]}, 
                        {"$set": {
                            "password_hash": new_password_hash,
                            "password_updated_at": datetime.utcnow()
                        }})
        
        logger.info(f"Password reset successful: {reset_data.phone}")
        return {
            "message": "Password reset successful. Please login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting password"
        )

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": str(current_user["_id"]),
        "full_name": current_user["full_name"],
        "phone": current_user["phone"],
        "email": current_user.get("email"),
        "is_verified": current_user.get("is_verified", False),
        "created_at": current_user["created_at"],
        "last_location": current_user.get("last_location"),
        "settings": current_user.get("settings", {})
    }

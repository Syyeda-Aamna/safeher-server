from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ShakeSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class UserSettings(BaseModel):
    shake_sos: bool = True
    shake_sensitivity: ShakeSensitivity = ShakeSensitivity.MEDIUM
    sos_alarm: bool = True
    location_interval: int = 60  # minutes
    
    class Config:
        use_enum_values = True

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., regex=r'^[6-9]\d{9}$')  # Indian mobile number
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        return v

class UserLogin(BaseModel):
    phone: Optional[str] = Field(None, regex=r'^[6-9]\d{9}$')
    email: Optional[EmailStr] = None
    password: str
    
    @validator('phone', 'email')
    def validate_login_identifier(cls, v, values, field):
        if field.name == 'phone' and v is None and values.get('email') is None:
            raise ValueError('Either phone or email must be provided')
        if field.name == 'email' and v is None and values.get('phone') is None:
            raise ValueError('Either phone or email must be provided')
        return v

class UserResponse(BaseModel):
    id: str
    full_name: str
    phone: str
    email: Optional[str] = None
    is_verified: bool
    created_at: datetime
    last_location: Optional[Location] = None
    settings: UserSettings = UserSettings()

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    settings: Optional[UserSettings] = None

class UserInDB(UserResponse):
    password_hash: str

class PasswordReset(BaseModel):
    phone: str = Field(..., regex=r'^[6-9]\d{9}$')
    otp: str = Field(..., regex=r'^\d{6}$')
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        return v

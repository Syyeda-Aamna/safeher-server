from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class OTPPurpose(str, Enum):
    REGISTER = "register"
    RESET = "reset"

class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r'^[6-9]\d{9}$')  # Indian mobile number
    purpose: OTPPurpose = OTPPurpose.REGISTER
    
    class Config:
        use_enum_values = True

class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r'^[6-9]\d{9}$')
    otp: str = Field(..., pattern=r'^\d{6}$')
    purpose: OTPPurpose = OTPPurpose.REGISTER
    
    class Config:
        use_enum_values = True

class OTPResponse(BaseModel):
    id: str
    phone: str
    purpose: OTPPurpose
    expires_at: datetime
    used: bool
    created_at: datetime
    
    class Config:
        use_enum_values = True

class OTPInDB(OTPResponse):
    otp_hash: str

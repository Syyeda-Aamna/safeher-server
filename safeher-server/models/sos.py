from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TriggerType(str, Enum):
    MANUAL = "manual"
    SHAKE = "shake"
    CHECKIN = "checkin"

class SMSResult(BaseModel):
    phone: str
    status: str  # "sent", "failed", "pending"
    sent_at: datetime
    error_message: Optional[str] = None

class SOSTrigger(BaseModel):
    trigger_type: TriggerType = TriggerType.MANUAL
    location: Optional[dict] = None  # {lat, lon, address}

class SOSResponse(BaseModel):
    id: str
    user_id: str
    trigger_type: TriggerType
    location: dict  # {lat, lon, address}
    contacts_notified: List[str]
    sms_results: List[SMSResult]
    is_active: bool
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True

class SOSInDB(SOSResponse):
    pass

class SOSCreate(BaseModel):
    trigger_type: TriggerType = TriggerType.MANUAL
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    
    class Config:
        use_enum_values = True

class SOSCancel(BaseModel):
    reason: Optional[str] = None

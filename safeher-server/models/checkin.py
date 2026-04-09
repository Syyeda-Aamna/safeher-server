from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TimerStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    MISSED = "missed"

class CheckinStart(BaseModel):
    hours: int = Field(..., ge=0, le=24)
    minutes: int = Field(..., ge=0, le=59)
    
    @field_validator('hours', 'minutes')
    @classmethod
    def validate_time(cls, v, info):
        if info.field_name == 'hours' and v == 0 and info.data.get('minutes', 0) == 0:
            raise ValueError('Timer must be at least 1 minute')
        return v

class CheckinResponse(BaseModel):
    id: str
    user_id: str
    deadline: datetime
    is_active: bool
    checked_in: bool
    created_at: datetime
    status: TimerStatus = TimerStatus.PENDING
    
    class Config:
        use_enum_values = True

class CheckinInDB(CheckinResponse):
    pass

class CheckinSafe(BaseModel):
    timer_id: str
    message: Optional[str] = None

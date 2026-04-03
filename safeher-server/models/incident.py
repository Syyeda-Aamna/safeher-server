from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class IncidentType(str, Enum):
    HARASSMENT = "harassment"
    THEFT = "theft"
    ACCIDENT = "accident"
    MEDICAL = "medical"
    SUSPICIOUS = "suspicious"
    OTHER = "other"

class IncidentCreate(BaseModel):
    type: IncidentType = IncidentType.OTHER
    description: str = Field(..., min_length=10, max_length=1000)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    photo_url: Optional[str] = None
    
    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

class IncidentUpdate(BaseModel):
    type: Optional[IncidentType] = None
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    photo_url: Optional[str] = None
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip() if v else v

class IncidentResponse(BaseModel):
    id: str
    user_id: str
    type: IncidentType
    description: str
    location: dict  # {lat, lon, address}
    photo_url: Optional[str] = None
    created_at: datetime
    synced: bool = False
    
    class Config:
        use_enum_values = True

class IncidentInDB(IncidentResponse):
    pass

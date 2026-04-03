from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    accuracy: Optional[float] = None  # GPS accuracy in meters

class LocationResponse(BaseModel):
    id: str
    user_id: str
    lat: float
    lon: float
    address: Optional[str] = None
    accuracy: Optional[float] = None
    updated_at: datetime

class LocationShareCreate(BaseModel):
    expires_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week

class LocationShareResponse(BaseModel):
    id: str
    user_id: str
    token: str
    expires_at: datetime
    last_location: Optional[dict] = None  # {lat, lon, updated_at}
    is_active: bool = True
    share_url: str  # Full URL to share

class LiveLocationResponse(BaseModel):
    user_name: str
    lat: float
    lon: float
    address: Optional[str] = None
    last_updated: datetime
    is_active: bool

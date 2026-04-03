from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class Relationship(str, Enum):
    FAMILY = "family"
    FRIEND = "friend"
    PARTNER = "partner"
    COLLEAGUE = "colleague"
    NEIGHBOR = "neighbor"
    OTHER = "other"

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., regex=r'^[6-9]\d{9}$')  # Indian mobile number
    relationship: Relationship = Relationship.FRIEND
    is_primary: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, regex=r'^[6-9]\d{9}$')
    relationship: Optional[Relationship] = None
    is_primary: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class ContactResponse(BaseModel):
    id: str
    user_id: str
    name: str
    phone: str
    relationship: Relationship
    is_primary: bool
    created_at: datetime
    
    class Config:
        use_enum_values = True

class ContactInDB(ContactResponse):
    pass

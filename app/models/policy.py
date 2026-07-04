from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PolicyLinkCreate(BaseModel):
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    drive_url: str

class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

class PolicyOut(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    drive_url: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
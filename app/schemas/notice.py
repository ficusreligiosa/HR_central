from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoticeCreate(BaseModel):
    title: str
    message: str
    priority: Optional[str] = "normal"   # "normal" | "important" | "urgent"
    expiry_date: Optional[datetime] = None   # None = never expires

class NoticeOut(BaseModel):
    id: int
    title: str
    message: str
    priority: Optional[str] = "normal"
    expiry_date: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
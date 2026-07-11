from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Notice(Base):
    __tablename__ = "notices"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    message     = Column(Text, nullable=False)
    priority    = Column(String(20), default="normal")   # "normal" | "important" | "urgent"

    # expiry_date = NULL means the notice never expires (stays until deleted)
    expiry_date = Column(DateTime(timezone=True), nullable=True)

    created_by  = Column(String(100))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
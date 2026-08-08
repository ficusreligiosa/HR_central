from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Policy(Base):
    __tablename__ = "policies"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    category    = Column(String(100))
    description = Column(Text)

    # Populated when the policy is an uploaded file
    filename    = Column(String(255))
    filepath    = Column(String(500))
    # Raw bytes kept in the DB so files survive the ephemeral local disk
    # (e.g. Render's free tier), where uploads/policies gets wiped on redeploy.
    file_data   = Column(LargeBinary)

    # Populated when the policy is a Google Drive link instead of a file
    drive_url   = Column(String(500))

    created_by  = Column(String(50))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
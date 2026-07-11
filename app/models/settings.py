from sqlalchemy import Column, Integer, String
from app.database import Base

class CompanySettings(Base):
    """
    Singleton table — always exactly one row (id=1). Holds company-wide
    settings that admin/HR configure and every logged-in role can read,
    such as the HR Contact info shown on the Employee Portal.

    Kept as a real DB table (not localStorage) so it's visible to every
    employee regardless of which browser/computer they log in from —
    localStorage only lives on the machine that set it.
    """
    __tablename__ = "company_settings"

    id                = Column(Integer, primary_key=True, default=1)
    hr_manager_name   = Column(String(100), default="Harsh Kumar")
    doc_manager_name  = Column(String(100), default="Nupur Pandey")
    hr_email          = Column(String(100), default="hr@company.com")
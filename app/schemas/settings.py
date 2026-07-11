from pydantic import BaseModel
from typing import Optional

class CompanySettingsUpdate(BaseModel):
    hr_manager_name: Optional[str] = None
    doc_manager_name: Optional[str] = None
    hr_email: Optional[str] = None

class CompanySettingsOut(BaseModel):
    hr_manager_name: str
    doc_manager_name: str
    hr_email: str

    class Config:
        from_attributes = True
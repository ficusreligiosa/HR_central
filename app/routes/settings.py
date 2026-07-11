from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import CompanySettings
from app.models.user import User
from app.schemas.settings import CompanySettingsUpdate, CompanySettingsOut
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/settings", tags=["Settings"])

def _get_or_create_settings(db: Session) -> CompanySettings:
    settings = db.query(CompanySettings).filter(CompanySettings.id == 1).first()
    if not settings:
        settings = CompanySettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("/hr-contact", response_model=CompanySettingsOut)
def get_hr_contact(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Every logged-in role can read this — shown on the Employee Portal."""
    return _get_or_create_settings(db)

@router.patch("/hr-contact", response_model=CompanySettingsOut)
def update_hr_contact(payload: CompanySettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    settings = _get_or_create_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
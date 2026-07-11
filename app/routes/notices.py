from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.notice import Notice
from app.models.user import User
from app.schemas.notice import NoticeCreate, NoticeOut
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/notices", tags=["Notices"])

@router.get("/", response_model=List[NoticeOut])
def list_active_notices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Every logged-in role sees only currently-active (non-expired) notices.
    Shown on the Dashboard (admin/hr/doc) and Employee Portal (emp)."""
    now = datetime.utcnow()
    return db.query(Notice).filter(
        or_(Notice.expiry_date.is_(None), Notice.expiry_date >= now)
    ).order_by(Notice.created_at.desc()).all()

@router.get("/all", response_model=List[NoticeOut])
def list_all_notices(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Admin-only — includes already-expired notices, for management in Setup & Config."""
    return db.query(Notice).order_by(Notice.created_at.desc()).all()

@router.post("/", response_model=NoticeOut, status_code=201)
def create_notice(payload: NoticeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    notice = Notice(
        title=payload.title,
        message=payload.message,
        priority=payload.priority or "normal",
        expiry_date=payload.expiry_date,
        created_by=current_user.display_name,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice

@router.delete("/{notice_id}", status_code=204)
def delete_notice(notice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(notice)
    db.commit()
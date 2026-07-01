from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.database import get_db
from app.models.form_submission import FormSubmission
from app.models.employee import Employee
from app.models.user import User
from app.auth import get_current_user, require_hr_admin, require_hr_doc

router = APIRouter(prefix="/api/inbox", tags=["Form Inbox"])

class InboxCreate(BaseModel):
    name: str
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    date_of_joining: Optional[str] = None
    marital_status: Optional[str] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    blood_group: Optional[str] = None
    qualification: Optional[str] = None
    is_pf_deducted: Optional[str] = None
    is_esic_deducted: Optional[str] = None
    aadhar_link: Optional[str] = None
    pan_link: Optional[str] = None
    cheque_link: Optional[str] = None
    offer_letter_link: Optional[str] = None
    submitted_at: Optional[str] = None

class InboxDraftUpdate(BaseModel):
    employee_code: Optional[str] = None
    employee_type: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    supervisor: Optional[str] = None
    hr_draft: Optional[str] = None  # JSON string

class InboxApprove(BaseModel):
    employee_code: str
    employee_type: str
    department: str
    designation: str
    supervisor: Optional[str] = None

class InboxReject(BaseModel):
    reason: Optional[str] = None

# ── GET ALL ───────────────────────────────────────────────
@router.get("/")
def get_submissions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_doc)
):
    query = db.query(FormSubmission)
    if status:
        query = query.filter(FormSubmission.status == status)
    submissions = query.order_by(FormSubmission.created_at.desc()).all()

    # Mark submissions that are already in employee DB
    result = []
    for s in submissions:
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        if s.status == 'pending':
            # Check if already imported
            exists = db.query(Employee).filter(
                Employee.name == s.name,
                Employee.contact == s.contact
            ).first()
            if exists:
                d['already_in_db'] = True
                d['existing_code'] = exists.employee_code
            else:
                d['already_in_db'] = False
        result.append(d)
    return result

# ── GET ONE ───────────────────────────────────────────────
@router.get("/{submission_id}")
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_doc)
):
    s = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    return s

# ── CREATE (from CSV import or future Google Form webhook) ─
@router.post("/", status_code=201)
def create_submission(
    payload: InboxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    s = FormSubmission(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

# ── SAVE DRAFT (autosave HR progress) ────────────────────
@router.patch("/{submission_id}/draft")
def save_draft(
    submission_id: int,
    payload: InboxDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_doc)
):
    s = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    if s.status not in ('pending',):
        raise HTTPException(status_code=400, detail="Can only edit pending submissions")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(s, field, value)

    db.commit()
    db.refresh(s)
    return s

# ── APPROVE ───────────────────────────────────────────────
@router.post("/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    payload: InboxApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    s = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    if s.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Submission is already {s.status}")

    # Check employee code not already taken
    existing = db.query(Employee).filter(Employee.employee_code == payload.employee_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee code {payload.employee_code} already exists")

    # Create employee record
    emp = Employee(
        employee_code    = payload.employee_code,
        employee_type    = payload.employee_type,
        department       = payload.department,
        designation      = payload.designation,
        supervisor       = payload.supervisor,
        status           = "Active",
        name             = s.name,
        father_name      = s.father_name,
        date_of_birth    = s.date_of_birth,
        date_of_joining  = s.date_of_joining,
        marital_status   = s.marital_status,
        gender           = s.gender,
        contact          = s.contact,
        personal_email   = s.email,
        aadhar_number    = s.aadhar_number,
        pan_number       = s.pan_number,
        bank_name        = s.bank_name,
        account_number   = s.account_number,
        ifsc_code        = s.ifsc_code,
        blood_group      = s.blood_group,
        qualification    = s.qualification,
        is_pf_deducted   = s.is_pf_deducted == 'Yes',
        is_esic_deducted = s.is_esic_deducted == 'Yes',
        form_row_id      = str(s.id),
        inbox_status     = "Approved",
    )
    db.add(emp)

    # Mark submission as approved
    s.status       = 'approved'
    s.employee_code = payload.employee_code
    s.employee_type = payload.employee_type
    s.department    = payload.department
    s.designation   = payload.designation
    s.supervisor    = payload.supervisor
    s.reviewed_by   = current_user.display_name
    s.reviewed_at   = datetime.utcnow()

    db.commit()
    db.refresh(emp)
    return {"message": f"Approved — employee {payload.employee_code} created", "employee_code": payload.employee_code}

# ── REJECT ────────────────────────────────────────────────
@router.post("/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    payload: InboxReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    s = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    if s.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Submission is already {s.status}")

    s.status       = 'rejected'
    s.reject_reason = payload.reason
    s.reviewed_by  = current_user.display_name
    s.reviewed_at  = datetime.utcnow()

    db.commit()
    return {"message": "Submission rejected"}

# ── STATS ─────────────────────────────────────────────────
@router.get("/meta/stats")
def inbox_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_doc)
):
    total    = db.query(FormSubmission).count()
    pending  = db.query(FormSubmission).filter(FormSubmission.status == 'pending').count()
    approved = db.query(FormSubmission).filter(FormSubmission.status == 'approved').count()
    rejected = db.query(FormSubmission).filter(FormSubmission.status == 'rejected').count()
    return {"total": total, "pending": pending, "approved": approved, "rejected": rejected}
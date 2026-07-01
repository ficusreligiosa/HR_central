from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id               = Column(Integer, primary_key=True, index=True)

    # Status: pending | approved | rejected
    status           = Column(String(20), default="pending", index=True)

    # Raw form data from Google Form / CSV
    name             = Column(String(100))
    father_name      = Column(String(100))
    date_of_birth    = Column(String(20))
    date_of_joining  = Column(String(20))
    marital_status   = Column(String(20))
    gender           = Column(String(10))
    contact          = Column(String(15))
    email            = Column(String(100))
    aadhar_number    = Column(String(25))
    pan_number       = Column(String(15))
    bank_name        = Column(String(100))
    account_number   = Column(String(30))
    ifsc_code        = Column(String(15))
    blood_group      = Column(String(5))
    qualification    = Column(String(100))
    is_pf_deducted   = Column(String(5))
    is_esic_deducted = Column(String(5))

    # Drive links
    aadhar_link      = Column(Text)
    pan_link         = Column(Text)
    cheque_link      = Column(Text)
    offer_letter_link= Column(Text)

    # Filled by HR during approval
    employee_code    = Column(String(20))
    employee_type    = Column(String(5))
    department       = Column(String(100))
    designation      = Column(String(100))
    supervisor       = Column(String(100))

    # HR draft — save progress even before final approval
    hr_draft         = Column(Text)   # JSON string of partial HR edits

    # Meta
    submitted_at     = Column(String(30))   # original form timestamp
    reviewed_by      = Column(String(100))
    reviewed_at      = Column(DateTime(timezone=True))
    reject_reason    = Column(Text)

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
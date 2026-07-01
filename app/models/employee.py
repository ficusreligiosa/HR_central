from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id                = Column(Integer, primary_key=True, index=True)
    employee_code     = Column(String(20), unique=True, nullable=False, index=True)
    employee_type     = Column(String(5), nullable=False)   # G1 / G2 / G3
    status            = Column(String(20), default="Active")

    # Personal
    name              = Column(String(100), nullable=False)
    father_name       = Column(String(100))
    date_of_birth     = Column(String(20))
    age               = Column(Integer)
    gender            = Column(String(10))
    marital_status    = Column(String(20))
    blood_group       = Column(String(5))
    contact           = Column(String(15))
    personal_email    = Column(String(100))
    official_email    = Column(String(100))
    address           = Column(Text)

    # Documents
    aadhar_number     = Column(String(20))
    pan_number        = Column(String(15))
    qualification     = Column(String(100))

    # Bank
    bank_name         = Column(String(100))
    account_number    = Column(String(30))
    ifsc_code         = Column(String(15))

    # Employment
    department        = Column(String(100))
    designation       = Column(String(100))
    supervisor        = Column(String(100))
    date_of_joining   = Column(String(20))
    probation_end     = Column(String(20))
    confirmation_date = Column(String(20))

    # Statutory
    epfo_number       = Column(String(30))
    esic_number       = Column(String(30))
    uan_number        = Column(String(30))

    # Salary
    basic             = Column(Float, default=0)
    hra               = Column(Float, default=0)
    other_allowance   = Column(Float, default=0)
    spl_allowance     = Column(Float, default=0)
    monthly_gross     = Column(Float, default=0)
    ctc_monthly       = Column(Float, default=0)
    ctc_annual        = Column(Float, default=0)
    take_home         = Column(Float, default=0)
    is_pf_deducted    = Column(Boolean, default=True)
    is_esic_deducted  = Column(Boolean, default=True)
    has_insurance     = Column(Boolean, default=False)
    has_bonus         = Column(Boolean, default=True)
    has_gratuity      = Column(Boolean, default=True)
    has_el            = Column(Boolean, default=True)
    has_cl            = Column(Boolean, default=True)

    # Document checklist
    doc_aadhar        = Column(String(20), default="Pending")
    doc_pan           = Column(String(20), default="Pending")
    doc_photo         = Column(String(20), default="Pending")
    doc_marksheet     = Column(String(20), default="Pending")
    doc_experience    = Column(String(20), default="Pending")
    doc_bank          = Column(String(20), default="Pending")
    doc_offer_letter  = Column(String(20), default="Pending")
    doc_joining_form  = Column(String(20), default="Pending")

    # Inbox
    form_row_id       = Column(String(50))
    inbox_status      = Column(String(20), default="Pending")

    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), onupdate=func.now())
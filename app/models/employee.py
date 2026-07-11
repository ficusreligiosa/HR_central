from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id                = Column(Integer, primary_key=True, index=True)
    employee_code     = Column(String(20), unique=True, nullable=False, index=True)
    employee_type     = Column(String(5), nullable=False)   # G1 / G2
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

    # ── EXTENDED HR FIELDS ────────────────────────────────────────────────
    # Added to support the full legacy 78-column HR sheet structure so bulk
    # import can carry over every field the company already tracks.

    # Extra biodata / statutory doc
    doc_medical_certificate = Column(String(20), default="Pending")

    # Emergency contact (promised by the old bulk-import template but never
    # actually added to the model until now)
    emergency_contact_number  = Column(String(15))
    emergency_contact_person  = Column(String(100))
    emergency_relation        = Column(String(50))

    # Extra salary components (all monthly unless noted)
    med_allowance             = Column(Float, default=0)
    misc_allowance            = Column(Float, default=0)
    fixed_other_allowance     = Column(Float, default=0)
    variable_pay_annual       = Column(Float, default=0)
    esi_employer_contribution = Column(Float, default=0)   # ESI, employer's 3.25%
    pf_employer_contribution  = Column(Float, default=0)   # PF, employer's 13%
    esic_employee_deduction   = Column(Float, default=0)   # ESIC, employee's 0.75%
    pf_employee_deduction     = Column(Float, default=0)   # PF, employee's 12%

    # Monetary accrual amounts — distinct from the has_insurance/has_bonus/
    # has_gratuity/has_el/has_cl booleans above, which just flag eligibility.
    # These are the actual ₹ amounts as tracked in the legacy sheet.
    insurance_amount = Column(Float, default=0)
    bonus_amount     = Column(Float, default=0)
    gratuity_amount  = Column(Float, default=0)
    pl_amount        = Column(Float, default=0)  # Privilege Leave
    cl_amount        = Column(Float, default=0)  # Casual Leave

    # Onboarding document checklist (each tracked as a status string, e.g.
    # "Pending" / "Received" / "Yes" / "No", matching the existing doc_* style)
    doc_personal_details          = Column(String(20), default="Pending")
    doc_form_26                   = Column(String(20), default="Pending")
    doc_esi_form1                 = Column(String(20), default="Pending")
    doc_form2_pf                  = Column(String(20), default="Pending")
    doc_nomination_form_f         = Column(String(20), default="Pending")
    doc_epf_form11                = Column(String(20), default="Pending")
    doc_joining_report            = Column(String(20), default="Pending")
    doc_rules_regulation_ack      = Column(String(20), default="Pending")
    doc_appointment_letter        = Column(String(20), default="Pending")
    doc_confirmation_letter       = Column(String(20), default="Pending")
    doc_service_record            = Column(String(20), default="Pending")
    doc_increment_letter          = Column(String(20), default="Pending")
    doc_promotion_letter          = Column(String(20), default="Pending")
    doc_employment_history_sheet  = Column(String(20), default="Pending")
    doc_jd                        = Column(String(20), default="Pending")
    doc_master_task_sheet         = Column(String(20), default="Pending")
    doc_kra                       = Column(String(20), default="Pending")
    doc_kpi                       = Column(String(20), default="Pending")

    # Asset issuance tracking
    asset_sim    = Column(String(20), default="Pending")
    asset_laptop = Column(String(20), default="Pending")

    # Exit / lifecycle tracking
    file_number             = Column(String(50))
    date_of_leaving          = Column(String(20))
    full_final_completed    = Column(String(20), default="Pending")
    relieving_letter_issued = Column(String(20), default="Pending")
    remarks                 = Column(Text)
    address_verification_link = Column(String(500))

    # Import audit trail
    source      = Column(String(30))   # "Manual", "Bulk Import", "Google Form"
    approved_by = Column(String(100))

    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), onupdate=func.now())
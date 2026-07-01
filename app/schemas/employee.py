from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    employee_code: str
    employee_type: str
    status: Optional[str] = "Active"
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    contact: Optional[str] = None
    personal_email: Optional[str] = None
    official_email: Optional[str] = None
    address: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    qualification: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    supervisor: Optional[str] = None
    date_of_joining: Optional[str] = None
    probation_end: Optional[str] = None
    confirmation_date: Optional[str] = None
    epfo_number: Optional[str] = None
    esic_number: Optional[str] = None
    uan_number: Optional[str] = None
    basic: Optional[float] = 0
    hra: Optional[float] = 0
    other_allowance: Optional[float] = 0
    spl_allowance: Optional[float] = 0
    monthly_gross: Optional[float] = 0
    ctc_monthly: Optional[float] = 0
    ctc_annual: Optional[float] = 0
    take_home: Optional[float] = 0
    is_pf_deducted: Optional[bool] = True
    is_esic_deducted: Optional[bool] = True
    has_insurance: Optional[bool] = False
    has_bonus: Optional[bool] = True
    has_gratuity: Optional[bool] = True
    has_el: Optional[bool] = True
    has_cl: Optional[bool] = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    employee_type: Optional[str] = None
    status: Optional[str] = None
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    contact: Optional[str] = None
    personal_email: Optional[str] = None
    official_email: Optional[str] = None
    address: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    qualification: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    supervisor: Optional[str] = None
    date_of_joining: Optional[str] = None
    probation_end: Optional[str] = None
    confirmation_date: Optional[str] = None
    epfo_number: Optional[str] = None
    esic_number: Optional[str] = None
    uan_number: Optional[str] = None
    basic: Optional[float] = None
    hra: Optional[float] = None
    other_allowance: Optional[float] = None
    spl_allowance: Optional[float] = None
    monthly_gross: Optional[float] = None
    ctc_monthly: Optional[float] = None
    ctc_annual: Optional[float] = None
    take_home: Optional[float] = None
    is_pf_deducted: Optional[bool] = None
    is_esic_deducted: Optional[bool] = None
    has_insurance: Optional[bool] = None
    has_bonus: Optional[bool] = None
    has_gratuity: Optional[bool] = None
    has_el: Optional[bool] = None
    has_cl: Optional[bool] = None

class EmployeeOut(EmployeeBase):
    id: int

    class Config:
        from_attributes = True
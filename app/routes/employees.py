from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.employee import Employee
from app.models.user import User
from app.auth import get_current_user, require_hr_admin, require_hr_doc

router = APIRouter(prefix="/api/employees", tags=["Employees"])

class EmployeeCreate(BaseModel):
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

@router.get("/meta/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(require_hr_doc)):
    return {
        "total":    db.query(Employee).count(),
        "g1":       db.query(Employee).filter(Employee.employee_type == "G1").count(),
        "g2":       db.query(Employee).filter(Employee.employee_type == "G2").count(),
        "g3":       db.query(Employee).filter(Employee.employee_type == "G3").count(),
        "active":   db.query(Employee).filter(Employee.status == "Active").count(),
        "inactive": db.query(Employee).filter(Employee.status == "Inactive").count(),
        "resigned": db.query(Employee).filter(Employee.status == "Resigned").count(),
    }

@router.get("/")
def get_employees(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_doc)
):
    query = db.query(Employee)
    if type:
        query = query.filter(Employee.employee_type == type)
    if status:
        query = query.filter(Employee.status == status)
    if department:
        query = query.filter(Employee.department == department)
    if search:
        query = query.filter(
            Employee.name.ilike(f"%{search}%") |
            Employee.employee_code.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()

@router.get("/{employee_code}")
def get_employee(employee_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "emp" and current_user.employee_code != employee_code:
        raise HTTPException(status_code=403, detail="Access denied")
    emp = db.query(Employee).filter(Employee.employee_code == employee_code).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/", status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_admin)):
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="Employee code already exists")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

@router.patch("/{employee_code}")
def update_employee(employee_code: str, payload: EmployeeUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_doc)):
    emp = db.query(Employee).filter(Employee.employee_code == employee_code).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp

@router.delete("/{employee_code}", status_code=204)
def delete_employee(employee_code: str, db: Session = Depends(get_db), current_user: User = Depends(require_hr_admin)):
    emp = db.query(Employee).filter(Employee.employee_code == employee_code).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.performance import PerformanceReview
from app.models.employee import Employee
from app.models.user import User
from app.auth import get_current_user, require_hr_admin, get_effective_role

router = APIRouter(prefix="/api/performance", tags=["Performance"])


# ── SCHEMAS ──────────────────────────────────────────────
class KPIItem(BaseModel):
    name: str
    weightage: float = Field(ge=0)
    rating: float = Field(ge=0)


class PerformanceCreate(BaseModel):
    employee_code: str
    period_type: str          # "monthly" or "quarterly"
    period_label: str         # "March 2026" or "Q1 2026"
    year: int
    period_value: str         # "03" or "Q1"
    kpis: List[KPIItem]
    remarks: Optional[str] = None


class PerformanceUpdate(BaseModel):
    period_type: Optional[str] = None
    period_label: Optional[str] = None
    year: Optional[int] = None
    period_value: Optional[str] = None
    kpis: Optional[List[KPIItem]] = None
    remarks: Optional[str] = None

def calc_totals(kpis: list):
    total_weightage = sum(k.get("weightage", 0) for k in kpis)
    final_rating = sum(k.get("rating", 0) for k in kpis)
    final_percent = round((final_rating / total_weightage) * 100, 2) if total_weightage > 0 else 0
    return total_weightage, final_rating, final_percent


# ── LIST — HR/Admin see all, employee sees only their own ──
@router.get("/")
def list_reviews(
    employee_code: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(PerformanceReview)

    role = get_effective_role(current_user)
    if role == "emp":
        # Employees can only ever see their own reviews
        if not current_user.employee_code:
            raise HTTPException(status_code=403, detail="No employee profile linked to this account")
        query = query.filter(PerformanceReview.employee_code == current_user.employee_code)
    elif role not in ("admin", "hr"):
        raise HTTPException(status_code=403, detail="Access denied")
    else:
        # HR/Admin can optionally filter by employee_code
        if employee_code:
            query = query.filter(PerformanceReview.employee_code == employee_code)

    if year:
        query = query.filter(PerformanceReview.year == year)

    return query.order_by(PerformanceReview.year.desc(), PerformanceReview.id.desc()).all()


# ── GET ONE ──────────────────────────────────────────────
@router.get("/{review_id}")
def get_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    role = get_effective_role(current_user)
    if role == "emp" and current_user.employee_code != r.employee_code:
        raise HTTPException(status_code=403, detail="Access denied")
    if role not in ("admin", "hr", "emp"):
        raise HTTPException(status_code=403, detail="Access denied")
    return r


# ── CREATE — HR/Admin only ──────────────────────────────
@router.post("/", status_code=201)
def create_review(payload: PerformanceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_admin)):
    emp = db.query(Employee).filter(Employee.employee_code == payload.employee_code).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {payload.employee_code} not found")

    kpi_dicts = [k.model_dump() for k in payload.kpis]
    total_weightage, final_rating, final_percent = calc_totals(kpi_dicts)

    review = PerformanceReview(
        employee_code   = payload.employee_code,
        period_type     = payload.period_type,
        period_label    = payload.period_label,
        year            = payload.year,
        period_value    = payload.period_value,
        kpis            = kpi_dicts,
        total_weightage = total_weightage,
        final_rating    = final_rating,
        final_percent   = final_percent,
        remarks         = payload.remarks,
        reviewed_by     = current_user.display_name,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ── UPDATE — HR/Admin only ──────────────────────────────
@router.patch("/{review_id}")
def update_review(review_id: int, payload: PerformanceUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_admin)):
    r = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")

    data = payload.model_dump(exclude_unset=True)
    if "kpis" in data:
        kpi_dicts = [k if isinstance(k, dict) else k for k in data["kpis"]]
        total_weightage, final_rating, final_percent = calc_totals(kpi_dicts)
        r.kpis = kpi_dicts
        r.total_weightage = total_weightage
        r.final_rating = final_rating
        r.final_percent = final_percent
        del data["kpis"]

    for field, value in data.items():
        setattr(r, field, value)

    r.reviewed_by = current_user.display_name
    db.commit()
    db.refresh(r)
    return r


# ── DELETE — HR/Admin only ──────────────────────────────
@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_hr_admin)):
    r = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(r)
    db.commit()

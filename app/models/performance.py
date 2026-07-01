from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id              = Column(Integer, primary_key=True, index=True)
    employee_code   = Column(String(20), ForeignKey("employees.employee_code"), nullable=False, index=True)

    # Period — flexible: HR can pick monthly or quarterly
    period_type     = Column(String(10), nullable=False)   # "monthly" or "quarterly"
    period_label    = Column(String(20), nullable=False)    # e.g. "March 2026" or "Q1 2026"
    year            = Column(Integer, nullable=False)
    period_value    = Column(String(10), nullable=False)    # "03" for March, or "Q1"

    # KPIs stored as JSON list — each item: {"name": str, "weightage": float, "rating": float}
    # This makes KPI count fully flexible — HR can add as many as needed
    kpis            = Column(JSON, nullable=False, default=list)

    # Calculated fields (stored so they don't need recomputing on every read)
    total_weightage = Column(Float, default=0)
    final_rating    = Column(Float, default=0)
    final_percent   = Column(Float, default=0)

    remarks         = Column(String(500))
    reviewed_by     = Column(String(100))   # HR display name who filled this

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
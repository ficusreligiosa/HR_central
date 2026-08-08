from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base, SessionLocal
from app.config import settings

# Import all models so Base knows about them
from app.models import User, Employee, FormSubmission, PerformanceReview, Policy, Notice, CompanySettings

# Import routes
from app.routes.auth import router as auth_router
from app.routes.employees import router as emp_router
from app.routes.inbox import router as inbox_router
from app.routes.performance import router as performance_router
from app.routes.google_sheet import router as google_sheet_router
from app.routes.policies import router as policies_router
from app.routes.notices import router as notices_router
from app.routes.settings import router as settings_router

# ── Create tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Ensure new employee columns exist ──────────────────────────────────────
try:
    import migrate_add_employee_fields
    migrate_add_employee_fields.run()
except Exception as e:
    print(f"[WARNING] Column addition migration error: {e}")

# ── Migrate varchar columns to TEXT ────────────────────────────────────────
def migrate_columns():
    """Alter known small varchar/date/document columns to TEXT so long PANs, doc URLs, empty dates etc fit."""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        # Standard columns to convert to TEXT
        cols = [
            "pan_number", "contact", "emergency_contact_number",
            "aadhar_number", "ifsc_code",
            "date_of_birth", "date_of_joining", "probation_end",
            "confirmation_date", "date_of_leaving",
            "doc_aadhar", "doc_pan", "doc_photo", "doc_marksheet", "doc_experience",
            "doc_bank", "doc_offer_letter", "doc_joining_form", "inbox_status",
            "qualification", "doc_medical_certificate", "doc_personal_details",
            "doc_form_26", "doc_esi_form1", "doc_form2_pf", "doc_nomination_form_f",
            "doc_epf_form11", "doc_joining_report", "doc_rules_regulation_ack",
            "doc_appointment_letter", "doc_confirmation_letter", "doc_service_record",
            "doc_increment_letter", "doc_promotion_letter", "doc_employment_history_sheet",
            "doc_jd", "doc_master_task_sheet", "doc_kra", "doc_kpi",
            "asset_sim", "asset_laptop", "remarks", "address_verification_link",
            "emergency_contact_person", "emergency_relation", "file_number",
            "source", "approved_by", "employee_type"
        ]
        for col in cols:
            try:
                db.execute(text(f"ALTER TABLE employees ALTER COLUMN {col} TYPE TEXT"))
            except Exception:
                pass  # already TEXT or doesn't exist
        
        # Ensure employee_type drops NOT NULL
        try:
            db.execute(text("ALTER TABLE employees ALTER COLUMN employee_type DROP NOT NULL"))
        except Exception:
            pass

        # Boolean columns that need casting to TEXT
        bool_cols = ["full_final_completed", "relieving_letter_issued"]
        for col in bool_cols:
            try:
                db.execute(text(f"ALTER TABLE employees ALTER COLUMN {col} TYPE TEXT USING {col}::text"))
            except Exception:
                pass

        db.commit()
        print("[OK] DB columns migrated to TEXT")
    finally:
        db.close()

migrate_columns()

# ── Ensure policies table has file_data column (bytes survive redeploys) ──
def migrate_policies():
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE policies ADD COLUMN IF NOT EXISTS file_data BYTEA"))
        db.commit()
        print("[OK] policies.file_data column ensured")
    except Exception:
        pass
    finally:
        db.close()

migrate_policies()

# ── Seed default users ─────────────────────────────────────────────────────
def seed_users():
    from app.auth import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            default_users = [
                User(username="admin",  password_hash=hash_password("Admin@123"),  display_name="Administrator",  role="admin"),
                User(username="harsh",  password_hash=hash_password("Harsh@123"),  display_name="Harsh Kumar",    role="hr"),
                User(username="nupur",  password_hash=hash_password("Nupur@123"),  display_name="Nupur Pandey",   role="admin"),
                User(username="emp",    password_hash=hash_password("Emp@123"),    display_name="Employee",       role="emp"),
            ]
            db.add_all(default_users)
            db.commit()
            print("[OK] Default users seeded")
    finally:
        db.close()

seed_users()

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="HR Management System — Surface Paints Pvt Ltd",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(emp_router)
app.include_router(inbox_router)
app.include_router(performance_router)
app.include_router(google_sheet_router)
app.include_router(policies_router)
app.include_router(notices_router)
app.include_router(settings_router)

# ── Serve frontend ─────────────────────────────────────────────────────────
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "company": settings.COMPANY_NAME}
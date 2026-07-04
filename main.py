from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base, SessionLocal
from app.config import settings

# Import all models so Base knows about them
from app.models import User, Employee, FormSubmission, PerformanceReview, Policy

# Import routes
from app.routes.auth import router as auth_router
from app.routes.employees import router as emp_router
from app.routes.inbox import router as inbox_router
from app.routes.performance import router as performance_router
from app.routes.google_sheet import router as google_sheet_router
from app.routes.policies import router as policies_router

# ── Create tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Seed default users ─────────────────────────────────────────────────────
# NOTE: these accounts still exist and can still be used to log in — the
# only thing that changed is the login page no longer shows one-click demo
# shortcut cards for them. Admin/HR/Doc/Employee(demo) still sign in by
# typing their username + password like everyone else.
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
            print("✅ Default users seeded")
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

# ── Serve frontend ─────────────────────────────────────────────────────────
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "company": settings.COMPANY_NAME}
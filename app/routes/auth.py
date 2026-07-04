from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.employee import Employee
from app.auth import verify_password, create_access_token, get_current_user, get_effective_role

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str


def _resolve_login_user(db: Session, identifier: str) -> Optional[User]:
    """
    Resolves whatever the person typed into the "Username" field to a User row.

    Supports:
      1. Exact username match — covers admin/hr/doc accounts AND employee
         accounts (an employee's username is always their employee_code).
      2. Employee email fallback — if no direct username match, look up
         the Employee by personal or official email (case-insensitive),
         then find that employee's linked User row via employee_code.
    """
    identifier = (identifier or "").strip()
    if not identifier:
        return None

    user = db.query(User).filter(User.username == identifier).first()
    if user:
        return user

    emp = db.query(Employee).filter(
        (Employee.official_email.ilike(identifier)) |
        (Employee.personal_email.ilike(identifier))
    ).first()
    if emp:
        return db.query(User).filter(User.employee_code == emp.employee_code).first()

    return None


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _resolve_login_user(db, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")
    effective_role = get_effective_role(user)
    token = create_access_token(data={"sub": user.username, "role": effective_role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id":            user.id,
            "username":      user.username,
            "display_name":  user.display_name,
            "role":          effective_role,
            "employee_code": user.employee_code,
        }
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id":            current_user.id,
        "username":      current_user.username,
        "display_name":  current_user.display_name,
        "role":          get_effective_role(current_user),
        "employee_code": current_user.employee_code,
    }
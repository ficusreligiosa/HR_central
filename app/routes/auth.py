from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.employee import Employee
from app.auth import verify_password, create_access_token, get_current_user, get_effective_role, require_admin, hash_password

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


class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "emp"
    employee_code: Optional[str] = None


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.id.desc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "role": u.role,
            "employee_code": u.employee_code,
            "is_active": u.is_active,
            "created_at": str(u.created_at) if u.created_at else None,
        }
        for u in users
    ]


@router.post("/users")
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password is required")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists")

    new_user = User(
        username=username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip() or username,
        role=payload.role,
        employee_code=payload.employee_code.strip() if payload.employee_code else None,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "display_name": new_user.display_name,
        "role": new_user.role,
        "employee_code": new_user.employee_code,
        "is_active": new_user.is_active,
    }


@router.put("/users/{user_id}/toggle")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot toggle your own account status")

    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

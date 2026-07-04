import os
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.policy import Policy
from app.models.user import User
from app.schemas.policy import PolicyOut, PolicyLinkCreate, PolicyUpdate
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/policies", tags=["Policies"])

# Files are stored on the server's local disk under uploads/policies.
# NOTE: on platforms with ephemeral filesystems (e.g. Render's free tier
# without a persistent disk attached), files written here will be lost on
# redeploy/restart. Attach a persistent disk mounted at this path in
# production, or swap this for S3/Cloud Storage later.
UPLOAD_DIR = os.path.join("uploads", "policies")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _safe_filename(filename: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]", "_", filename or "file")
    return name[-150:]  # cap length to keep paths sane


# ── LIST — every logged-in role can view ────────────────────────────────────
@router.get("/", response_model=List[PolicyOut])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Policy).order_by(Policy.created_at.desc()).all()


# ── CREATE (upload from computer) — admin only ──────────────────────────────
@router.post("/upload", response_model=PolicyOut, status_code=201)
async def upload_policy(
    title: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext or 'unknown'}' not allowed. Allowed: PDF, DOC, DOCX, and images."
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    stored_name = f"{uuid.uuid4().hex}_{_safe_filename(file.filename)}"
    disk_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(disk_path, "wb") as f:
        f.write(contents)

    policy = Policy(
        title=title,
        category=category,
        description=description,
        filename=file.filename,
        filepath=disk_path.replace("\\", "/"),
        drive_url=None,
        created_by=current_user.username,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


# ── CREATE (Google Drive link) — admin only ─────────────────────────────────
@router.post("/link", response_model=PolicyOut, status_code=201)
def create_policy_link(
    payload: PolicyLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    policy = Policy(
        title=payload.title,
        category=payload.category,
        description=payload.description,
        filename=None,
        filepath=None,
        drive_url=payload.drive_url,
        created_by=current_user.username,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


# ── EDIT metadata — admin only ───────────────────────────────────────────────
@router.patch("/{policy_id}", response_model=PolicyOut)
def update_policy(
    policy_id: int,
    payload: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    db.commit()
    db.refresh(policy)
    return policy


# ── VIEW / DOWNLOAD — every logged-in role can view ─────────────────────────
@router.get("/{policy_id}/download")
def download_policy(policy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.drive_url:
        return RedirectResponse(policy.drive_url)
    if policy.filepath and os.path.exists(policy.filepath):
        return FileResponse(policy.filepath, filename=policy.filename or os.path.basename(policy.filepath))
    raise HTTPException(status_code=404, detail="File not found on server")


# ── DELETE — admin only ──────────────────────────────────────────────────────
@router.delete("/{policy_id}", status_code=204)
def delete_policy(policy_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.filepath and os.path.exists(policy.filepath):
        try:
            os.remove(policy.filepath)
        except OSError:
            pass
    db.delete(policy)
    db.commit()
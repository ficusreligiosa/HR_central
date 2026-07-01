from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    employee_code: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
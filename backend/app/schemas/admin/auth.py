from typing import Optional

from pydantic import BaseModel, EmailStr


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminOut(BaseModel):
    id: str
    name: Optional[str] = None
    username: str
    email: EmailStr
    is_admin: bool = True


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminOut

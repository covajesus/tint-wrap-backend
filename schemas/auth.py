from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 50:
            raise ValueError("用户名长度须为 3-50 个字符")
        if not v.isalnum() and "_" not in v:
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码长度至少 8 位")
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("密码须包含字母和数字")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    avatar: str | None
    bio: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    avatar: str | None = None
    bio: str | None = None

from datetime import datetime
from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class UserProfileResponse(BaseModel):
    id: int
    username: str
    role: str
    avatar: str | None
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

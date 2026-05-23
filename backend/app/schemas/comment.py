from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.auth import UserResponse


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(CommentBase):
    id: int
    article_id: int
    user_id: int
    parent_id: int | None
    created_at: datetime
    updated_at: datetime | None
    user: UserResponse | None = None
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


CommentResponse.model_rebuild()

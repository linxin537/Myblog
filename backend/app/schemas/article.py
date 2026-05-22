from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse
from app.schemas.auth import UserResponse

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    summary: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    is_draft: bool = True
    is_pinned: bool = False

class ArticleCreate(ArticleBase):
    tag_ids: list[int] = []

class ArticleUpdate(ArticleBase):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None
    tag_ids: list[int] | None = None

class ArticleResponse(ArticleBase):
    id: int
    html_content: str | None
    author_id: int
    view_count: int
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    
    author: UserResponse | None = None
    category: CategoryResponse | None = None
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}

class ArticleListResponse(BaseModel):
    id: int
    title: str
    summary: str | None
    cover_image: str | None
    author_id: int
    view_count: int
    is_draft: bool
    is_pinned: bool
    published_at: datetime | None
    created_at: datetime

    author: UserResponse | None = None
    category: CategoryResponse | None = None
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}

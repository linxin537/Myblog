from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/tags", tags=["标签"])

@router.get("", response_model=dict)
async def get_tags(db: AsyncSession = Depends(get_db)):
    stmt = select(Tag).where(Tag.deleted_at.is_(None)).order_by(Tag.id.desc())
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return success_response(data=[TagResponse.model_validate(t).model_dump() for t in tags])

@router.post("", response_model=dict)
async def create_tag(
    req: TagCreate, 
    current_user: User = Depends(require_role(UserRole.admin, UserRole.author)),
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(select(Tag).where(Tag.name == req.name, Tag.deleted_at.is_(None)))
    if existing.scalar_one_or_none():
        return error_response(1001, "标签已存在")
        
    tag = Tag(**req.model_dump())
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return success_response(data=TagResponse.model_validate(tag).model_dump())

@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: int,
    req: TagUpdate,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id, Tag.deleted_at.is_(None)))
    tag = result.scalar_one_or_none()
    if not tag:
        return error_response(1002, "标签不存在")
        
    if req.name and req.name != tag.name:
        existing = await db.execute(select(Tag).where(Tag.name == req.name, Tag.deleted_at.is_(None)))
        if existing.scalar_one_or_none():
            return error_response(1001, "标签名称已存在")
            
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)
        
    await db.flush()
    await db.refresh(tag)
    return success_response(data=TagResponse.model_validate(tag).model_dump())

@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id, Tag.deleted_at.is_(None)))
    tag = result.scalar_one_or_none()
    if not tag:
        return error_response(1002, "标签不存在")
        
    tag.deleted_at = datetime.utcnow()
    await db.flush()
    return success_response(message="已删除")

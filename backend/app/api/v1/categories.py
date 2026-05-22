from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/categories", tags=["分类"])

@router.get("", response_model=dict)
async def get_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.deleted_at.is_(None)).order_by(Category.sort_order.asc(), Category.id.desc())
    result = await db.execute(stmt)
    categories = result.scalars().all()
    return success_response(data=[CategoryResponse.model_validate(c).model_dump() for c in categories])

@router.post("", response_model=dict)
async def create_category(
    req: CategoryCreate, 
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(select(Category).where(Category.name == req.name, Category.deleted_at.is_(None)))
    if existing.scalar_one_or_none():
        return error_response(1001, "分类名称已存在")
        
    category = Category(**req.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return success_response(data=CategoryResponse.model_validate(category).model_dump())

@router.put("/{category_id}", response_model=dict)
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.deleted_at.is_(None)))
    category = result.scalar_one_or_none()
    if not category:
        return error_response(1002, "分类不存在")
        
    if req.name and req.name != category.name:
        existing = await db.execute(select(Category).where(Category.name == req.name, Category.deleted_at.is_(None)))
        if existing.scalar_one_or_none():
            return error_response(1001, "分类名称已存在")
            
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
        
    await db.flush()
    await db.refresh(category)
    return success_response(data=CategoryResponse.model_validate(category).model_dump())

@router.delete("/{category_id}", response_model=dict)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.deleted_at.is_(None)))
    category = result.scalar_one_or_none()
    if not category:
        return error_response(1002, "分类不存在")
        
    category.deleted_at = datetime.utcnow()
    await db.flush()
    return success_response(message="已删除")

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.article import Article
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user

router = APIRouter(tags=["评论"])


def _build_comment_response(comment: Comment) -> dict:
    return CommentResponse.model_validate(comment).model_dump()


@router.get("/articles/{article_id}/comments")
async def get_comments(
    article_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    if not result.scalar_one_or_none():
        return error_response(1004, "文章不存在")

    count_stmt = (
        select(func.count())
        .select_from(Comment)
        .where(
            Comment.article_id == article_id,
            Comment.parent_id.is_(None),
            Comment.deleted_at.is_(None),
        )
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.user),
            selectinload(Comment.replies).selectinload(Comment.user),
        )
        .where(
            Comment.article_id == article_id,
            Comment.parent_id.is_(None),
            Comment.deleted_at.is_(None),
        )
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    comments = result.unique().scalars().all()

    for c in comments:
        c.replies.sort(key=lambda r: r.created_at)

    return {
        "code": 0,
        "message": "ok",
        "data": [_build_comment_response(c) for c in comments],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.post("/articles/{article_id}/comments")
async def create_comment(
    article_id: int,
    req: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    if not result.scalar_one_or_none():
        return error_response(1004, "文章不存在")

    if req.parent_id:
        parent_result = await db.execute(
            select(Comment).where(
                Comment.id == req.parent_id,
                Comment.article_id == article_id,
                Comment.parent_id.is_(None),
                Comment.deleted_at.is_(None),
            )
        )
        if not parent_result.scalar_one_or_none():
            return error_response(1004, "父评论不存在")

    comment = Comment(
        content=req.content,
        article_id=article_id,
        user_id=current_user.id,
        parent_id=req.parent_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    stmt = (
        select(Comment)
        .options(selectinload(Comment.user), selectinload(Comment.replies))
        .where(Comment.id == comment.id)
    )
    result = await db.execute(stmt)
    comment = result.scalar_one()

    return success_response(data=_build_comment_response(comment))


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    req: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.deleted_at.is_(None))
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return error_response(1004, "评论不存在")

    if comment.user_id != current_user.id:
        return error_response(1003, "无权修改此评论")

    comment.content = req.content
    await db.flush()
    await db.refresh(comment)

    stmt = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )
    result = await db.execute(stmt)
    comment = result.scalar_one()

    return success_response(data=_build_comment_response(comment))


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.deleted_at.is_(None))
    )
    comment = result.scalar_one_or_none()
    if not comment:
        return error_response(1004, "评论不存在")

    if comment.user_id != current_user.id and current_user.role != UserRole.admin:
        return error_response(1003, "无权删除此评论")

    comment.deleted_at = datetime.utcnow()
    await db.flush()
    return success_response(message="已删除")

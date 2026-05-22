from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.article import Article, article_likes, article_favorites
from app.models.comment import Comment
from app.schemas.auth import UserResponse, UpdateUserRequest
from app.schemas.article import ArticleListResponse
from app.schemas.password import UserProfileResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response(data=UserResponse.model_validate(current_user).model_dump())


@router.put("/me", response_model=dict)
async def update_me(
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.avatar is not None:
        current_user.avatar = req.avatar
    if req.bio is not None:
        current_user.bio = req.bio
    await db.flush()
    await db.refresh(current_user)
    return success_response(data=UserResponse.model_validate(current_user).model_dump())


@router.get("/me/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    article_count = (await db.execute(
        select(func.count(Article.id)).where(
            Article.author_id == current_user.id,
            Article.is_draft == False,
            Article.deleted_at.is_(None),
        )
    )).scalar() or 0

    draft_count = (await db.execute(
        select(func.count(Article.id)).where(
            Article.author_id == current_user.id,
            Article.is_draft == True,
            Article.deleted_at.is_(None),
        )
    )).scalar() or 0

    views_row = (await db.execute(
        select(func.coalesce(func.sum(Article.view_count), 0)).where(
            Article.author_id == current_user.id,
            Article.is_draft == False,
            Article.deleted_at.is_(None),
        )
    )).scalar() or 0

    # Likes received on user's articles
    like_count = (await db.execute(
        select(func.count()).select_from(article_likes).join(
            Article, article_likes.c.article_id == Article.id
        ).where(
            Article.author_id == current_user.id,
            Article.deleted_at.is_(None),
        )
    )).scalar() or 0

    # Favorites on user's articles
    fav_count = (await db.execute(
        select(func.count()).select_from(article_favorites).join(
            Article, article_favorites.c.article_id == Article.id
        ).where(
            Article.author_id == current_user.id,
            Article.deleted_at.is_(None),
        )
    )).scalar() or 0

    comment_count = (await db.execute(
        select(func.count()).select_from(Comment).join(
            Article, Comment.article_id == Article.id
        ).where(
            Article.author_id == current_user.id,
            Article.deleted_at.is_(None),
            Comment.deleted_at.is_(None),
        )
    )).scalar() or 0

    return success_response(data={
        "total_articles": article_count,
        "total_drafts": draft_count,
        "total_views": views_row,
        "total_likes": like_count,
        "total_favorites": fav_count,
        "total_comments": comment_count,
    })


@router.get("/{username}/profile")
async def get_user_profile(
    username: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == username, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        return error_response(1004, "用户不存在")

    # 统计
    stats_result = await db.execute(
        select(func.count(Article.id), func.coalesce(func.sum(Article.view_count), 0))
        .where(Article.author_id == user.id, Article.is_draft == False, Article.deleted_at.is_(None))
    )
    article_count, total_views = stats_result.one()

    # 文章列表
    stmt = (
        select(Article)
        .options(selectinload(Article.tags))
        .where(Article.author_id == user.id, Article.is_draft == False, Article.deleted_at.is_(None))
        .order_by(Article.published_at.desc(), Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    articles_result = await db.execute(stmt)
    articles = articles_result.scalars().all()

    profile = {
        **UserProfileResponse.model_validate(user).model_dump(),
        "article_count": article_count or 0,
        "total_views": total_views or 0,
        "articles": [ArticleListResponse.model_validate(a).model_dump() for a in articles],
    }

    return success_response(data=profile)

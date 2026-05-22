from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.article import Article, article_tags
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/articles", tags=["文章"])


def _build_article_list_response(article: Article) -> dict:
    return ArticleListResponse.model_validate(article).model_dump()


def _build_article_response(article: Article) -> dict:
    return ArticleResponse.model_validate(article).model_dump()


@router.get("")
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category_id: int | None = Query(None),
    tag_id: int | None = Query(None),
    is_draft: bool | None = Query(None),
    search: str | None = Query(None),
    current_user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.category),
        selectinload(Article.tags),
    )

    # 未登录只看已发布；已登录看自己的全部 + 别人的已发布
    if current_user:
        stmt = stmt.where(
            (Article.deleted_at.is_(None))
            & (
                (Article.is_draft == False)
                | ((Article.is_draft == True) & (Article.author_id == current_user.id))
            )
        )
    else:
        stmt = stmt.where(Article.deleted_at.is_(None), Article.is_draft == False)

    if category_id:
        stmt = stmt.where(Article.category_id == category_id)
    if is_draft is not None:
        stmt = stmt.where(Article.is_draft == is_draft)
    if tag_id:
        stmt = stmt.where(Article.tags.any(Tag.id == tag_id))

    if search:
        stmt = stmt.where(
            text("MATCH(articles.title, articles.content) AGAINST(:kw IN BOOLEAN MODE)")
            .bindparams(kw=f"+{search}")
        )

    # 计数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Article.is_pinned.desc(), Article.published_at.desc(), Article.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    articles = result.scalars().all()

    return {
        "code": 0,
        "message": "ok",
        "data": [_build_article_list_response(a) for a in articles],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/{article_id}")
async def get_article(
    article_id: int,
    current_user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        return error_response(1004, "文章不存在")

    if article.is_draft and (not current_user or current_user.id != article.author_id):
        return error_response(1003, "无权查看此草稿")

    # 增加浏览计数
    article.view_count += 1
    await db.flush()

    return success_response(data=_build_article_response(article))


@router.post("")
async def create_article(
    req: ArticleCreate,
    current_user: User = Depends(require_role(UserRole.admin, UserRole.author)),
    db: AsyncSession = Depends(get_db),
):
    article = Article(
        title=req.title,
        content=req.content,
        summary=req.summary,
        cover_image=req.cover_image,
        author_id=current_user.id,
        category_id=req.category_id,
        is_draft=req.is_draft,
        is_pinned=req.is_pinned,
    )

    if not req.is_draft:
        article.published_at = datetime.utcnow()

    if req.tag_ids:
        result = await db.execute(
            select(Tag).where(Tag.id.in_(req.tag_ids), Tag.deleted_at.is_(None))
        )
        tags = result.scalars().all()
        article.tags = list(tags)

    db.add(article)
    await db.flush()
    await db.refresh(article)

    # 重新加载关联
    stmt = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id == article.id)
    )
    article = (await db.execute(stmt)).scalar_one()

    return success_response(data=_build_article_response(article))


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    req: ArticleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Article)
        .options(selectinload(Article.tags))
        .where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        return error_response(1004, "文章不存在")

    if article.author_id != current_user.id and current_user.role != UserRole.admin:
        return error_response(1003, "无权修改此文章")

    update_data = req.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    was_draft = article.is_draft
    for key, value in update_data.items():
        setattr(article, key, value)

    # 从草稿变为发布
    if was_draft and not article.is_draft and not article.published_at:
        article.published_at = datetime.utcnow()

    if tag_ids is not None:
        result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids), Tag.deleted_at.is_(None))
        )
        article.tags = list(result.scalars().all())

    await db.flush()
    await db.refresh(article)

    # 重新加载关联
    stmt = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id == article.id)
    )
    article = (await db.execute(stmt)).scalar_one()

    return success_response(data=_build_article_response(article))


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        return error_response(1004, "文章不存在")

    if article.author_id != current_user.id and current_user.role != UserRole.admin:
        return error_response(1003, "无权删除此文章")

    article.deleted_at = datetime.utcnow()
    await db.flush()
    return success_response(message="已删除")

import time
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func, text, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.article import Article, article_tags, article_likes, article_favorites
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user, require_role
from app.services import log_action

router = APIRouter(prefix="/articles", tags=["文章"])

# IP 防刷：{(article_id, ip): timestamp}
_view_records: dict[tuple[int, str], float] = {}


async def _enrich_social_data(articles: list[Article], current_user: User | None, db: AsyncSession) -> None:
    """为文章列表补充点赞/收藏计数和当前用户状态"""
    if not articles:
        return
    article_ids = [a.id for a in articles]

    # 批量查询点赞数
    like_counts = {}
    like_rows = await db.execute(
        select(article_likes.c.article_id, func.count())
        .where(article_likes.c.article_id.in_(article_ids))
        .group_by(article_likes.c.article_id)
    )
    for article_id, count in like_rows:
        like_counts[article_id] = count

    # 批量查询收藏数
    fav_counts = {}
    fav_rows = await db.execute(
        select(article_favorites.c.article_id, func.count())
        .where(article_favorites.c.article_id.in_(article_ids))
        .group_by(article_favorites.c.article_id)
    )
    for article_id, count in fav_rows:
        fav_counts[article_id] = count

    # 当前用户的点赞/收藏状态
    user_likes = set()
    user_favs = set()
    if current_user:
        likes_result = await db.execute(
            select(article_likes.c.article_id).where(
                article_likes.c.user_id == current_user.id,
                article_likes.c.article_id.in_(article_ids),
            )
        )
        user_likes = {row[0] for row in likes_result}

        favs_result = await db.execute(
            select(article_favorites.c.article_id).where(
                article_favorites.c.user_id == current_user.id,
                article_favorites.c.article_id.in_(article_ids),
            )
        )
        user_favs = {row[0] for row in favs_result}

    for a in articles:
        a.like_count = like_counts.get(a.id, 0)
        a.favorite_count = fav_counts.get(a.id, 0)
        a.is_liked = a.id in user_likes
        a.is_favorited = a.id in user_favs


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

    await _enrich_social_data(articles, current_user, db)

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


@router.get("/favorites")
async def get_my_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav_sub = select(article_favorites.c.article_id).where(
        article_favorites.c.user_id == current_user.id
    ).subquery()

    count_stmt = select(func.count()).select_from(Article).where(
        Article.id.in_(select(fav_sub)),
        Article.deleted_at.is_(None),
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.category),
            selectinload(Article.tags),
        )
        .where(Article.id.in_(select(fav_sub)), Article.deleted_at.is_(None))
        .order_by(Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()

    await _enrich_social_data(articles, current_user, db)

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


def _should_count_view(article_id: int, ip: str, author_id: int, current_user: User | None) -> bool:
    """判断是否应该增加浏览计数"""
    if current_user and current_user.id == author_id:
        return False
    key = (article_id, ip)
    now = time.time()
    if key in _view_records and now - _view_records[key] < 86400:
        return False
    _view_records[key] = now
    # 定期清理过期记录
    if len(_view_records) > 10000:
        _view_records.clear()
    return True


@router.get("/{article_id}")
async def get_article(
    article_id: int,
    request: Request,
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

    # 增加浏览计数（防刷）
    ip = request.client.host if request.client else "unknown"
    if _should_count_view(article_id, ip, article.author_id, current_user):
        await db.execute(
            update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
        )
        await db.flush()
        await db.refresh(article)

    await _enrich_social_data([article], current_user, db)

    return success_response(data=_build_article_response(article))


@router.post("")
async def create_article(
    req: ArticleCreate,
    request: Request,
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

    await log_action(db, action="create_article", user_id=current_user.id,
                     target_type="article", target_id=article.id, request=request)

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
    request: Request,
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

    await log_action(db, action="delete_article", user_id=current_user.id,
                     target_type="article", target_id=article_id, request=request)

    return success_response(message="已删除")


async def _get_like_count(article_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(article_likes).where(article_likes.c.article_id == article_id)
    )
    return result.scalar() or 0


async def _get_favorite_count(article_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(article_favorites).where(article_favorites.c.article_id == article_id)
    )
    return result.scalar() or 0


@router.post("/{article_id}/like")
async def toggle_like(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    if not result.scalar_one_or_none():
        return error_response(1004, "文章不存在")

    existing = await db.execute(
        select(article_likes).where(
            article_likes.c.user_id == current_user.id,
            article_likes.c.article_id == article_id,
        )
    )
    if existing.first():
        await db.execute(
            article_likes.delete().where(
                article_likes.c.user_id == current_user.id,
                article_likes.c.article_id == article_id,
            )
        )
        liked = False
    else:
        await db.execute(
            article_likes.insert().values(user_id=current_user.id, article_id=article_id)
        )
        liked = True

    await db.flush()
    count = await _get_like_count(article_id, db)
    return success_response(data={"liked": liked, "count": count})


@router.post("/{article_id}/favorite")
async def toggle_favorite(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    if not result.scalar_one_or_none():
        return error_response(1004, "文章不存在")

    existing = await db.execute(
        select(article_favorites).where(
            article_favorites.c.user_id == current_user.id,
            article_favorites.c.article_id == article_id,
        )
    )
    if existing.first():
        await db.execute(
            article_favorites.delete().where(
                article_favorites.c.user_id == current_user.id,
                article_favorites.c.article_id == article_id,
            )
        )
        favorited = False
    else:
        await db.execute(
            article_favorites.insert().values(user_id=current_user.id, article_id=article_id)
        )
        favorited = True

    await db.flush()
    count = await _get_favorite_count(article_id, db)
    return success_response(data={"favorited": favorited, "count": count})



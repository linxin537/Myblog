from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.article import Article
from fastapi.responses import Response

router = APIRouter(tags=["sitemap"])


@router.get("/sitemap.xml")
async def sitemap(request: Request, db: AsyncSession = Depends(get_db)):
    site_url = str(request.base_url).rstrip("/")

    result = await db.execute(
        select(Article.id, Article.published_at, Article.updated_at)
        .where(Article.deleted_at.is_(None), Article.is_draft == False)
        .order_by(Article.published_at.desc())
    )
    articles = result.all()

    urls = [
        f"""  <url>
    <loc>{site_url}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
    ]

    for article_id, published_at, updated_at in articles:
        lastmod = (updated_at or published_at).strftime("%Y-%m-%d") if (updated_at or published_at) else ""
        urls.append(
            f"""  <url>
    <loc>{site_url}/article/{article_id}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""

    return Response(content=xml, media_type="application/xml")

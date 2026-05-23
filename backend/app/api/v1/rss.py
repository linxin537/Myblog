from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.article import Article
from fastapi.responses import Response

router = APIRouter(tags=["rss"])


@router.get("/rss.xml")
async def rss_feed(request: Request, db: AsyncSession = Depends(get_db)):
    site_url = str(request.base_url).rstrip("/")

    result = await db.execute(
        select(Article)
        .options(selectinload(Article.author))
        .where(Article.deleted_at.is_(None), Article.is_draft == False)
        .order_by(Article.published_at.desc())
        .limit(30)
    )
    articles = result.scalars().all()

    items_xml = []
    for article in articles:
        url = f"{site_url}/article/{article.id}"
        pub_date = (article.published_at or article.created_at).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        description = article.summary or (
            article.content[:500] + "..." if len(article.content) > 500 else article.content
        )
        author_name = article.author.username if article.author else "Unknown"
        items_xml.append(
            f"""    <item>
      <title><![CDATA[{article.title}]]></title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <description><![CDATA[{description}]]></description>
      <pubDate>{pub_date}</pubDate>
      <author>{author_name}</author>
    </item>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>个人博客</title>
    <link>{site_url}</link>
    <description>个人日常记录与博客</description>
    <language>zh-CN</language>
    <atom:link href="{site_url}/api/v1/rss.xml" rel="self" type="application/rss+xml"/>
{"".join(items_xml)}
  </channel>
</rss>"""

    return Response(content=xml, media_type="application/rss+xml")

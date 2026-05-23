# 博客功能增强 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为博客平台新增 RSS Feed、通知中心、密码重置、阅读时长估算、代码高亮改进、SEO 元标签 + Sitemap 共 6 项功能

**Architecture:** 遵循现有 FastAPI + Vue 3 分层架构。后端新增 4 个 API 模块（rss/sitemap/notifications + auth 扩展），3 个数据模型（notification/password_reset_token + article_likes 表已存在）。前端新增 3 个组件/视图（NotificationBell/ResetPassword + composables），修改现有组件以集成新功能。

**Tech Stack:** Python 3.11+ / FastAPI + SQLAlchemy (async) + MySQL 8.0 | Vue 3 + TypeScript + Naive UI + GSAP

---

## 文件结构

```
后端 (backend/app/)
├── models/
│   ├── notification.py        ← 新：通知模型
│   └── password_reset.py      ← 新：密码重置令牌模型
├── api/v1/
│   ├── rss.py                 ← 新：RSS Feed 端点
│   ├── sitemap.py             ← 新：Sitemap 端点
│   ├── notifications.py       ← 新：通知 CRUD API
│   ├── auth.py                ← 改：新增忘记密码 + 重置密码端点
│   ├── comments.py            ← 改：通知触发
│   ├── articles.py            ← 改：点赞通知触发
│   └── __init__.py
├── schemas/
│   └── notification.py        ← 新：通知 Pydantic schemas
└── main.py                    ← 改：注册新路由 + 模型导入

前端 (frontend/src/)
├── api/
│   ├── notifications.ts       ← 新：通知 API 调用
│   └── auth.ts                ← 改：新增忘记密码 + 重置密码 API
├── stores/
│   └── notification.ts        ← 新：通知 Pinia store
├── composables/
│   ├── useReadingTime.ts      ← 新：阅读时长计算
│   └── useCodeHighlight.ts    ← 新：代码高亮主题切换 + 复制
├── components/
│   ├── NotificationBell.vue   ← 新：通知铃铛组件
│   ├── ArticleCard.vue        ← 改：显示阅读时长
│   └── AppLayout.vue          ← 改：导航栏 + 通知铃铛 + RSS link
├── views/
│   ├── ArticleDetail.vue      ← 改：阅读时长 + 代码高亮改进
│   ├── LoginView.vue          ← 改：添加"忘记密码"链接
│   ├── ResetPassword.vue      ← 新：密码重置页面
│   ├── HomeView.vue           ← 改：SEO useHead
│   └── ProfileView.vue        ← 改：SEO useHead
├── router/
│   └── index.ts               ← 改：新增 /reset-password 路由
├── index.html                 ← 改：默认 meta 标签
└── main.ts                    ← 改：注册 @unhead/vue
```

---

### Task 1: 阅读时长估算 (Composable)

**Files:**
- Create: `frontend/src/composables/useReadingTime.ts`
- Modify: `frontend/src/components/ArticleCard.vue`
- Modify: `frontend/src/views/ArticleDetail.vue`

- [ ] **Step 1: 创建 useReadingTime composable**

```ts
// frontend/src/composables/useReadingTime.ts

export function useReadingTime(content: string): number {
  const chineseChars = (content.match(/[一-鿿]/g) || []).length
  const words = (content.match(/[a-zA-Z]+/g) || []).length
  return Math.max(1, Math.ceil((chineseChars + words) / 400))
}

export function formatReadingTime(content: string): string {
  return `约 ${useReadingTime(content)} 分钟`
}
```

- [ ] **Step 2: 在 ArticleCard 中显示阅读时长**

Read `ArticleCard.vue` to locate the meta line showing date + view_count.

```vue
<!-- In the meta line of ArticleCard.vue, add after view_count: -->
<span> · {{ formatReadingTime(article.summary || '') }}</span>
```

Add import:
```ts
import { formatReadingTime } from '../composables/useReadingTime'
```

- [ ] **Step 3: 在 ArticleDetail 中显示阅读时长**

Read `ArticleDetail.vue` to locate the meta line (around line 229).

```vue
<!-- Add after view_count in the meta line: -->
<span> · {{ formatReadingTime(article.content || '') }}</span>
```

Add import:
```ts
import { formatReadingTime } from '../composables/useReadingTime'
```

- [ ] **Step 4: 验证前端编译**

```bash
cd frontend && npm run build -- --emptyOutDir false
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/composables/useReadingTime.ts frontend/src/components/ArticleCard.vue frontend/src/views/ArticleDetail.vue
git commit -m "feat: add reading time estimate to article card and detail" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: RSS Feed (Backend)

**Files:**
- Create: `backend/app/api/v1/rss.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 RSS 端点**

```python
# backend/app/api/v1/rss.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.article import Article
from app.models.user import User
from fastapi.responses import Response

router = APIRouter(tags=["rss"])


@router.get("/rss.xml")
async def rss_feed(request: Request, db: AsyncSession = Depends(get_db)):
    settings = __import__("app.config", fromlist=["get_settings"]).get_settings()
    site_url = str(request.base_url).rstrip("/")

    result = await db.execute(
        select(Article)
        .options(
            __import__("sqlalchemy.orm", fromlist=["selectinload"]).selectinload(Article.author),
        )
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
```

- [ ] **Step 2: 在 main.py 注册路由**

```python
# In backend/app/main.py, add near the other imports:
from app.api.v1.rss import router as rss_router

# Add near the other include_router calls:
app.include_router(rss_router, prefix="/api/v1")
```

- [ ] **Step 3: 在 AppLayout 添加 RSS 发现链接**

Read `AppLayout.vue` to check how the head is managed. Since it's a Vue SPA without SSR, add the link to `index.html` instead:

```html
<!-- In frontend/index.html, inside <head>, add: -->
<link rel="alternate" type="application/rss+xml" title="RSS" href="/api/v1/rss.xml">
```

- [ ] **Step 4: 启动后端并测试 RSS 端点**

```bash
# Start backend and test:
curl http://127.0.0.1:8000/api/v1/rss.xml
```

Expected: XML response with `<rss>` root element containing `<channel>` and `<item>` elements.

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/v1/rss.py backend/app/main.py frontend/index.html
git commit -m "feat: add RSS 2.0 feed endpoint at /api/v1/rss.xml" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: Sitemap (Backend)

**Files:**
- Create: `backend/app/api/v1/sitemap.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 Sitemap 端点**

```python
# backend/app/api/v1/sitemap.py

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
{"".join(urls)}
</urlset>"""

    return Response(content=xml, media_type="application/xml")
```

- [ ] **Step 2: 在 main.py 注册路由**

```python
# In backend/app/main.py, add near the other imports:
from app.api.v1.sitemap import router as sitemap_router

# Add near the other include_router calls:
app.include_router(sitemap_router, prefix="/api/v1")
```

- [ ] **Step 3: 创建 robots.txt**

```text
User-agent: *
Allow: /

Sitemap: http://localhost:8000/api/v1/sitemap.xml
```

Save to `frontend/public/robots.txt`

- [ ] **Step 4: 测试 Sitemap 端点**

```bash
curl http://127.0.0.1:8000/api/v1/sitemap.xml
```

Expected: XML response with `<urlset>` root element containing `<url>` items.

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/v1/sitemap.py backend/app/main.py frontend/public/robots.txt
git commit -m "feat: add sitemap.xml endpoint" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: SEO 元标签 (Frontend)

**Files:**
- Install: `@unhead/vue` package
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/views/HomeView.vue`
- Modify: `frontend/src/views/ArticleDetail.vue`
- Modify: `frontend/src/views/ProfileView.vue`
- Modify: `frontend/index.html`

- [ ] **Step 1: 安装 @unhead/vue**

```bash
cd frontend && npm install @unhead/vue
```

- [ ] **Step 2: 在 main.ts 注册 Unhead plugin**

Read `frontend/src/main.ts` to find the app creation code.

```ts
// In frontend/src/main.ts, add:
import { createHead } from '@unhead/vue'

const head = createHead()

// After app creation, before mount:
app.use(head)
```

- [ ] **Step 3: 修改 index.html 默认 meta**

Read `frontend/index.html` to add default OG tags:

```html
<!-- In <head>, add after <title>: -->
<meta property="og:title" content="个人博客">
<meta property="og:description" content="个人日常记录与博客">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
```

- [ ] **Step 4: 在 HomeView 添加 SEO**

Read `frontend/src/views/HomeView.vue` to find the `<script setup>` block, add:

```ts
import { useHead } from '@unhead/vue'

useHead({
  title: '个人博客',
  meta: [
    { name: 'description', content: '个人日常记录与博客平台' },
    { property: 'og:title', content: '个人博客' },
  ],
})
```

- [ ] **Step 5: 在 ArticleDetail 添加 SEO**

Read `frontend/src/views/ArticleDetail.vue` to find the `<script setup>` block, add after article load:

```ts
import { useHead } from '@unhead/vue'
import { computed } from 'vue'

// After article.value is available, compute SEO:
const seoDescription = computed(() =>
  article.value?.summary || article.value?.content?.slice(0, 200) || ''
)

// Add a watch or include in the template - since useHead is reactive,
// use it with computed refs:
useHead({
  title: () => article.value?.title || '文章详情',
  meta: [
    { name: 'description', content: seoDescription.value },
    { property: 'og:title', content: () => article.value?.title || '' },
    { property: 'og:description', content: seoDescription.value },
    { property: 'og:type', content: 'article' },
    { name: 'twitter:card', content: 'summary' },
  ],
})
```

- [ ] **Step 6: 在 ProfileView 添加 SEO**

Read `frontend/src/views/ProfileView.vue` to add:

```ts
import { useHead } from '@unhead/vue'

// Inside <script setup>, add:
useHead({
  title: () => `${route.params.username} 的个人主页`,
  meta: [
    { name: 'description', content: () => `${route.params.username} 的个人主页` },
  ],
})
```

Note: `route` is already imported from `vue-router` in ProfileView.

- [ ] **Step 7: 验证前端编译**

```bash
cd frontend && npm run build -- --emptyOutDir false
```

Expected: Build succeeds with no errors.

- [ ] **Step 8: 提交**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/main.ts frontend/index.html frontend/src/views/HomeView.vue frontend/src/views/ArticleDetail.vue frontend/src/views/ProfileView.vue
git commit -m "feat: add SEO meta tags with @unhead/vue" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: 代码高亮改进 (Frontend)

**Files:**
- Create: `frontend/src/composables/useCodeHighlight.ts`
- Modify: `frontend/src/views/ArticleDetail.vue`

- [ ] **Step 1: 创建 useCodeHighlight composable**

```ts
// frontend/src/composables/useCodeHighlight.ts

import { onMounted, onUnmounted } from 'vue'

function getThemeLink(theme: string): HTMLLinkElement | null {
  return document.querySelector(`link[data-highlight-theme="${theme}"]`) as HTMLLinkElement | null
}

function toggleThemeLink(current: HTMLLinkElement | null, targetTheme: string) {
  if (!current) return
  current.disabled = true

  let target = getThemeLink(targetTheme)
  if (!target) {
    target = document.createElement('link')
    target.rel = 'stylesheet'
    target.dataset.highlightTheme = targetTheme
    target.href = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/${targetTheme}.min.css`
    document.head.appendChild(target)
  }
  target.disabled = false
}

export function useCodeHighlight() {
  function updateTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
    const lightLink = getThemeLink('github')
    const darkLink = getThemeLink('github-dark')

    if (isDark) {
      if (lightLink) lightLink.disabled = true
      toggleThemeLink(darkLink, 'github-dark')
    } else {
      if (darkLink) darkLink.disabled = true
      toggleThemeLink(lightLink, 'github')
    }
  }

  const observer = new MutationObserver(updateTheme)

  onMounted(() => {
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    updateTheme()
  })

  onUnmounted(() => {
    observer.disconnect()
  })

  function copyCodeBlock(block: HTMLElement) {
    const code = block.textContent || ''
    navigator.clipboard.writeText(code).catch(() => {})
  }

  return { copyCodeBlock, updateTheme }
}
```

- [ ] **Step 2: 修改 ArticleDetail 添加复制按钮**

Read `ArticleDetail.vue` to find where rendered HTML is displayed.

After marked rendering of the HTML content, the rendered HTML is displayed in a `<div>` with `v-html`. In the `onMounted` or `nextTick` after content renders, add event listeners:

```ts
// In ArticleDetail.vue <script setup>, add:
import { useCodeHighlight } from '../composables/useCodeHighlight'

const { copyCodeBlock } = useCodeHighlight()

// In onMounted or after article load, add copy buttons to code blocks:
function attachCopyButtons() {
  document.querySelectorAll('.article-content pre').forEach((pre) => {
    if (pre.querySelector('.copy-btn')) return
    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.textContent = '复制'
    btn.onclick = () => {
      copyCodeBlock(pre)
      btn.textContent = '已复制'
      setTimeout(() => { btn.textContent = '复制' }, 1500)
    }
    pre.appendChild(btn)
  })
}

// Call attachCopyButtons() in nextTick after article content is rendered.
// In the watch or nextTick where content is set:
import { nextTick } from 'vue'
// After setting the inner HTML:
await nextTick()
attachCopyButtons()
```

Add styles in the scoped `<style>`:

```css
.article-content pre {
  position: relative;
}
.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  font-size: 12px;
  background: rgba(128, 128, 128, 0.2);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: inherit;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.article-content pre:hover .copy-btn {
  opacity: 1;
}
```

- [ ] **Step 3: 验证前端视觉效果**

```bash
cd frontend && npm run dev
```

Open the dev server, navigate to an article with code blocks, verify:
- Code blocks show copy button on hover
- Switching dark/light mode changes code theme

- [ ] **Step 4: 提交**

```bash
git add frontend/src/composables/useCodeHighlight.ts frontend/src/views/ArticleDetail.vue
git commit -m "feat: improve code highlighting with dark mode sync and copy button" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: 通知中心 - 数据模型 + API (Backend)

**Files:**
- Create: `backend/app/models/notification.py`
- Create: `backend/app/schemas/notification.py`
- Create: `backend/app/api/v1/notifications.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 Notification 模型**

```python
# backend/app/models/notification.py

from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    comment = "comment"
    reply = "reply"
    like = "like"
    system = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
```

- [ ] **Step 2: 创建 Notification schemas**

```python
# backend/app/schemas/notification.py

from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    content: str
    link: str | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 3: 创建 Notification API 端点**

```python
# backend/app/api/v1/notifications.py

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import success_response, error_response
from app.api.deps import get_current_user

router = APIRouter(tags=["notifications"])


@router.get("/notifications")
async def list_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id
        )
    )
    total = total.scalar() or 0

    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = result.scalars().all()

    return success_response(
        data={
            "items": [
                NotificationResponse.model_validate(n) for n in notifications
            ],
            "total": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    )


@router.put("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        return error_response(1004, "通知不存在")

    notification.is_read = True
    await db.flush()
    return success_response(data=NotificationResponse.model_validate(notification))


@router.put("/notifications/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()
    return success_response()


@router.get("/notifications/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    count = result.scalar() or 0
    return success_response(data={"count": count})
```

- [ ] **Step 4: 在 main.py 注册模型和路由**

```python
# In backend/app/main.py, add near the other model imports:
from app.models.notification import Notification  # noqa: F401

# Add near the other router imports:
from app.api.v1.notifications import router as notifications_router

# Add near the other include_router calls:
app.include_router(notifications_router, prefix="/api/v1")
```

- [ ] **Step 5: 启动后端测试通知 API**

```bash
# Start backend, then test with a logged-in user:
curl -X GET http://127.0.0.1:8000/api/v1/notifications -c cookies.txt -b cookies.txt
```

Expected: `{"code": 0, "message": "success", "data": {"items": [], "total": 0, "total_pages": 1}}`

- [ ] **Step 6: 提交**

```bash
git add backend/app/models/notification.py backend/app/schemas/notification.py backend/app/api/v1/notifications.py backend/app/main.py
git commit -m "feat: add notification model and API endpoints" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: 通知触发 (Backend — 评论 + 点赞)

**Files:**
- Modify: `backend/app/api/v1/comments.py`
- Modify: `backend/app/api/v1/articles.py`

- [ ] **Step 1: 在评论创建时触发通知**

Add notification creation in `backend/app/api/v1/comments.py`.

First, add imports at the top of the file:
```python
# At the top of comments.py, add to existing imports:
from app.models.notification import Notification, NotificationType
```

Then in `create_comment` function, after `await db.flush()` of the comment and before the re-query:

```python
# 通知文章作者
article_result = await db.execute(
    select(Article).where(Article.id == article_id)
)
article_obj = article_result.scalar_one()

if article_obj.author_id != current_user.id:
    notification = Notification(
        user_id=article_obj.author_id,
        type=NotificationType.comment,
        title="新评论",
        content=f"{current_user.username} 评论了你的文章《{article_obj.title}》",
        link=f"/article/{article_id}",
    )
    db.add(notification)

# 如果是回复，通知父评论作者
if req.parent_id:
    parent_result = await db.execute(
        select(Comment).where(Comment.id == req.parent_id)
    )
    parent_comment = parent_result.scalar_one()
    if parent_comment.user_id != current_user.id:
        reply_notification = Notification(
            user_id=parent_comment.user_id,
            type=NotificationType.reply,
            title="新回复",
            content=f"{current_user.username} 回复了你的评论",
            link=f"/article/{article_id}",
        )
        db.add(reply_notification)
```

- [ ] **Step 2: 在点赞时触发通知**

Modify `backend/app/api/v1/articles.py` `toggle_like` function.

First, add imports at the top of the file:
```python
# At the top of articles.py, add to existing imports:
from app.models.notification import Notification, NotificationType
```

Then in `toggle_like`, after the article_likes insert:

```python
# In toggle_like, after the article_likes insert (when liked=True):
if liked:
    article_result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article_obj = article_result.scalar_one()
    if article_obj.author_id != current_user.id:
        notification = Notification(
            user_id=article_obj.author_id,
            type=NotificationType.like,
            title="新的赞",
            content=f"{current_user.username} 赞了你的文章《{article_obj.title}》",
            link=f"/article/{article_id}",
        )
        db.add(notification)
```

- [ ] **Step 3: 测试通知触发**

```bash
# Start backend, login as reader, create a comment on another author's article,
# then check notifications endpoint:
curl -X GET http://127.0.0.1:8000/api/v1/notifications -c cookies.txt -b cookies.txt
```

Expected: Notification appears in the list.

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/v1/comments.py backend/app/api/v1/articles.py
git commit -m "feat: trigger notifications on comment and like events" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: 通知中心 - 前端 (NotificationBell + Store)

**Files:**
- Create: `frontend/src/stores/notification.ts`
- Create: `frontend/src/api/notifications.ts`
- Create: `frontend/src/components/NotificationBell.vue`
- Modify: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: 创建通知 API 模块**

```ts
// frontend/src/api/notifications.ts

import client from './client'
import type { ApiResponse } from '../types/api'

export interface NotificationItem {
  id: number
  type: 'comment' | 'reply' | 'like' | 'system'
  title: string
  content: string
  link: string | null
  is_read: boolean
  created_at: string
}

export interface NotificationListData {
  items: NotificationItem[]
  total: number
  total_pages: number
}

export function getNotifications(page = 1, pageSize = 20) {
  return client.get<ApiResponse<NotificationListData>>('/notifications', {
    params: { page, page_size: pageSize },
  })
}

export function markRead(notificationId: number) {
  return client.put<ApiResponse<NotificationItem>>(`/notifications/${notificationId}/read`)
}

export function markAllRead() {
  return client.put<ApiResponse>('/notifications/read-all')
}

export function getUnreadCount() {
  return client.get<ApiResponse<{ count: number }>>('/notifications/unread-count')
}
```

- [ ] **Step 2: 创建通知 Pinia Store**

```ts
// frontend/src/stores/notification.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getNotifications,
  getUnreadCount,
  markRead,
  markAllRead,
  type NotificationItem,
} from '../api/notifications'
import { useAuthStore } from './auth'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)
  const items = ref<NotificationItem[]>([])
  let pollingTimer: ReturnType<typeof setInterval> | null = null

  async function fetchUnreadCount() {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return
    try {
      const res = await getUnreadCount()
      unreadCount.value = res.data.data?.count ?? 0
    } catch {
      // Silently fail
    }
  }

  async function fetchItems(page = 1) {
    try {
      const res = await getNotifications(page)
      items.value = res.data.data?.items ?? []
    } catch {
      // Silently fail
    }
  }

  async function readOne(id: number) {
    try {
      await markRead(id)
      const item = items.value.find((n) => n.id === id)
      if (item) item.is_read = true
      await fetchUnreadCount()
    } catch {
      // Silently fail
    }
  }

  async function readAll() {
    try {
      await markAllRead()
      items.value.forEach((n) => (n.is_read = true))
      unreadCount.value = 0
    } catch {
      // Silently fail
    }
  }

  function startPolling() {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return
    fetchUnreadCount()
    pollingTimer = setInterval(fetchUnreadCount, 60000)
  }

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  return { unreadCount, items, fetchUnreadCount, fetchItems, readOne, readAll, startPolling, stopPolling }
})
```

- [ ] **Step 3: 创建 NotificationBell 组件**

```vue
<!-- frontend/src/components/NotificationBell.vue -->

<script setup lang="ts">
import { NIcon, NBadge, NPopover, NButton, NList, NListItem, NText, NEmpty, NScrollbar } from 'naive-ui'
import { NotificationsOutline } from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notification'
import { onMounted } from 'vue'

const router = useRouter()
const store = useNotificationStore()

onMounted(async () => {
  await store.fetchItems()
})

function handleOpen() {
  store.fetchItems()
}

async function handleClick(item: { id: number; link: string | null }) {
  await store.readOne(item.id)
  if (item.link) router.push(item.link)
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = Date.now()
  const diff = now - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  return `${days} 天前`
}
</script>

<template>
  <NPopover
    trigger="click"
    placement="bottom-end"
    :style="{ padding: 0, width: '360px' }"
    @update:show="handleOpen"
  >
    <template #trigger>
      <NButton quaternary circle>
        <template #icon>
          <NBadge :value="store.unreadCount" :max="99" :show="store.unreadCount > 0">
            <NIcon :component="NotificationsOutline" :size="22" />
          </NBadge>
        </template>
      </NButton>
    </template>

    <div :style="{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid var(--color-hairline-soft)' }">
      <NText strong :style="{ fontSize: '14px' }">通知</NText>
      <NButton
        v-if="store.unreadCount > 0"
        text
        size="tiny"
        :style="{ fontSize: '12px', color: 'var(--color-primary)' }"
        @click="store.readAll()"
      >
        全部标为已读
      </NButton>
    </div>

    <NScrollbar :style="{ maxHeight: '400px' }">
      <NEmpty v-if="store.items.length === 0" description="暂无通知" :style="{ padding: '32px' }" />
      <NList v-else>
        <NListItem
          v-for="item in store.items"
          :key="item.id"
          :style="{
            padding: '12px 16px',
            cursor: 'pointer',
            background: item.is_read ? 'transparent' : 'var(--color-surface-soft)',
            opacity: item.is_read ? 0.7 : 1,
          }"
          @click="handleClick(item)"
        >
          <div>
            <NText :style="{ fontSize: '14px', fontWeight: item.is_read ? 400 : 600 }">
              {{ item.title }}
            </NText>
            <br>
            <NText :depth="3" :style="{ fontSize: '13px' }">{{ item.content }}</NText>
            <br>
            <NText :depth="3" :style="{ fontSize: '11px' }">{{ formatTime(item.created_at) }}</NText>
          </div>
        </NListItem>
      </NList>
    </NScrollbar>
  </NPopover>
</template>
```

- [ ] **Step 4: 在 AppLayout 集成通知铃铛**

Modify `AppLayout.vue`:

```vue
<!-- After the import lines, add: -->
import NotificationBell from './NotificationBell.vue'
import { useNotificationStore } from '../stores/notification'

// In <script setup>, add after auth declaration:
const notifStore = useNotificationStore()
notifStore.startPolling()
```

In the right-side nav (after the dark mode toggle button, before the username), add:

```vue
<NotificationBell v-if="auth.isLoggedIn" />
```

- [ ] **Step 5: 验证前端编译和功能**

```bash
cd frontend && npm run build -- --emptyOutDir false
```

Expected: Build succeeds.

- [ ] **Step 6: 提交**

```bash
git add frontend/src/api/notifications.ts frontend/src/stores/notification.ts frontend/src/components/NotificationBell.vue frontend/src/components/AppLayout.vue
git commit -m "feat: add notification bell with polling and popover panel" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: 密码重置 - 数据模型 + API (Backend)

**Files:**
- Create: `backend/app/models/password_reset.py`
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 PasswordResetToken 模型**

```python
# backend/app/models/password_reset.py

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- [ ] **Step 2: 在 auth.py 添加忘记密码和重置密码端点**

Read `backend/app/api/v1/auth.py` to find the router definition and existing imports.

Add new imports at the top of the file:
```python
# Add to existing imports:
import hashlib
import os
from datetime import timedelta
from app.models.password_reset import PasswordResetToken
from app.schemas.password import ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import _utcnow, hash_password
```

Then add two new endpoints at the end of the file:

```python

@router.post("/auth/forgot-password")
async def forgot_password(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == req.email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if user:
        token = hashlib.sha256(os.urandom(32)).hexdigest()
        expires_at = _utcnow() + timedelta(hours=24)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(reset_token)
        await db.flush()

        # Dev mode: print reset link to console
        reset_url = f"http://localhost:5173/reset-password?token={token}"
        print(f"\n{'='*60}")
        print(f"密码重置链接 (dev): {reset_url}")
        print(f"{'='*60}\n")

    # Always return success to prevent user enumeration
    return success_response(message="如果邮箱已注册，重置链接已发送")


@router.post("/auth/reset-password")
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    now = _utcnow()
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == req.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > now,
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        return error_response(1021, "无效或过期的重置令牌")

    result = await db.execute(
        select(User).where(User.id == reset_token.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return error_response(1021, "无效或过期的重置令牌")

    user.hashed_password = hash_password(req.new_password)
    reset_token.used = True
    await db.flush()

    return success_response(message="密码已重置")
```

- [ ] **Step 3: 创建 Pydantic schemas for password**

```python
# backend/app/schemas/password.py

from pydantic import BaseModel, Field


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=100)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)
```

- [ ] **Step 4: 在 main.py 注册模型**

```python
# In backend/app/main.py, add near the other model imports:
from app.models.password_reset import PasswordResetToken  # noqa: F401
```

- [ ] **Step 5: 测试忘记密码端点**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

Expected: `{"code": 0, "message": "如果邮箱已注册，重置链接已发送", "data": null}`. Check console for reset URL.

- [ ] **Step 6: 提交**

```bash
git add backend/app/models/password_reset.py backend/app/schemas/password.py backend/app/api/v1/auth.py backend/app/main.py
git commit -m "feat: add password reset flow with token-based reset" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 10: 密码重置 - 前端页面

**Files:**
- Create: `frontend/src/views/ResetPassword.vue`
- Modify: `frontend/src/views/LoginView.vue`
- Modify: `frontend/src/api/auth.ts`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 添加密码重置 API**

In `frontend/src/api/auth.ts`, add:

```ts
export function forgotPassword(email: string) {
  return client.post<ApiResponse>('/auth/forgot-password', { email })
}

export function resetPassword(token: string, newPassword: string) {
  return client.post<ApiResponse>('/auth/reset-password', { token, new_password: newPassword })
}
```

- [ ] **Step 2: 创建 ResetPassword 视图**

```vue
<!-- frontend/src/views/ResetPassword.vue -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NText, NResult, useMessage } from 'naive-ui'
import { forgotPassword, resetPassword } from '../api/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const token = ref(route.query.token as string || '')
const email = ref('')
const newPassword = ref('')
const sent = ref(false)
const done = ref(false)
const submitting = ref(false)

async function handleForgot() {
  submitting.value = true
  try {
    const res = await forgotPassword(email.value)
    if (res.data.code === 0) sent.value = true
  } catch {
    // ignore
  }
  submitting.value = false
}

async function handleReset() {
  submitting.value = true
  try {
    const res = await resetPassword(token.value, newPassword.value)
    if (res.data.code === 0) {
      done.value = true
      message.success('密码已重置，请重新登录')
    } else {
      message.error(res.data.message || '重置失败')
    }
  } catch {
    message.error('网络错误')
  }
  submitting.value = false
}
</script>

<template>
  <div :style="{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-canvas)' }">
    <div :style="{ width: '380px', padding: '40px', background: 'var(--color-canvas)', borderRadius: '14px', border: '1px solid var(--color-hairline-soft)', boxShadow: 'var(--shadow-card)' }">
      <!-- Done state -->
      <NResult
        v-if="done"
        status="success"
        title="密码重置成功"
        description="请使用新密码登录"
      >
        <template #footer>
          <NButton type="primary" @click="router.push('/login')" :style="{ borderRadius: '8px' }">
            前往登录
          </NButton>
        </template>
      </NResult>

      <!-- Token mode: reset password -->
      <template v-else-if="token">
        <NText strong :style="{ fontSize: '22px', display: 'block', marginBottom: '24px' }">设置新密码</NText>
        <NForm>
          <NFormItem label="新密码">
            <NInput
              v-model:value="newPassword"
              type="password"
              placeholder="至少 6 位"
              :style="{ borderRadius: '8px' }"
            />
          </NFormItem>
          <NButton
            type="primary"
            block
            :loading="submitting"
            :disabled="newPassword.length < 6"
            @click="handleReset"
            :style="{ borderRadius: '8px' }"
          >
            重置密码
          </NButton>
        </NForm>
      </template>

      <!-- Email mode: request reset -->
      <template v-else-if="!sent">
        <NText strong :style="{ fontSize: '22px', display: 'block', marginBottom: '24px' }}">忘记密码</NText>
        <NForm>
          <NFormItem label="注册邮箱">
            <NInput
              v-model:value="email"
              placeholder="请输入注册邮箱"
              :style="{ borderRadius: '8px' }"
            />
          </NFormItem>
          <NButton
            type="primary"
            block
            :loading="submitting"
            :disabled="!email"
            @click="handleForgot"
            :style="{ borderRadius: '8px' }"
          >
            发送重置链接
          </NButton>
        </NForm>
      </template>

      <!-- Sent state -->
      <template v-else>
        <NText strong :style="{ fontSize: '18px', display: 'block', marginBottom: '16px', textAlign: 'center' }">请检查控制台日志</NText>
        <NText depth="3" :style="{ textAlign: 'center', display: 'block', marginBottom: '24px' }">
          开发模式下，重置链接已打印到后端控制台。请复制链接在浏览器中打开。
        </NText>
        <NButton block @click="router.push('/login')" :style="{ borderRadius: '8px' }">
          返回登录
        </NButton>
      </template>
    </div>
  </div>
</template>
```

- [ ] **Step 3: 在 LoginView 添加"忘记密码"链接**

Read `LoginView.vue` to find the login form area. Add after the login button:

```vue
<!-- After the login button NFormItem, add: -->
<div :style="{ textAlign: 'right', marginTop: '8px' }">
  <NButton text :style="{ fontSize: '13px', color: 'var(--color-muted)' }" @click="router.push('/reset-password')">
    忘记密码？
  </NButton>
</div>
```

- [ ] **Step 4: 添加路由**

In `frontend/src/router/index.ts`, add to the routes array:

```ts
{
  path: '/reset-password',
  name: 'reset-password',
  component: () => import('../views/ResetPassword.vue'),
  meta: { guest: true },
},
```

- [ ] **Step 5: 验证前端编译**

```bash
cd frontend && npm run build -- --emptyOutDir false
```

- [ ] **Step 6: 提交**

```bash
git add frontend/src/views/ResetPassword.vue frontend/src/views/LoginView.vue frontend/src/api/auth.ts frontend/src/router/index.ts
git commit -m "feat: add password reset frontend page and flow" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 11: 最终验证与调试

**Files:** (No new files, verify all changes)

- [ ] **Step 1: 启动完整应用**

```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

- [ ] **Step 2: 验证阅读时长**

Navigate to homepage → confirm reading time displays on article cards.
Navigate to an article → confirm reading time in detail meta.

- [ ] **Step 3: 验证 RSS Feed**

Navigate to `http://localhost:8000/api/v1/rss.xml` → confirm valid XML with articles.

- [ ] **Step 4: 验证 Sitemap**

Navigate to `http://localhost:8000/api/v1/sitemap.xml` → confirm valid XML.

- [ ] **Step 5: 验证代码高亮**

Open an article with code blocks → hover over code block → confirm copy button appears. Switch dark/light mode → confirm code theme changes.

- [ ] **Step 6: 验证通知中心**

Login as a user → comment on someone else's article → login as article author → confirm notification bell shows unread count → click to open panel → click notification to navigate.

- [ ] **Step 7: 验证密码重置**

Visit `/login` → click "忘记密码？" → enter email → check backend console for reset link → paste link → enter new password → login with new password.

- [ ] **Step 8: 验证 SEO 元标签**

Navigate to an article → view page source → confirm `<title>`, `<meta name="description">`, `og:title`, `og:description` are present.

- [ ] **Step 9: 提交**

```bash
git add -A
git commit -m "chore: final verification, all 6 features integrated" -m "Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

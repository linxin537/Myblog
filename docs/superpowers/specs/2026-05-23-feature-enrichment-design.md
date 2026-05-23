# 博客功能增强设计规格

**日期**: 2026-05-23
**状态**: Draft
**范围**: 全栈新增 6 项功能

---

## 概述

在现有博客平台基础上新增 6 项功能，补齐基础设施短板，提升读者体验和互动粘性。阅读计数已有完整实现，无需开发。

---

## 功能清单

| # | 功能 | 类型 | 复杂度 |
|---|---|---|---|
| 1 | RSS Feed | 新增 | 小 |
| 2 | 代码高亮改进 | 改进 | 极小 |
| 3 | 通知中心 | 新增 | 中 |
| 4 | 阅读时长估算 | 新增 | 极小 |
| 5 | SEO 元标签 + Sitemap | 新增 | 小 |
| 6 | 密码重置 | 新增 | 中 |

---

## 1. RSS Feed

### 端点

`GET /api/v1/rss.xml`

### 实现

后端用字符串模板生成标准 RSS 2.0 XML，取最近 30 篇已发布文章。文章内容取 `summary` 字段作为 `<description>`，无摘要则截取前 500 字符。

### 前端

`AppLayout.vue` 的 `<head>` 添加发现链接：
```html
<link rel="alternate" type="application/rss+xml" title="RSS" href="/api/v1/rss.xml">
```

### 文件

- 新增 `backend/app/api/v1/rss.py`
- 修改 `backend/app/main.py`（注册路由）
- 修改 `frontend/src/components/AppLayout.vue`

---

## 2. 代码高亮改进

### 现状

ByteMD 编辑器已有 `@bytemd/plugin-highlight`，文章详情页已有 `marked` + `highlight.js`。

### 改进点

1. **暗色模式跟随** — 目前代码块主题不跟随站点暗色模式，需根据 `[data-theme]` 动态切换 highlight.js 样式
2. **代码块复制按钮** — 每个 `<pre>` 块 hover 时显示复制按钮

### 文件

- 修改 `frontend/src/views/ArticleDetail.vue` — 主题监听 + 复制按钮
- 新增 `frontend/src/composables/useCodeHighlight.ts` — 封装主题切换和复制逻辑

---

## 3. 通知中心

### 数据模型

新表 `notifications`：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | 自增 |
| user_id | int FK | 接收通知的用户 |
| type | enum | `comment`, `reply`, `like`, `system` |
| title | varchar(255) | 通知标题 |
| content | text | 通知正文 |
| link | varchar(255) | 点击跳转链接 |
| is_read | bool | 默认 false |
| created_at | datetime | 通知时间 |

### 触发时机

- 评论文章 → 通知文章作者（type=comment）
- 回复评论 → 通知被回复者（type=reply）
- 点赞文章 → 通知文章作者（type=like）

通知创建代码写在对应的业务 API 中，不引入消息队列。

### API 端点

- `GET /api/v1/notifications` — 通知列表（分页，需登录）
- `PUT /api/v1/notifications/{id}/read` — 标记单条已读
- `PUT /api/v1/notifications/read-all` — 全部标为已读
- `GET /api/v1/notifications/unread-count` — 未读数

### 前端

- 导航栏右侧新增铃铛图标 + `NBadge` 未读数字红点
- 点击弹出 `NPopover` 面板，展示最近通知列表
- 点击通知跳转对应文章，并标记已读
- Pinia store 管理未读计数，每 60s 轮询

### 文件

- 新增 `backend/app/models/notification.py`
- 新增 `backend/app/api/v1/notifications.py`
- 修改 `backend/app/main.py`（注册路由）
- 修改 `backend/app/api/v1/comments.py`（创建评论/回复时触发通知）
- 修改 `backend/app/api/v1/articles.py`（点赞时触发通知）
- 新增 `frontend/src/components/NotificationBell.vue`
- 新增 `frontend/src/api/notifications.ts`
- 新增 `frontend/src/stores/notification.ts`
- 修改 `frontend/src/components/AppLayout.vue`

---

## 4. 阅读时长估算

### 实现

纯前端 composable，中文约 400 字/分钟：

```ts
// composables/useReadingTime.ts
export function useReadingTime(content: string): number {
  const chineseChars = (content.match(/[一-鿿]/g) || []).length
  const words = (content.match(/[a-zA-Z]+/g) || []).length
  return Math.max(1, Math.ceil((chineseChars + words) / 400))
}
```

### 展示位置

- `ArticleCard` — 日期和阅读量旁加 `· 约 N 分钟`
- `ArticleDetail` — 标题下方元数据区域

### 文件

- 新增 `frontend/src/composables/useReadingTime.ts`
- 修改 `frontend/src/components/ArticleCard.vue`
- 修改 `frontend/src/views/ArticleDetail.vue`

---

## 5. SEO 元标签 + Sitemap

### 5.1 动态元标签

引入 `@unhead/vue`（3KB gzipped），在各页面视图调用 `useHead()`。

**首页**：站点名称 + 副标题
**文章详情**：文章标题 + 摘要 + Open Graph + Twitter Card
**用户主页**：用户名 + 简介

### 5.2 Sitemap

`GET /api/v1/sitemap.xml` — 标准 sitemap XML，包含首页和所有已发布文章 URL。

`public/robots.txt` 添加 sitemap 链接。

### 文件

- 安装 `@unhead/vue`
- 修改 `frontend/src/main.ts`（注册 plugin）
- 修改 `frontend/src/views/HomeView.vue`
- 修改 `frontend/src/views/ArticleDetail.vue`
- 修改 `frontend/src/views/ProfileView.vue`
- 修改 `frontend/index.html`
- 新增 `backend/app/api/v1/sitemap.py`
- 修改 `backend/app/main.py`

---

## 6. 密码重置

### 数据模型

新表 `password_reset_tokens`：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | int PK | 自增 |
| user_id | int FK | 关联用户 |
| token | varchar(128) | SHA256 随机令牌 |
| expires_at | datetime | 24 小时过期 |
| used | bool | 默认 false |

### 流程

```
登录页 → "忘记密码" → 输入邮箱
  → 后端生成 token，打印重置链接到控制台日志
  → 用户访问 /reset-password?token=xxx
  → 输入新密码 → 完成
```

### API 端点

- `POST /api/v1/auth/forgot-password` — `{ email }`，生成 token。不管邮箱是否存在都返回成功（防用户枚举）
- `POST /api/v1/auth/reset-password` — `{ token, new_password }`，验证 token + 更新密码

### 邮件策略

开发阶段不接入真实邮件服务，重置链接打印到控制台日志。后续可扩展 SMTP。

### 前端

- `LoginView.vue` 添加"忘记密码？"链接
- 新增 `ResetPassword.vue` — 两步 UI：输入邮箱 → 提示已发送；带 token → 输入新密码

### 文件

- 新增 `backend/app/models/password_reset.py`
- 修改 `backend/app/api/v1/auth.py`（新增两个端点）
- 修改 `backend/app/main.py`（注册模型和路由）
- 修改 `frontend/src/views/LoginView.vue`
- 新增 `frontend/src/views/ResetPassword.vue`
- 修改 `frontend/src/api/auth.ts`
- 修改 `frontend/src/router/index.ts`

---

## 路由变更

新增路由：
```ts
{ path: '/reset-password', name: 'reset-password', component: () => import('../views/ResetPassword.vue'), meta: { guest: true } }
```

---

## 非功能需求

- 所有新增 API 遵循现有规范：`/api/v1/` 前缀，`{ code, message, data }` 统一响应
- 通知、密码重置令牌在数据库迁移脚本中创建
- 前端保持 Airbnb 极简风格，复用现有 CSS 变量
- 所有改动遵循 Claude.md 中的项目架构约定

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

个人日常记录与博客平台（Personal Daily Journal & Blog Platform）。前后端分离的 SPA 架构。需求规格见 `个人博客平台需求规格说明书_v2.0.docx`。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite + Naive UI |
| 后端 | Python 3.11+ / FastAPI + SQLAlchemy (async, aiomysql) |
| 数据库 | MySQL 8.0 |
| 认证 | python-jose (JWT) + passlib (bcrypt) |
| 文件存储 | 本地文件系统 `/static/uploads/` |

## 常用命令

```bash
# 后端启动
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端开发
cd frontend && npm run dev   # Vite dev server → http://localhost:5173
```

## 架构要点

- **API 规范**: RESTful，URL 版本化 `/api/v1/`，统一响应格式 `{code, message, data}`，标准错误码 0=成功，1001-9999=各类错误
- **分页约定**: `page` + `page_size` 参数，响应含 `total` / `total_pages`
- **认证**: JWT 双 token — Access Token (2h) + Refresh Token (7d)，HttpOnly Cookie 存储，token 轮换
- **角色**: Admin / Author / Reader，路由守卫 + API 权限校验
- **软删除**: 所有核心表使用 `deleted_at` 字段
- **搜索**: Phase 1 使用 MySQL FULLTEXT，后续迁移 Elasticsearch

## 核心数据表

`users`, `articles`, `categories`, `tags`, `article_tags`, `files`, `comments`, `likes`, `favorites`, `audit_logs`

## 开发阶段

1. **Phase 1 (MVP)**: 脚手架搭建、注册登录、JWT 认证、登录锁定、毛玻璃主题、暗色模式、统一响应
2. **Phase 2 (核心博客)**: 文章 CRUD、Markdown 编辑器 (Milkdown/ByteMD)、分类标签、图片上传+缩略图、全文搜索、草稿自动保存、软删除
3. **Phase 3 (社交与管理)**: 管理后台、用户角色管理、个人主页、浏览计数、评论、点赞收藏、审计日志、密码重置
4. **Phase 4 (增强)**: 编辑器改进、微信绑定、搜索建议、动画优化、限流、快捷键
5. **Phase 5 (部署)**: 本地部署文档、启动脚本、可选 Docker Compose、备份脚本

## UI 设计

Glassmorphism（毛玻璃）风格，Naive UI 组件库，支持亮/暗色主题切换。

# Apple 极简风格重设计 - 设计规格

> 日期：2026-05-22 | 状态：已确认

## 概述

对博客平台前端进行全面视觉升级，从当前毛玻璃风格转向 Apple 式极简设计。不改动功能逻辑，只改造样式、布局、动效。

### 设计原则

- **克制**：中性色为主，强调色只在关键操作点出现
- **留白**：充足间距，让内容呼吸
- **精致**：排版层次分明，动效自然流畅
- **一致**：所有页面遵循统一设计语言

---

## 一、色彩体系

### 主色调

| 角色 | 色值 | 用途 |
|---|---|---|
| 页面背景 | `#f5f5f7` | 全局背景（亮色模式） |
| 页面背景（暗色） | `#1d1d1f` | 全局背景（暗色模式） |
| 卡片背景 | `#ffffff` | 卡片、表单、面板 |
| 卡片背景（暗色） | `#2d2d2f` | 暗色模式卡片 |
| 主文字 | `#1d1d1f` | 标题、正文 |
| 次要文字 | `#86868b` | 日期、描述、辅助信息 |
| 弱文字 | `#aeaeb2` | 占位符、禁用态 |
| 强调色 | `#0071e3` | 链接、主按钮、选中态 |
| 强调色 hover | `#0077ed` | 按钮悬停 |
| 分割线 | `rgba(0,0,0,0.08)` | 细线分割、Header 底边 |
| 分割线（暗色） | `rgba(255,255,255,0.08)` | 暗色模式分割线 |

### 阴影体系

| 层级 | 阴影值 | 用途 |
|---|---|---|
| 极淡 | `0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)` | 默认卡片 |
| 浅 | `0 4px 12px rgba(0,0,0,0.06)` | 卡片 hover |
| 中 | `0 8px 30px rgba(0,0,0,0.08)` | 下拉菜单、弹窗 |
| 深 | `0 20px 60px rgba(0,0,0,0.12)` | 模态框 |

### 放弃

- 移除 `.glass` / `.glass-strong` 毛玻璃效果
- 移除 `glassmorphism.css` 中所有与毛玻璃相关的 CSS 变量
- 暗色模式不做毛玻璃，统一用纯色卡片

---

## 二、排版体系

### 字号层级

| 层级 | 字号 | 行高 | 字重 | 用途 |
|---|---|---|---|---|
| Hero 标题 | 48px | 1.1 | 600 | 首页大标题 |
| Hero 副标题 | 21px | 1.4 | 400 | 首页描述 |
| 页面标题 | 32px | 1.25 | 600 | 各页面顶部标题 |
| 区块标题 | 24px | 1.3 | 600 | 区块分隔标题 |
| 卡片标题 | 20px | 1.35 | 600 | 文章列表标题 |
| 正文 | 17px | 1.6 | 400 | 文章内容 |
| 辅助文字 | 14px | 1.5 | 400 | 日期、阅读量 |
| 小标签 | 12px | 1.4 | 500 | 分类、标签 |

### 字体栈

```
"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont,
"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif
```

代码字体保持 `"JetBrains Mono", "Fira Code", monospace`。

### 间距体系（4px 基数）

| Token | 值 | 用途 |
|---|---|---|
| xs | 4px | 紧密元素 |
| sm | 8px | 相关元素 |
| md | 16px | 组件内边距 |
| lg | 24px | 卡片之间 |
| xl | 32px | 区块之间 |
| 2xl | 48px | 大区块分隔 |
| 3xl | 64px | Hero 上下间距 |
| 4xl | 96px | 极端留白 |

### 页面宽度

| 页面类型 | 最大宽度 |
|---|---|
| 文章列表 | 720px |
| 文章详情 | 780px |
| 表单页面 | 460px |
| 宽页面（设置/管理） | 1080px |

---

## 三、布局与组件

### Header

- 固定高度 44px，纯白背景 `#ffffff`（暗色 `#2d2d2f`）
- 底部 0.5px 分割线 `rgba(0,0,0,0.08)`
- 滚动时：`backdrop-filter: saturate(180%) blur(20px)` + 背景微透明 `rgba(255,255,255,0.85)`
- Logo 左对齐，导航项居中，操作按钮右侧
- 当前路由导航项有底部指示器（2px 强调色短线或小圆点）

### Hero 区域（首页）

- 纯浅灰背景 `#f5f5f7`
- 高度约 320px，垂直居中内容
- 结构：大标题（1-2 行）+ 副标题 + 搜索框
- 标题逐字/逐行淡入动画（`fade-in-up`，0.6s cubic-bezier）
- 不设背景图，保持极简

### 卡片（替代 GlassCard）

- 纯白背景 + 极淡阴影，圆角 16px
- 内边距 28px
- hover：`translateY(-2px)` + 阴影从"极淡"过渡到"浅"
- 过渡：`0.3s cubic-bezier(0.25, 0.1, 0.25, 1)`
- 封面图：顶对齐填满卡片宽度，`border-radius: 16px 16px 0 0`

### 按钮

- 主按钮：`#0071e3` 背景，白色文字，圆角 980px（全圆角胶囊），高度 38px
- 次级按钮：`#f5f5f7` 背景，hover 变 `#e8e8ed`
- 文字按钮：无背景，hover 时淡灰底色 `rgba(0,0,0,0.04)`
- 危险操作：红色 `#ff3b30`

### 登录/注册卡片

- 纯白卡片 + 细阴影，内边距 48px
- 宽度 440px，垂直居中
- Segment tabs 保持使用 Naive UI 原生

### 表单控件

- 输入框：圆角 10px，高度 40px，边框 `rgba(0,0,0,0.12)`
- 聚焦态：边框变为 `#0071e3`，加 2px 外发光 `0 0 0 2px rgba(0,113,227,0.15)`
- Label：字号 14px，字重 500，颜色 `#1d1d1f`

### 空状态/错误页

- 简洁图标（使用 Ionicons 的 document-text-outline 等）
- 主文字 "还没有文章" 字号 21px，颜色 `#1d1d1f`
- 副说明（如有）字号 15px，颜色 `#86868b`
- 操作按钮在文字下方 24px

---

## 四、动效

### 页面入场

| 元素 | 动画 | 时长 | 缓动 |
|---|---|---|---|
| Hero 标题 | fade-in-up (20px → 0) | 0.6s | cubic-bezier(0.25, 0.1, 0.25, 1) |
| Hero 副标题 | fade-in-up (16px → 0) | 0.6s | 同上，延迟 0.1s |
| 文章卡片 | fade-in-up + stagger (每张 +60ms) | 0.4s | ease-out |
| 页面切换 | opacity + translateY(8px) | 0.3s | ease |

### 微交互

| 元素 | 效果 | 时长 | 缓动 |
|---|---|---|---|
| 卡片 hover | translateY(-2px) + 阴影加深 | 0.3s | cubic-bezier(0.25, 0.1, 0.25, 1) |
| 按钮 hover | 背景色过渡 | 0.2s | ease |
| 链接 hover | 下划线滑入（background-size 动画） | 0.25s | ease |
| 输入框聚焦 | 边框 + 外发光过渡 | 0.2s | ease |
| 导航项选中 | 底部指示器宽度过渡 | 0.25s | cubic-bezier |

### 点赞/收藏

- 保留 `like-bounce`（缩放弹性 400ms）
- 保留 `star-spin`（旋转 500ms）
- 统一缓动为 `cubic-bezier(0.34, 1.56, 0.64, 1)`

### Header 滚动

- 从透明纯白过渡到毛玻璃纯白
- transition: `background 0.3s ease, backdrop-filter 0.3s ease`

---

## 五、实现范围

### 需要改动的文件

**全局样式（2 文件）：**
- `frontend/src/styles/glassmorphism.css` → 重命名为 `theme.css`，完全重写
- `frontend/src/styles/transitions.css` → 更新缓动和关键帧

**入口（1 文件）：**
- `frontend/src/App.vue` → 更新 Naive UI 主题覆盖（色值、圆角）

**布局组件（1 文件）：**
- `frontend/src/components/AppLayout.vue` → Header 重设计

**通用组件（3 文件）：**
- `frontend/src/components/GlassCard.vue` → 从毛玻璃改为纯白卡片
- `frontend/src/components/ArticleCard.vue` → 卡片样式 + 排版重构
- `frontend/src/components/ArticleCardSkeleton.vue` → 骨架屏样式适配

**页面（10 文件）：**
- `frontend/src/views/HomeView.vue` → 新增 Hero 区域
- `frontend/src/views/LoginView.vue` → 卡片样式重构
- `frontend/src/views/ArticleDetail.vue` → 排版优化
- `frontend/src/views/ArticleEditor.vue` → 编辑器样式适配
- `frontend/src/views/ProfileView.vue` → 排版优化
- `frontend/src/views/FavoritesView.vue` → 与文章列表一致
- `frontend/src/views/DraftsView.vue` → 与文章列表一致
- `frontend/src/views/SettingsView.vue` → 排版优化
- `frontend/src/views/admin/*.vue` → 4 个管理页面适配

**其他组件（6 文件）：**
- `frontend/src/components/CommentSection.vue`
- `frontend/src/components/CommentItem.vue`
- `frontend/src/components/LikeButton.vue`
- `frontend/src/components/FavoriteButton.vue`
- `frontend/src/components/TableOfContents.vue`
- `frontend/src/components/AuthorDashboard.vue`

**入口文件（1 文件）：**
- `frontend/src/main.ts` → 更名后的 CSS 引用路径

**总计：约 25 个文件**

### 不改动

- 后端代码（FastAPI）
- API 调用逻辑
- 路由配置
- 状态管理（Pinia）
- Markdown 编辑器（ByteMD）功能
- 页面业务逻辑（只改 template 和 style）

---

## 六、验收标准

1. 所有页面在亮色/暗色模式下视觉一致、无明显瑕疵
2. Hero 区域正确显示在首页顶部，含入场动画
3. Header 滚动时有两态切换（纯白 → 毛玻璃）
4. 文章卡片 hover 有平滑抬升效果
5. 页面切换过渡流畅无闪烁
6. 所有按钮、输入框遵循新配色规范
7. 毛玻璃相关 CSS 类已完全移除
8. 不影响任何现有功能（登录、CRUD、搜索、筛选、分页）

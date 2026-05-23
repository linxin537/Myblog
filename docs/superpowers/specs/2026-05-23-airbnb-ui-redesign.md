# Airbnb 风格 UI 改版设计规格

**日期**: 2026-05-23
**状态**: Approved
**范围**: 全站前端 UI 重构

---

## 概述

将博客前端从极光玻璃主题（Aurora Glassmorphism）全面改造为 Airbnb 极简设计风格。保留暗色模式，以 Airbnb 设计语言为基础设计暗色版本。保留 Naive UI 组件库，通过 CSS 变量 + themeOverrides + 模板重构实现。

### 设计参考

基于 `DESIGN.md` 中的 Airbnb 设计系统规范（Rausch 品牌色、Inter 字体、柔和圆角、极简阴影、Photo-first 卡片）。

---

## 配色系统

### 亮色模式（`:root`）

| Token | 值 | 用途 |
|---|---|---|
| `--color-canvas` | `#ffffff` | 页面底色 |
| `--color-surface-soft` | `#f7f7f7` | 浅填充（禁用态、hover 背景） |
| `--color-surface-strong` | `#f2f2f2` | 较重填充（图标按钮底） |
| `--color-primary` | `#ff385c` | 唯一品牌色 (Rausch) |
| `--color-primary-hover` | `#e00b41` | 按下态 |
| `--color-ink` | `#222222` | 主文字色 |
| `--color-body` | `#3f3f3f` | 正文辅助色 |
| `--color-muted` | `#6a6a6a` | 次要信息色 |
| `--color-muted-soft` | `#929292` | 禁用文字色 |
| `--color-hairline` | `#dddddd` | 默认 1px 边框 |
| `--color-hairline-soft` | `#ebebeb` | 浅分割线 |
| `--color-error` | `#c13515` | 错误文字 |
| `--shadow-card` | `rgba(0,0,0,.02) 0 0 0 1px, rgba(0,0,0,.04) 0 2px 6px, rgba(0,0,0,.1) 0 4px 8px` | 唯一阴影层级 |

### 暗色模式（`[data-theme="dark"]`）

| Token | 值 |
|---|---|
| `--color-canvas` | `#141414` |
| `--color-surface-soft` | `#1e1e1e` |
| `--color-surface-strong` | `#2a2a2a` |
| `--color-primary` | `#ff5a7a` |
| `--color-primary-hover` | `#ff7a95` |
| `--color-ink` | `#e8e8e8` |
| `--color-body` | `#b0b0b0` |
| `--color-muted` | `#888888` |
| `--color-hairline` | `#333333` |
| `--color-hairline-soft` | `#2a2a2a` |
| `--shadow-card` | `rgba(0,0,0,.3) 0 0 0 1px, rgba(0,0,0,.4) 0 2px 6px, rgba(0,0,0,.5) 0 4px 8px` |

---

## 排版系统

- **字体**: Inter（Google Fonts），替代 DM Sans + Fraunces
- **font-family**: `"Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif`
- **层级**:

| 用途 | Size | Weight | Line Height |
|---|---|---|---|
| 页面主标题 (Hero h1) | 28px | 700 | 1.43 |
| 区块标题 | 20px | 600 | 1.2 |
| 卡片标题 | 16px | 600 | 1.25 |
| 正文 | 16px | 400 | 1.5 |
| 辅助信息 | 14px | 400 | 1.43 |
| 微小文本 | 12px | 400 | 1.23 |

---

## 间距与圆角

- **间距**: 4px base unit
  - xs: 4px, sm: 8px, base: 16px, lg: 24px, xl: 32px, section: 64px
- **圆角**:
  - sm (button/input): 8px
  - md (card): 14px
  - lg: 16px
  - full (pill/search): 9999px

---

## Naive UI ThemeOverrides 关键映射

### Common
- `primaryColor`: #ff385c (亮) / #ff5a7a (暗)
- `primaryColorHover`: #e00b41 / #ff7a95
- `borderRadius`: 8px
- `fontFamily`: Inter 字体栈
- `textColor1/2/3`: Ink → Body → Muted 映射

### Button
- `borderRadiusMedium`: 8px（不再 pill 形）
- `heightMedium`: 40px

### Input
- `borderRadius`: 8px
- `heightLarge`: 48px

---

## 组件改造规格

### AppLayout（导航栏）
- 白底 + 80px 高度 + 底部 1px hairline 分割线
- 导航项居中排列，活跃 tab 底部 2px Ink 下划线
- 移除 backdrop-blur 和 glass-strong class
- 暗色模式: 深灰底 + 深色分割线

### ArticleCard（文章卡片）
- Photo-first 布局: 封面图 1:1 aspect-ratio 在顶部
- 14px 圆角 + 1px hairline 边框
- Hover: 单层 shadow-card 浮起
- 无封面图时：根据文章标签匹配默认渐变色封面
- "精选"浮动徽章（类似 "Guest favorite"）
- 底部: 标题(16px/600) + 作者日期(14px muted) + 阅读量(14px muted)

### ArticleDetail（文章详情）
- 双栏布局: 内容 64% + 侧边栏 32%（sticky）
- 侧边栏: 目录 + 点赞收藏按钮
- 作者行: identicon 头像(32px) + 用户名 + 日期
- 评分区域移除（博客无评分需求）
- 评论区集成 identicon 头像

### ArticleEditor（文章编辑器）
- 表单元素直接平铺白底，无卡片包裹
- Input: 1px hairline + 8px 圆角 + 48px 高度
- Stacked label（标签在输入框上方）
- Primary 按钮: Rausch 填充 + 8px 圆角
- Secondary 按钮: 白底 + Ink 文字 + 1px Ink 边框

### LoginView（登录/注册）
- 极简居中表单，宽 360px，垂直居中
- Stacked labels + 8px 圆角输入框
- Primary 按钮全宽
- 链接用 Rausch 色
- 移除玻璃卡片包裹

### 管理后台（UserManage / CategoryManage / TagManage / AuditLogs）
- 表头: 浅灰底 + 大写标签 + 字母间距
- 行: 用户头像 28px 圆形 + 用户名
- 角色: 浅灰 pill 标签
- 状态: 彩色圆点
- 操作: Rausch 链接色
- 分页器: Airbnb 风格圆角按钮

### 个人主页 / 收藏 / 草稿 / 设置
- 统一卡片网格布局
- Tab 切换: pill 按钮组（选中=Ink 底，未选中=浅灰底）
- 表单: Stacked labels + 8px 圆角
- 空状态: 统一占位样式

---

## 新增特性

### 标签 → 默认封面映射（covers.ts）

当文章无 `cover_image` 时，根据第一个标签匹配预定义封面：

- 预置 ~15 种标签风格映射
- 每项包含: `{ gradient: string, icon: string, iconSize: string }`
- 图标占比 ~30%，渐变色块 ~70%
- 未匹配标签使用通用默认封面
- 无标签文章使用通用默认封面

### GitHub Identicon 头像系统（identicon.ts）

- 基于 `hash(username)` 确定性生成几何头像
- 5×5 网格对称图案（上下左右镜像）
- 12 色调色板
- 输出 SVG Data URI（可直接用作 `<img src>`
- 8px 圆角（匹配 Airbnb 风格）
- 头像组件优先级: 自定义上传 URL → identicon → 默认占位符
- 预生成 ~20 个视觉上不同的几何图案组合

---

## 文件变更清单

### 新建
- `frontend/src/styles/airbnb.css` — CSS 变量 + 全局重置
- `frontend/src/utils/identicon.ts` — hash 头像生成器
- `frontend/src/utils/covers.ts` — 标签封面映射表

### 修改
- `frontend/src/main.ts` — 引用 airbnb.css
- `frontend/src/App.vue` — themeOverrides 重写
- `frontend/index.html` — Google Fonts 替换
- `frontend/src/components/AppLayout.vue` — 导航栏重构
- `frontend/src/components/ArticleCard.vue` — Photo-first 卡片
- `frontend/src/components/ArticleCardSkeleton.vue` — 匹配新骨架
- `frontend/src/components/CommentItem.vue` — identicon 头像
- `frontend/src/components/CommentSection.vue` — 头像评论框
- `frontend/src/components/GlassCard.vue` — 重命名/简化
- `frontend/src/views/HomeView.vue` — 白底 Hero + 卡片网格
- `frontend/src/views/ArticleDetail.vue` — 双栏布局
- `frontend/src/views/ArticleEditor.vue` — 干净表单
- `frontend/src/views/LoginView.vue` — 极简表单
- `frontend/src/views/ProfileView.vue` — 个人主页
- `frontend/src/views/FavoritesView.vue` — 收藏页
- `frontend/src/views/DraftsView.vue` — 草稿页
- `frontend/src/views/SettingsView.vue` — 设置页
- `frontend/src/views/admin/UserManage.vue` — 用户管理
- `frontend/src/views/admin/CategoryManage.vue` — 分类管理
- `frontend/src/views/admin/TagManage.vue` — 标签管理
- `frontend/src/views/admin/AuditLogs.vue` — 审计日志

### 删除
- `frontend/src/styles/glassmorphism.css` — 退役毛玻璃样式

---

## 不变更

- Naive UI 组件库保留
- API 层不做任何修改
- 路由结构不变
- 后端不做任何修改
- 功能逻辑（认证、CRUD、评论等）不变
- 暗色模式切换开关保留

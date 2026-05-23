# 博客动效系统 + 封面图移除 设计规格

> **设计目标**: 在 Airbnb 极简风格基础上，用 GSAP 为所有页面注入大胆创意动效，同时性能保持平衡。一并移除长期无法正常工作的封面图功能。

---

## 1. 封面图功能移除

### 1.1 移除范围

| 文件 | 改动 |
|---|---|
| `src/components/ArticleCard.vue` | 删除封面区域（img + 渐变 emoji），卡片改为纯文字布局 |
| `src/views/ArticleDetail.vue` | 删除文章顶部封面图展示 |
| `src/views/ArticleEditor.vue` | 删除封面图输入框、上传按钮、图片预览、ImageUpload 弹窗 |
| `src/utils/covers.ts` | 删除文件 |
| `src/types/api.ts` | `cover_image` 字段保留但前端不再渲染 |

### 1.2 ArticleCard 新布局

移除封面后，卡片变为紧凑文字卡片：
- 分类标签 + 草稿标签（顶行）
- 标题（16px，600 粗细，最多 2 行）
- 摘要（14px，最多 2 行）
- 底行：作者 · 日期 · 阅读数
- 标签列表

卡片保持 Airbnb 风格：14px 圆角、1px 细边框、hover 阴影。

---

## 2. 动效系统总览

### 2.1 风格定位

**融合型** — 不同页面匹配不同调性：
- 首页：潮酷吸睛
- 文章详情：温暖沉浸
- 编辑器：科技流畅
- 收藏/草稿：潮酷
- 登录：品牌仪式
- 设置/主页：克制实用

### 2.2 技术栈

- **GSAP** (gsap + ScrollTrigger + Flip)
- 性能策略：优先 CSS transform/opacity，必要时用 will-change
- 低端设备降级：通过 `prefers-reduced-motion` 媒体查询静默所有非必要动画

---

## 3. 全局基础设施

### 3.1 页面过渡 (Page Transitions)

**风格 A: 淡入淡出 + 微位移**

路由跳转时：
- 离开页面：opacity 1→0，translateY 0→-8px，duration 350ms
- 进入页面：opacity 0→1，translateY 8px→0，duration 350ms
- 使用 GSAP timeline 编排，等待离开完成后再播放入场

实现位置：`App.vue` RouterView 包装层，使用 `gsap.fromTo()` 配合 Vue Router 钩子。

### 3.2 导航栏滚动变形

- 默认状态：80px 高，纯白/纯黑背景
- 滚动超过 50px：缩减至 56px，背景变为半透明毛玻璃 (`backdrop-filter: blur(12px)`)
- Logo 字号从 20px → 18px 平滑过渡
- 使用 GSAP ScrollTrigger 或 CSS transition

实现位置：`AppLayout.vue`

### 3.3 统一滚动揭示系统 (ScrollReveal)

- 所有页面的内容区域使用 GSAP ScrollTrigger
- 默认参数：从下方 30px 淡入上浮，duration 0.6s，ease `power2.out`
- 列表场景使用 stagger 0.08-0.1s 错落延迟
- 封装为可复用的 composable: `useScrollReveal(el, options)`

实现位置：新建 `src/composables/useScrollReveal.ts`

### 3.4 自定义光标 + 点击波纹

- 默认光标替换为 20px 圆形（品牌色 30% 透明 + 1px 边框）
- 悬停可点击元素时光标缩小至 12px，边框变实心
- 点击时在点击位置产生涟漪动画（圆环扩散 + 淡出，duration 0.6s）
- 使用 CSS `cursor: none` 隐藏原生光标，JS 监听 mousemove 更新位置

实现位置：新建 `src/composables/useCustomCursor.ts`，在 `App.vue` 中全局挂载

### 3.5 视差滚动层 (Parallax)

- 多速滚动效果，不同元素以不同速率响应滚动
- Hero 区背景元素：0.5x 速度
- 文章封面图：0.7x 速度
- 内容区：1x 正常速度
- 使用 GSAP ScrollTrigger 的 scrub 功能

实现位置：新建 `src/composables/useParallax.ts`

---

## 4. 页面动效矩阵

### 4.1 首页 (HomeView)

**Hero 区域 — 弹性入场 (Bounce In)**
- 标题文字：scale 0.3→1.05→0.95→1，ease `elastic.out(1, 0.5)`，duration 0.8s
- 副标题：延迟 0.3s，淡入上浮
- 搜索框：延迟 0.5s，弹性入场
- 总开场时长约 1.2s，完成后页面进入可交互状态

**卡片流 — 3D Tilt 跟随**
- 使用 GSAP 或自定义 3D transform
- 鼠标在卡片上移动时：卡片沿 X/Y 轴倾斜（max 8deg），光晕跟随鼠标位置
- 鼠标离开：弹性回弹至原位，duration 0.4s，ease `back.out(1.5)`
- 滚动入场：卡片从下方 40px 淡入，stagger 0.08s

### 4.2 文章详情 (ArticleDetail)

**沉浸联动型**
- **阅读进度条**: 顶部 2px 高细线，品牌色，随滚动从 0%→100%，GSAP ScrollTrigger scrub
- **ToC 高亮追踪**: 当前阅读章节在 ToC 中高亮 + 平滑滚动，IntersectionObserver 驱动
- **封面图视差**: 已随封面移除一同删除
- **内容揭示**: 图片和代码块进入视口时轻微淡入 + 上浮
- **评论区计数器**: 滚动到评论区时，评论数从 0 滚动动画至实际数字（duration 1s）
- **点赞粒子**: 点击点赞按钮时，从按钮位置爆发 8-12 个品牌色小圆点（使用 GSAP + 绝对定位）

### 4.3 编辑器 (ArticleEditor)

**流畅创作体验**
- 工具栏 hover：图标放大至 1.15x，弹性缓动
- 拖拽图片上传：拖入区域边框从虚线变为实线 + 品牌色光晕
- 保存成功：保存按钮有绿色波纹从中心扩散（类似 Material ripple）
- 草稿/发布切换：开关动画使用 GSAP Flip 平滑过渡
- 发布按钮：呼吸脉冲（box-shadow 扩散），提示可以发布

### 4.4 收藏 / 草稿 (FavoritesView / DraftsView)

**3D 卡片 + 滑动手势**
- 列表项复用首页的 3D Tilt 效果（轻度版，max 4deg）
- 滚动入场 stagger 0.06s
- 空状态插画有呼吸缩放动画（scale 0.98→1.02，duration 2s，loop）

### 4.5 登录 (LoginView)

**品牌仪式感**
- Logo 弹性入场（类似首页 Hero），duration 0.6s
- 表单从下方淡入，延迟 0.3s
- 输入框聚焦时：边框变为品牌色 + 外发光 box-shadow
- 登录按钮 loading 状态：脉冲动画
- 背景：两个缓慢移动的大渐变色块（blur 120px），duration 20s 循环

### 4.6 设置 / 个人主页 (SettingsView / ProfileView)

**功能即动效**（不添加装饰动画）
- 开关切换弹性：thumb 圆点有轻微缩放回弹
- 保存成功：绿色对勾弹跳 + 淡出
- 头像上传裁剪框：拖拽调整时有弹性边界反馈

---

## 5. 文件结构

```
src/
├── composables/
│   ├── useScrollReveal.ts    # 新建：滚动揭示
│   ├── useCustomCursor.ts    # 新建：自定义光标
│   └── useParallax.ts        # 新建：视差滚动
├── components/
│   ├── ArticleCard.vue       # 修改：移除封面，纯文字卡片
│   ├── AppLayout.vue         # 修改：导航栏滚动变形
│   └── DynamicCursor.vue     # 新建：光标组件
├── views/
│   ├── HomeView.vue          # 修改：Hero 弹性入场 + 3D Tilt
│   ├── ArticleDetail.vue     # 修改：阅读辅助 + 粒子点赞，移除封面图
│   ├── ArticleEditor.vue     # 修改：流畅动效，移除封面图
│   ├── LoginView.vue         # 修改：品牌仪式感入场
│   ├── FavoritesView.vue     # 修改：3D 列表项
│   ├── DraftsView.vue        # 修改：3D 列表项
│   ├── SettingsView.vue      # 修改：开关弹性
│   └── ProfileView.vue       # 修改：保存弹跳
├── styles/
│   └── transitions.css       # 替换：移除旧动效，保留骨架屏
├── utils/
│   └── covers.ts             # 删除
└── App.vue                   # 修改：页面过渡、光标挂载
```

---

## 6. 性能约束

- 所有 GSAP 动画使用 `gsap.context()` 管理，组件卸载时 `revert()` 清理
- ScrollTrigger 使用 `gsap.matchMedia()` 处理响应式断点
- 移动端（<768px）：关闭自定义光标、减弱 3D 效果（max tilt 2deg）、视差简化为 opacity 变化
- 监听 `prefers-reduced-motion: reduce`，跳过非必要动画
- 不使用 WebGL/Canvas 粒子（未选 D）

---

## 7. 测试要点

- 首页 Hero 动画在慢速网络下不会阻塞交互
- 路由切换过渡在快速连续点击时不出现视觉错乱
- 自定义光标在 Naive UI 弹窗/下拉菜单上方正确隐藏
- 移动端触摸交互不触发 tilt 效果
- ScrollTrigger 在窗口 resize 时正确重算位置
- 封面图移除后文章卡片、详情页、编辑器无残留引用

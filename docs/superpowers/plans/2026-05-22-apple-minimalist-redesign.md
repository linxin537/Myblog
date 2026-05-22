# Apple 极简风格重设计 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将博客前端从毛玻璃风格全面升级为 Apple 极简风格，覆盖色彩、排版、动效、组件。

**Architecture:** 自底向上逐层替换 — 先全局样式系统和主题变量，再布局壳体，然后通用组件，最后页面逐一适配。每层完成即可独立验证视觉效果。

**Tech Stack:** Vue 3 + TypeScript + Naive UI 2.x + 纯 CSS（无 Tailwind/SCSS）

---

### Task 1: 全局样式系统重建

**Files:**
- Create: `frontend/src/styles/theme.css`
- Modify: `frontend/src/styles/transitions.css`
- Modify: `frontend/src/main.ts:5`
- Modify: `frontend/index.html:7`

- [ ] **Step 1: 创建新的 theme.css 替代 glassmorphism.css**

```css
/* ===== Apple 极简设计 Token ===== */
:root {
  /* 背景 */
  --bg-primary: #f5f5f7;
  --bg-card: #ffffff;
  --bg-card-hover: #ffffff;
  --bg-header: rgba(255, 255, 255, 0.85);
  --bg-header-solid: #ffffff;

  /* 文字 */
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #aeaeb2;

  /* 强调 */
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --accent-glow: rgba(0, 113, 227, 0.15);

  /* 分割线 */
  --border-color: rgba(0, 0, 0, 0.08);
  --border-color-strong: rgba(0, 0, 0, 0.12);

  /* 阴影 */
  --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-card-hover: 0 4px 12px rgba(0,0,0,0.06);
  --shadow-dropdown: 0 8px 30px rgba(0,0,0,0.08);
  --shadow-modal: 0 20px 60px rgba(0,0,0,0.12);

  /* 圆角 */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 980px;
}

[data-theme="dark"] {
  --bg-primary: #1d1d1f;
  --bg-card: #2d2d2f;
  --bg-card-hover: #323234;
  --bg-header: rgba(29, 29, 31, 0.85);
  --bg-header-solid: #2d2d2f;

  --text-primary: #f5f5f7;
  --text-secondary: #a1a1a6;
  --text-tertiary: #6e6e73;

  --accent: #2997ff;
  --accent-hover: #40a9ff;
  --accent-glow: rgba(41, 151, 255, 0.2);

  --border-color: rgba(255, 255, 255, 0.08);
  --border-color-strong: rgba(255, 255, 255, 0.12);

  --shadow-card: 0 1px 3px rgba(0,0,0,0.2), 0 1px 2px rgba(0,0,0,0.16);
  --shadow-card-hover: 0 4px 12px rgba(0,0,0,0.3);
  --shadow-dropdown: 0 8px 30px rgba(0,0,0,0.4);
  --shadow-modal: 0 20px 60px rgba(0,0,0,0.5);
}

/* ===== 全局重置 ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont,
    "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  transition: background 0.3s ease, color 0.3s ease;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* ===== 卡片（替代旧 .glass / .glass-strong） ===== */
.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1),
              box-shadow 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.card-clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
}

/* ===== 链接 ===== */
a {
  color: var(--accent);
  text-decoration: none;
  transition: opacity 0.2s ease;
}

a:hover {
  opacity: 0.8;
}

/* ===== 动画关键帧 ===== */
.fade-in {
  animation: fadeIn 0.3s ease-out;
}

.scale-in {
  animation: scaleIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.25, 0.1, 0.25, 1) both;
}

.fade-in-up-delayed {
  animation: fadeInUp 0.6s cubic-bezier(0.25, 0.1, 0.25, 1) 0.1s both;
}
```

- [ ] **Step 2: 删除旧的 glassmorphism.css**

Run: `Remove-Item frontend/src/styles/glassmorphism.css`

- [ ] **Step 3: 更新 transitions.css — 改进缓动曲线和关键帧**

将 `frontend/src/styles/transitions.css` 完全重写为：

```css
/* 页面过渡 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 卡片交错入场 */
.card-stagger-enter-active {
  transition: opacity 0.4s ease-out, transform 0.4s ease-out;
}
.card-stagger-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* 骨架屏脉冲 */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}
.skeleton-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  background: var(--border-color);
  border-radius: 6px;
}

/* 点赞弹跳 */
@keyframes like-bounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.25); }
  60% { transform: scale(0.9); }
  100% { transform: scale(1); }
}
.like-bounce {
  animation: like-bounce 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 收藏旋转 */
@keyframes star-spin {
  0% { transform: rotate(0deg) scale(1); }
  40% { transform: rotate(180deg) scale(1.15); }
  100% { transform: rotate(360deg) scale(1); }
}
.star-spin {
  animation: star-spin 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 淡入上浮 */
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up-el {
  animation: fade-in-up 0.4s ease both;
}
```

- [ ] **Step 4: 更新 main.ts 的 CSS 导入路径**

将 `frontend/src/main.ts` 第5行从：
```ts
import './styles/glassmorphism.css'
```
改为：
```ts
import './styles/theme.css'
```

- [ ] **Step 5: 更新 index.html 字体引用，加入中文字体**

将 `frontend/index.html` 第7行的 Google Fonts 链接替换为：
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@400;500;600&display=swap" rel="stylesheet">
```

- [ ] **Step 6: 验证 — 启动前端确认无报错**

Run: `cd frontend && npm run dev`
Expected: Vite 正常启动，无 CSS 引用报错，页面背景已变为 `#f5f5f7`

- [ ] **Step 7: Commit**

```bash
git add frontend/src/styles/theme.css frontend/src/styles/transitions.css frontend/src/styles/glassmorphism.css frontend/src/main.ts frontend/index.html
git commit -m "feat: 全局样式系统重建 — Apple 极简色彩 + 排版 token"
```

---

### Task 2: Naive UI 主题配置更新

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 更新 Naive UI themeOverrides 的色值和圆角**

将 `frontend/src/App.vue` 的 `<script setup>` 中 `lightThemeOverrides` 和 `darkThemeOverrides` 替换为：

```ts
const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#0071e3',
    primaryColorHover: '#0077ed',
    primaryColorPressed: '#0066cc',
    borderRadius: '10px',
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  Button: {
    borderRadiusMedium: '980px',
  },
  Input: {
    borderRadius: '10px',
    heightMedium: '40px',
  },
  Card: {
    borderRadius: '16px',
  },
}

const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#2997ff',
    primaryColorHover: '#40a9ff',
    primaryColorPressed: '#0077ed',
    borderRadius: '10px',
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  Button: {
    borderRadiusMedium: '980px',
  },
  Input: {
    borderRadius: '10px',
    heightMedium: '40px',
  },
  Card: {
    borderRadius: '16px',
  },
}
```

- [ ] **Step 2: 验证 — 启动前端查看 Naive UI 按钮和输入框样式**

Run: `cd frontend && npm run dev`
Expected: 主按钮变为苹果蓝 `#0071e3`，胶囊形圆角，输入框高度 40px 圆角 10px

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: Naive UI 主题配置更新 — 苹果蓝色 + 胶囊按钮 + 新字体栈"
```

---

### Task 3: Header 导航栏重设计

**Files:**
- Modify: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: 重写 AppLayout.vue template 中的 Header 和 script 滚动监听**

将 `<script setup>` 部分替换为（保留 import 和已有逻辑，新增滚动状态）：

```ts
import { ref, onMounted, onBeforeUnmount } from 'vue'

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const auth = useAuthStore()
const isScrolled = ref(false)

function onScroll() {
  isScrolled.value = window.scrollY > 0
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

const adminOptions = [
  { label: '分类管理', key: 'categories' },
  { label: '标签管理', key: 'tags' },
  { label: '用户管理', key: 'users' },
  { type: 'divider' as const, key: 'd1' },
  { label: '审计日志', key: 'audit-logs' },
]

function handleAdminSelect(key: string) {
  router.push(`/admin/${key}`)
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
```

将 `<template>` 中的 `NLayoutHeader` 替换为：

```html
<template>
  <NLayout style="min-height: 100vh; background: var(--bg-primary);">
    <NLayoutHeader
      :style="{
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: '44px',
        background: isScrolled ? 'var(--bg-header)' : 'var(--bg-header-solid)',
        borderBottom: isScrolled ? 'none' : '0.5px solid var(--border-color)',
        backdropFilter: isScrolled ? 'saturate(180%) blur(20px)' : 'none',
        WebkitBackdropFilter: isScrolled ? 'saturate(180%) blur(20px)' : 'none',
        transition: 'background 0.3s ease, backdrop-filter 0.3s ease, border-color 0.3s ease',
      }"
    >
      <NSpace align="center" :size="24">
        <NText
          strong
          style="font-size: 18px; font-weight: 600; cursor: pointer; letter-spacing: -0.3px;"
          @click="router.push('/')"
        >
          Blog
        </NText>
      </NSpace>

      <NSpace align="center" :size="4">
        <NButton text @click="router.push('/')">首页</NButton>
        <NButton v-if="auth.isAuthor" text @click="router.push('/editor')">创作</NButton>
        <NButton v-if="auth.isAuthor" text @click="router.push('/drafts')">草稿</NButton>
        <NButton v-if="auth.isLoggedIn" text @click="router.push('/favorites')">收藏</NButton>
        <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
          <NButton text>管理</NButton>
        </NDropdown>
      </NSpace>

      <NSpace align="center" :size="8">
        <NButton quaternary circle size="small" @click="dark = !dark">
          <template #icon>
            <NIcon :component="dark ? Sunny : Moon" />
          </template>
        </NButton>

        <template v-if="auth.isLoggedIn">
          <NText depth="2" style="font-size: 13px;">{{ auth.user?.username }}</NText>
          <NButton text size="small" @click="router.push('/settings')">设置</NButton>
          <NButton text size="small" @click="handleLogout">登出</NButton>
        </template>
        <template v-else>
          <NButton size="small" type="primary" @click="router.push('/login')">登录</NButton>
        </template>
      </NSpace>
    </NLayoutHeader>

    <NLayoutContent style="padding: 0 32px 64px; max-width: 1200px; margin: 0 auto; width: 100%;">
      <slot />
    </NLayoutContent>
  </NLayout>
</template>
```

- [ ] **Step 2: 验证 — 启动前端，检查 Header 高度 44px、滚动行为、导航项居中**

Run: `cd frontend && npm run dev`
Expected: Header 高度 44px，滚动前纯白+分割线，滚动后毛玻璃背景

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AppLayout.vue
git commit -m "feat: Header 重设计 — 44px 高度 + 滚动毛玻璃切换 + 苹果极简导航"
```

---

### Task 4: GlassCard 组件改造

**Files:**
- Modify: `frontend/src/components/GlassCard.vue`

- [ ] **Step 1: 将 GlassCard 从毛玻璃改为纯白卡片**

将 `GlassCard.vue` 完全替换为：

```vue
<script setup lang="ts">
defineProps<{
  padding?: string
}>()
</script>

<template>
  <div class="card scale-in" :style="{ padding: padding || '32px' }">
    <slot />
  </div>
</template>
```

- [ ] **Step 2: 验证 — 检查使用 GlassCard 的页面（Login, Settings）**

Run: `cd frontend && npm run dev`
Expected: GlassCard 变为纯白卡片 + 极淡阴影

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/GlassCard.vue
git commit -m "refactor: GlassCard 从毛玻璃改为 Apple 纯白卡片"
```

---

### Task 5: ArticleCard + ArticleCardSkeleton 重构

**Files:**
- Modify: `frontend/src/components/ArticleCard.vue`
- Modify: `frontend/src/components/ArticleCardSkeleton.vue`

- [ ] **Step 1: 重写 ArticleCard.vue — 纯白卡片 + 新排版**

将 `ArticleCard.vue` 的 `<template>` 和 `<style>` 替换为：

```html
<template>
  <div class="card card-clickable scale-in" style="padding: 0; cursor: pointer; overflow: hidden;">
    <div v-if="article.cover_image" style="height: 180px; overflow: hidden;">
      <img
        :src="article.cover_image"
        style="width: 100%; height: 100%; object-fit: cover; display: block;"
        alt=""
      />
    </div>

    <div style="padding: 28px;">
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
        <NTag v-if="article.is_pinned" type="error" size="small" round>置顶</NTag>
        <NTag v-if="article.is_draft" type="warning" size="small" round>草稿</NTag>
        <NTag v-if="article.category" type="info" size="small" round>{{ article.category.name }}</NTag>
      </div>

      <NText tag="h2" style="font-size: 20px; font-weight: 600; margin-bottom: 8px; line-height: 1.35; letter-spacing: -0.2px;">
        {{ article.title }}
      </NText>

      <NText
        v-if="article.summary"
        depth="2"
        style="margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: 15px; line-height: 1.5;"
      >
        {{ article.summary }}
      </NText>

      <NSpace align="center">
        <NText depth="3" style="font-size: 13px;">
          {{ article.author?.username || '匿名' }}
        </NText>
        <NText depth="3" style="font-size: 13px;">·</NText>
        <NText depth="3" style="font-size: 13px;">
          {{ formatDate(article.published_at || article.created_at) }}
        </NText>
        <NText depth="3" style="font-size: 13px;">·</NText>
        <NText depth="3" style="font-size: 13px;">
          {{ article.view_count }} 次阅读
        </NText>
      </NSpace>

      <NSpace v-if="article.tags.length" style="margin-top: 12px;">
        <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
          {{ tag.name }}
        </NTag>
      </NSpace>
    </div>
  </div>
</template>
```

删除旧的 `<style scoped>` 块（hover 效果已由 `.card-clickable` 全局处理）。

- [ ] **Step 2: 重写 ArticleCardSkeleton.vue — 适配新卡片风格**

```html
<template>
  <div class="card" style="padding: 0; overflow: hidden;">
    <div class="skeleton-pulse" style="height: 180px; width: 100%; border-radius: 0;" />
    <div style="padding: 28px; display: flex; flex-direction: column; gap: 12px;">
      <div class="skeleton-pulse" style="height: 22px; width: 65%;" />
      <div class="skeleton-pulse" style="height: 15px; width: 90%;" />
      <div class="skeleton-pulse" style="height: 15px; width: 45%;" />
      <div style="display: flex; gap: 8px; margin-top: 4px;">
        <div class="skeleton-pulse" style="height: 20px; width: 50px; border-radius: 10px;" />
        <div class="skeleton-pulse" style="height: 20px; width: 50px; border-radius: 10px;" />
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 3: 验证 — 检查文章列表卡片样式**

Expected: 纯白卡片 + 封面图撑满顶边 + hover 抬升效果

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ArticleCard.vue frontend/src/components/ArticleCardSkeleton.vue
git commit -m "feat: ArticleCard + Skeleton 重构 — Apple 纯白卡片 + 新排版"
```

---

### Task 6: HomeView — 新增 Hero 区域

**Files:**
- Modify: `frontend/src/views/HomeView.vue`

- [ ] **Step 1: 在文章列表上方添加 Hero 区域**

在 `HomeView.vue` 的 `<template>` 中，将当前的 `<div style="max-width: 800px;...">` 改为：

```html
<template>
  <div>
    <!-- Hero 区域 -->
    <div style="background: var(--bg-primary); padding: 80px 0 64px; text-align: center;">
      <h1 class="fade-in-up" style="font-size: 48px; font-weight: 600; line-height: 1.1; letter-spacing: -0.5px; margin: 0 0 16px; color: var(--text-primary);">
        用文字记录思考
      </h1>
      <p class="fade-in-up-delayed" style="font-size: 21px; line-height: 1.4; color: var(--text-secondary); margin: 0 0 40px; max-width: 500px; margin-left: auto; margin-right: auto;">
        分享技术见解与日常感悟
      </p>
      <div class="fade-in-up-delayed" style="max-width: 480px; margin: 0 auto;">
        <NInput
          v-model:value="searchKeyword"
          placeholder="搜索文章..."
          clearable
          round
          size="large"
          :style="{ '--n-border': 'var(--border-color-strong)', '--n-color': 'var(--bg-card)', '--n-color-focus': 'var(--bg-card)', '--n-text-color': 'var(--text-primary)' }"
        >
          <template #prefix>
            <NIcon :component="Search" />
          </template>
        </NInput>
      </div>
    </div>

    <!-- 搜索筛选栏 + 文章列表 -->
    <div style="max-width: 720px; margin: 0 auto; padding-top: 32px;">
      <div class="card" style="padding: 16px 20px; margin-bottom: 24px;">
        <NSpace vertical :size="12" style="width: 100%;">
          <NSpace>
            <NSelect
              v-model:value="selectedCategory"
              :options="categories.map(c => ({ label: c.name, value: c.id }))"
              placeholder="分类筛选"
              clearable
              style="width: 160px;"
            />
            <NSelect
              v-model:value="selectedTag"
              :options="tags.map(t => ({ label: t.name, value: t.id }))"
              placeholder="标签筛选"
              clearable
              style="width: 160px;"
            />
            <NButton text @click="clearFilters">清除筛选</NButton>
            <div style="flex: 1;" />
            <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
              写文章
            </NButton>
          </NSpace>
        </NSpace>
      </div>

      <!-- 文章列表 (保持原有逻辑) -->
      <template v-if="initialLoading">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <ArticleCardSkeleton v-for="i in 3" :key="i" />
        </div>
      </template>

      <NSpin v-else :show="loading">
        <div v-if="!loading && articles.length === 0" style="padding: 80px 0;">
          <NEmpty description="还没有文章">
            <template #extra>
              <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
                写第一篇文章
              </NButton>
            </template>
          </NEmpty>
        </div>

        <div v-else style="display: flex; flex-direction: column; gap: 24px;">
          <div
            v-for="article in articles"
            :key="article.id"
            @click="router.push(`/article/${article.id}`)"
          >
            <ArticleCard :article="article" />
          </div>
        </div>
      </NSpin>

      <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 48px;">
        <NPagination
          :page="page"
          :page-size="pageSize"
          :item-count="total"
          @update:page="onPageChange"
        />
      </div>
    </div>
  </div>
</template>
```

注意：搜索框已移到 Hero 区域，因此从筛选栏中移除 `NInput` 搜索框。`searchKeyword` 的 watch 保持不变（在 Hero 区域的搜索框中输入依然会触发搜索）。

- [ ] **Step 2: 验证 — 检查 Hero 入场动画、搜索框功能、布局**

Expected: Hero 标题淡入上浮，搜索正常，页面最大宽度 720px

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/HomeView.vue
git commit -m "feat: HomeView — 新增 Apple 风格 Hero 区域 + 入场动画"
```

---

### Task 7: LoginView 卡片重构

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

- [ ] **Step 1: 更新 LoginView 模板样式**

将 `LoginView.vue` 的 `<template>` 中 `<GlassCard>` 标签替换为纯白卡片，并增大内边距：

```html
<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 160px);">
    <div class="card" style="width: 440px; max-width: 90vw; padding: 48px;">
      <NH2 style="text-align: center; margin-bottom: 28px; font-weight: 600; font-size: 28px; letter-spacing: -0.3px;">
        {{ isLogin ? '登录' : '注册' }}
      </NH2>

      <NTabs v-model:value="activeTab" type="segment" animated style="margin-bottom: 28px;">
        <NTabPane name="login" tab="登录" />
        <NTabPane name="register" tab="注册" />
      </NTabs>

      <template v-if="isLogin">
        <NForm ref="loginRef" :model="loginForm" :rules="loginRules" label-placement="left">
          <NFormItem label="用户名" path="username">
            <NInput v-model:value="loginForm.username" placeholder="请输入用户名" />
          </NFormItem>
          <NFormItem label="密码" path="password">
            <NInput v-model:value="loginForm.password" type="password" placeholder="请输入密码" show-password-on="click" />
          </NFormItem>
          <NFormItem>
            <NCheckbox v-model:checked="loginForm.rememberMe">记住我</NCheckbox>
          </NFormItem>
          <NButton
            type="primary"
            block
            :loading="loading"
            :disabled="lockCountdown > 0"
            @click="handleLogin"
            style="height: 42px; font-size: 16px;"
          >
            {{ lockText || '登录' }}
          </NButton>
        </NForm>
      </template>

      <template v-else>
        <NForm ref="registerRef" :model="registerForm" :rules="registerRules" label-placement="left">
          <NFormItem label="用户名" path="username">
            <NInput v-model:value="registerForm.username" placeholder="请输入用户名" />
          </NFormItem>
          <NFormItem label="邮箱" path="email">
            <NInput v-model:value="registerForm.email" placeholder="请输入邮箱" />
          </NFormItem>
          <NFormItem label="密码" path="password">
            <NInput v-model:value="registerForm.password" type="password" placeholder="至少8位，含字母和数字" show-password-on="click" />
          </NFormItem>
          <NFormItem label="确认密码" path="confirmPassword">
            <NInput v-model:value="registerForm.confirmPassword" type="password" placeholder="再次输入密码" show-password-on="click" />
          </NFormItem>
          <NButton type="primary" block :loading="loading" @click="handleRegister" style="height: 42px; font-size: 16px;">
            注册
          </NButton>
        </NForm>
      </template>
    </div>
  </div>
</template>
```

同时删除 `<script setup>` 中 `import GlassCard from '../components/GlassCard.vue'` 这一行。

- [ ] **Step 2: 验证 — 登录页卡片纯白 + 48px 内边距**

Expected: 纯白卡片，内边距 48px，整体更宽松

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/LoginView.vue
git commit -m "feat: LoginView — 纯白卡片 + Apple 风格宽间距"
```

---

### Task 8: ArticleDetail 排版优化

**Files:**
- Modify: `frontend/src/views/ArticleDetail.vue`

- [ ] **Step 1: 更新详情页宽度、分割线色值、内边距**

在 `ArticleDetail.vue` 中进行以下模板改动：

1. 容器最大宽度从 `800px` 改为 `780px`
2. 分割线从 `var(--border-glass)` 改为 `var(--border-color)`
3. 文章内容样式微调

关键替换：
- 第 99 行：`max-width: 800px` → `max-width: 780px`
- 第 119-128 行：封面图的 `class="glass"` → `class="card"`
- 第 182 行：`1px solid var(--border-glass)` → `1px solid var(--border-color)`
- 第 192 行：同上替换
- 第 206 行：同上替换

- [ ] **Step 2: 更新文章内容样式（全局 style 块）**

将 `<style>` 块中 `--accent` 和 `--border-glass` 的引用更新：

```css
.article-content h1 { font-size: 28px; margin: 32px 0 12px; }
.article-content h2 { font-size: 24px; margin: 28px 0 10px; }
.article-content h3 { font-size: 20px; margin: 24px 0 8px; }
.article-content p { margin-bottom: 16px; }
.article-content img { max-width: 100%; border-radius: 8px; margin: 12px 0; }
.article-content pre { background: rgba(0,0,0,0.03); border-radius: 8px; padding: 20px; overflow-x: auto; margin: 20px 0; }
.article-content code { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 14px; }
.article-content blockquote { border-left: 3px solid var(--accent); padding-left: 16px; margin: 20px 0; color: var(--text-secondary); }
.article-content table { width: 100%; border-collapse: collapse; margin: 20px 0; }
.article-content th, .article-content td { border: 1px solid var(--border-color); padding: 8px 12px; text-align: left; }
.article-content th { background: rgba(0,0,0,0.02); }
.article-content a { color: var(--accent); }
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/ArticleDetail.vue
git commit -m "feat: ArticleDetail — 排版优化 + 分割线色值统一"
```

---

### Task 9: ArticleEditor 编辑器样式适配

**Files:**
- Modify: `frontend/src/views/ArticleEditor.vue`

- [ ] **Step 1: 替换工具栏和面板的毛玻璃类名**

在 `ArticleEditor.vue` 中进行以下替换：
- 第 201 行工具栏：`class="glass"` → `class="card"`
- 第 216 行侧边栏：`class="glass"` → `class="card"`
- 第 279 行图片弹窗：`class="glass"` → `class="card"`

- [ ] **Step 2: 验证编辑器外观**

Expected: 工具栏和侧边栏均为纯白卡片，无毛玻璃效果

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/ArticleEditor.vue
git commit -m "feat: ArticleEditor — 工具栏/面板 Apple 纯白卡片适配"
```

---

### Task 10: ProfileView, FavoritesView, DraftsView 批量适配

**Files:**
- Modify: `frontend/src/views/ProfileView.vue`
- Modify: `frontend/src/views/FavoritesView.vue`
- Modify: `frontend/src/views/DraftsView.vue`

- [ ] **Step 1: ProfileView — 替换 glass 类 + 优化排版**

替换内容：
- 容器最大宽度 `800px` → `720px`
- 用户信息卡片 `class="glass"` → `class="card"`
- 用户名字号 `28px` → `32px`，字重 `700` → `600`

- [ ] **Step 2: FavoritesView — 替换 glass 类 + 宽度统一**

替换内容：
- 容器最大宽度 `800px` → `720px`
- 标题字号 `24px` → `32px`，间距调整
- 已有毛玻璃 card 的容器（无 glass 类名），只需改宽度

- [ ] **Step 3: DraftsView — 替换 glass 类 + 宽度统一**

替换内容：
- 容器最大宽度 `800px` → `720px`
- 保持编辑/删除按钮在卡片右侧的布局

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/ProfileView.vue frontend/src/views/FavoritesView.vue frontend/src/views/DraftsView.vue
git commit -m "feat: 用户页面 — Profile/Favorites/Drafts 宽度统一 + 纯白卡片"
```

---

### Task 11: SettingsView 适配

**Files:**
- Modify: `frontend/src/views/SettingsView.vue`

- [ ] **Step 1: 替换 GlassCard 为纯白卡片，更新宽度**

替换内容：
- 容器最大宽度 `600px` → `720px`
- 所有 `<GlassCard>` 标签替换为 `<div class="card" style="margin-top: 16px; padding: 32px;">`
- 删除 `import GlassCard` 引用
- 页面标题字号 `24px` → `32px`

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/SettingsView.vue
git commit -m "feat: SettingsView — 纯白卡片 + 新宽度 + 新排版"
```

---

### Task 12: 管理页面批量适配

**Files:**
- Modify: `frontend/src/views/admin/CategoryManage.vue`
- Modify: `frontend/src/views/admin/TagManage.vue`
- Modify: `frontend/src/views/admin/UserManage.vue`
- Modify: `frontend/src/views/admin/AuditLogs.vue`

- [ ] **Step 1: CategoryManage — 替换 glass 类名**

替换内容：
- 第 91 行数据表格容器：`class="glass"` → `class="card"`
- 第 96 行 Modal 内容：`class="glass"` → `class="card"`

- [ ] **Step 2: TagManage — 替换 glass 类名**

替换内容：
- 第 87 行数据表格容器：`class="glass"` → `class="card"`
- 第 92 行 Modal 内容：`class="glass"` → `class="card"`

- [ ] **Step 3: UserManage — 更新页面标题字号**

- 标题字号 `24px` → `32px`

- [ ] **Step 4: AuditLogs — 更新页面标题字号**

- 标题字号 `24px` → `32px`

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/admin/CategoryManage.vue frontend/src/views/admin/TagManage.vue frontend/src/views/admin/UserManage.vue frontend/src/views/admin/AuditLogs.vue
git commit -m "feat: 管理页面 — 数据表格纯白卡片 + 标题排版统一"
```

---

### Task 13: 子组件样式适配

**Files:**
- Modify: `frontend/src/components/CommentSection.vue`
- Modify: `frontend/src/components/CommentItem.vue`
- Modify: `frontend/src/components/LikeButton.vue`
- Modify: `frontend/src/components/FavoriteButton.vue`
- Modify: `frontend/src/components/TableOfContents.vue`
- Modify: `frontend/src/components/AuthorDashboard.vue`

- [ ] **Step 1: CommentSection — 更新标题字号**

- 评论标题字号 `20px` → `24px`

- [ ] **Step 2: CommentItem — 替换 glass 类名**

- `class="glass"` → `class="card"`

- [ ] **Step 3: LikeButton + FavoriteButton — 微调圆角**

- 按钮 `border-radius: 20px` → `border-radius: 980px`

- [ ] **Step 4: TableOfContents — 更新色值引用**

更新 `<style scoped>` 中的颜色引用：
- `var(--text-secondary, #666)` → `var(--text-secondary)`
- `var(--accent, #5b8c5a)` → `var(--accent)`
- `background: rgba(128, 128, 128, 0.04)` → `background: transparent`

- [ ] **Step 5: AuthorDashboard — 替换 glass 类名**

- 统计卡片中 5 处 `class="glass"` → `class="card"`
- 卡片内 `padding: 20px` → `padding: 24px`

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/CommentSection.vue frontend/src/components/CommentItem.vue frontend/src/components/LikeButton.vue frontend/src/components/FavoriteButton.vue frontend/src/components/TableOfContents.vue frontend/src/components/AuthorDashboard.vue
git commit -m "feat: 子组件 — Comment/Like/Favorite/ToC/Dashboard 样式适配"
```

---

### Task 14: 最终验收

- [ ] **Step 1: 亮色模式全页面验收**

Run: `cd frontend && npm run dev`
Check 每个页面：
1. 首页：Hero 区域 + 卡片 + 入场动画
2. 文章详情：排版、分割线、目录侧边栏
3. 登录：纯白卡片 + 宽间距
4. 编辑器：工具栏 + 侧边栏
5. 个人主页：用户卡片 + 文章列表
6. 设置：表单卡片
7. 收藏/草稿：列表样式
8. 管理页面：数据表格

- [ ] **Step 2: 暗色模式验收**

切换暗色模式，检查所有页面在暗色下的对比度和可读性。

- [ ] **Step 3: Header 滚动行为验收**

在首页滚动，确认 Header 从纯白切换到毛玻璃背景的过渡效果。

- [ ] **Step 4: 确认无残留引用**

搜索确认代码库中不再有任何 `glass` / `glass-strong` / `glassmorphism` 引用：
```bash
rg "glass|glassmorphism" frontend/src --include "*.vue" --include "*.ts" --include "*.css"
```
Expected: 无结果（或仅出现在注释中）

- [ ] **Step 5: Commit**

```bash
git commit -m "chore: 最终验收通过 — 无毛玻璃残留 + 亮/暗色一致"
```

# Airbnb 风格 UI 改版实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将博客前端从极光玻璃主题全面改造为 Airbnb 极简设计风格，保留暗色模式。

**Architecture:** 分 4 层实施。Layer 1 建立设计令牌基础（CSS 变量 + Naive UI themeOverrides + 工具模块），Layer 2 改造导航布局，Layer 3 更新通用组件，Layer 4 改造所有页面视图。每层完成后验证构建。

**Tech Stack:** Vue 3 + TypeScript + Naive UI + Vite + CSS Custom Properties

---

### Task 1: 新建 Airbnb 设计令牌 CSS 文件

**Files:**
- Create: `frontend/src/styles/airbnb.css`

- [ ] **Step 1: 写入完整的 airbnb.css**

```css
/* ===== Airbnb Design System ===== */

:root {
  /* Canvas & Surface */
  --color-canvas: #ffffff;
  --color-surface-soft: #f7f7f7;
  --color-surface-strong: #f2f2f2;

  /* Brand — Rausch */
  --color-primary: #ff385c;
  --color-primary-hover: #e00b41;
  --color-primary-disabled: #ffd1da;

  /* Text */
  --color-ink: #222222;
  --color-body: #3f3f3f;
  --color-muted: #6a6a6a;
  --color-muted-soft: #929292;

  /* Hairlines */
  --color-hairline: #dddddd;
  --color-hairline-soft: #ebebeb;
  --color-border-strong: #c1c1c1;

  /* Semantic */
  --color-error: #c13515;
  --color-error-hover: #b32505;

  /* Shadow — single tier */
  --shadow-card: rgba(0, 0, 0, 0.02) 0 0 0 1px,
    rgba(0, 0, 0, 0.04) 0 2px 6px,
    rgba(0, 0, 0, 0.1) 0 4px 8px;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-base: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-xxl: 48px;
  --spacing-section: 64px;

  /* Typography */
  --font-family: "Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* Dark mode */
[data-theme="dark"] {
  --color-canvas: #141414;
  --color-surface-soft: #1e1e1e;
  --color-surface-strong: #2a2a2a;
  --color-primary: #ff5a7a;
  --color-primary-hover: #ff7a95;
  --color-primary-disabled: #5c2030;
  --color-ink: #e8e8e8;
  --color-body: #b0b0b0;
  --color-muted: #888888;
  --color-muted-soft: #666666;
  --color-hairline: #333333;
  --color-hairline-soft: #2a2a2a;
  --color-border-strong: #555555;
  --color-error: #e05545;
  --color-error-hover: #f07060;
  --shadow-card: rgba(0, 0, 0, 0.3) 0 0 0 1px,
    rgba(0, 0, 0, 0.4) 0 2px 6px,
    rgba(0, 0, 0, 0.5) 0 4px 8px;
}

/* ===== Global Reset ===== */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background: var(--color-canvas);
  color: var(--color-ink);
  min-height: 100vh;
  transition: background 0.3s ease, color 0.3s ease;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* ===== Utility Classes ===== */
.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline-soft);
  border-radius: var(--radius-md);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-card);
}

/* Links */
a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-primary-hover);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--color-hairline);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-strong);
}

/* Selection */
::selection {
  background: rgba(255, 56, 92, 0.2);
  color: var(--color-ink);
}
```

- [ ] **Step 2: 验证文件创建成功**

Run: `Get-ChildItem "C:\Mywebsite_2\frontend\src\styles\airbnb.css"`
Expected: 文件存在

---

### Task 2: 新建 Identicon 头像生成器

**Files:**
- Create: `frontend/src/utils/identicon.ts`

- [ ] **Step 1: 写入 identicon.ts**

```typescript
/**
 * GitHub-style identicon generator.
 * Deterministic geometric avatar from username hash.
 */

const PALETTE: [string, string][] = [
  ['#667eea', '#764ba2'],
  ['#f093fb', '#f5576c'],
  ['#4facfe', '#00f2fe'],
  ['#43e97b', '#38f9d7'],
  ['#fa709a', '#fee140'],
  ['#a18cd1', '#fbc2eb'],
  ['#fad0c4', '#ffd1ff'],
  ['['#ff9a9e', '#fecfef'],
  ['#a1c4fd', '#c2e9fb'],
  ['#d4fc79', '#96e6a1'],
  ['#84fab0', '#8fd3f4'],
  ['#e0c3fc', '#8ec5fc'],
]

function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}

function getPalette(username: string): [string, string] {
  return PALETTE[hashString(username) % PALETTE.length]
}

/**
 * Generate a 5x5 symmetric identicon pattern.
 * Returns a 5-element array of 5-bit integers (each bit = fill/empty).
 * Mirroring: horizontal flip for symmetry.
 */
function generatePattern(hash: number): number[] {
  const rows: number[] = []
  for (let y = 0; y < 5; y++) {
    let row = 0
    // Only need to compute left 3 columns; mirror for right
    for (let x = 0; x < 3; x++) {
      const bit = (hash >> (y * 3 + x)) & 1
      if (bit) {
        row |= (1 << x)
        row |= (1 << (4 - x)) // mirror
      }
    }
    rows.push(row)
  }
  return rows
}

export function generateIdenticonSVG(username: string, size = 80): string {
  const hash = hashString(username)
  const [color1, color2] = getPalette(username)
  const pattern = generatePattern(hash)
  const cellSize = size / 5
  const radius = size * 0.1 // 8px radius equivalent at 80px

  let rects = ''
  for (let y = 0; y < 5; y++) {
    for (let x = 0; x < 5; x++) {
      if (pattern[y] & (1 << x)) {
        const rx = x * cellSize
        const ry = y * cellSize
        rects += `<rect x="${rx}" y="${ry}" width="${cellSize}" height="${cellSize}" rx="${radius}" ry="${radius}"/>`
      }
    }
  }

  return `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${color1}"/><stop offset="100%" stop-color="${color2}"/></linearGradient></defs>
      <rect width="${size}" height="${size}" rx="${radius}" fill="url(#g)"/>
      <g fill="rgba(255,255,255,0.55)">${rects}</g>
    </svg>`
  )}`
}

export function getIdenticonUrl(username: string, customAvatar?: string | null, size = 80): string {
  if (customAvatar) return customAvatar
  return generateIdenticonSVG(username, size)
}
```

- [ ] **Step 2: 验证语法无错误**

Run: `npx tsc --noEmit --skipLibCheck "C:\Mywebsite_2\frontend\src\utils\identicon.ts"`
Expected: 无错误输出

---

### Task 3: 新建标签封面映射表

**Files:**
- Create: `frontend/src/utils/covers.ts`

- [ ] **Step 1: 写入 covers.ts**

```typescript
/**
 * Tag-to-cover-image mapping.
 * When an article has no cover_image, derive a default gradient + icon
 * from the first matching tag.
 */

export interface CoverStyle {
  gradient: string    // CSS gradient string
  icon: string        // Emoji or SVG
}

const TAG_COVER_MAP: Record<string, CoverStyle> = {
  '编程':    { gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: '\u{1F4BB}' },
  '技术':    { gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: '\u{1F527}' },
  '前端':    { gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: '\u{1F3A8}' },
  '后端':    { gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: '\u{2699}️' },
  'Python':  { gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', icon: '\u{1F40D}' },
  'JavaScript': { gradient: 'linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)', icon: '\u{1F310}' },
  'AI':      { gradient: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)', icon: '\u{1F916}' },
  '设计':    { gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', icon: '\u{1F3A8}' },
  '产品':    { gradient: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)', icon: '\u{1F4A1}' },
  '创业':    { gradient: 'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)', icon: '\u{1F680}' },
  '生活':    { gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', icon: '\u{1F30D}' },
  '随笔':    { gradient: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)', icon: '\u{270F}️' },
  '阅读':    { gradient: 'linear-gradient(135deg, #c1dfc4 0%, #deecdd 100%)', icon: '\u{1F4DA}' },
  '摄影':    { gradient: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)', icon: '\u{1F4F7}' },
  '音乐':    { gradient: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)', icon: '\u{1F3B5}' },
}

const DEFAULT_COVER: CoverStyle = {
  gradient: 'linear-gradient(135deg, #e8e8e8 0%, #f5f5f5 100%)',
  icon: '\u{1F4DD}',
}

/**
 * Get cover style for a given tag name.
 * Falls back to DEFAULT_COVER for unknown tags.
 */
export function getCoverForTag(tagName?: string | null): CoverStyle {
  if (!tagName) return DEFAULT_COVER
  const match = TAG_COVER_MAP[tagName]
  if (match) return match
  // Try lowercase match
  const lower = tagName.toLowerCase()
  for (const [key, value] of Object.entries(TAG_COVER_MAP)) {
    if (key.toLowerCase() === lower) return value
  }
  return DEFAULT_COVER
}

/**
 * Get cover style from an article's tags array.
 * Uses the first tag, falls back to default.
 */
export function getCoverForArticle(tags?: Array<{ id: number; name: string }> | null): CoverStyle {
  if (!tags || tags.length === 0) return DEFAULT_COVER
  return getCoverForTag(tags[0].name)
}
```

- [ ] **Step 2: 验证语法无错误**

Run: `npx tsc --noEmit --skipLibCheck "C:\Mywebsite_2\frontend\src\utils\covers.ts"`
Expected: 无错误输出

---

### Task 4: 更新入口文件 — index.html / main.ts / 删除 glassmorphism.css

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/main.ts`
- Delete: `frontend/src/styles/glassmorphism.css`

- [ ] **Step 1: 更新 index.html 中的 Google Fonts 引用**

将第 7 行的字体 link:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

替换为:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: 更新 main.ts 引用**

将第 5 行:
```typescript
import './styles/glassmorphism.css'
```

替换为:
```typescript
import './styles/airbnb.css'
```

- [ ] **Step 3: 删除 glassmorphism.css**

Run: `Remove-Item "C:\Mywebsite_2\frontend\src\styles\glassmorphism.css"`

- [ ] **Step 4: 删除 transitions.css（如果存在且已空）**

检查 `frontend/src/styles/transitions.css`，保留页面过渡动画，移除玻璃相关动画引用。

- [ ] **Step 5: 验证 Vite 开发服务器正常启动**

Run: `cd C:\Mywebsite_2\frontend; npm run dev`
Expected: Vite 启动成功，无 CSS 相关错误

---

### Task 5: 更新 App.vue — Naive UI ThemeOverrides

**Files:**
- Modify: `frontend/src/App.vue:12-36`

- [ ] **Step 1: 重写 lightThemeOverrides 和 darkThemeOverrides**

替换 `App.vue` 中 `<script setup>` 内的 `lightThemeOverrides` 和 `darkThemeOverrides` 定义为:

```typescript
const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#ff385c',
    primaryColorHover: '#e00b41',
    primaryColorPressed: '#c90936',
    borderRadius: '8px',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    textColor1: '#222222',
    textColor2: '#3f3f3f',
    textColor3: '#6a6a6a',
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusLarge: '8px',
    borderRadiusSmall: '8px',
    heightMedium: '40px',
  },
  Input: {
    borderRadius: '8px',
    heightLarge: '48px',
  },
  Tag: {
    borderRadius: '8px',
  },
}

const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#ff5a7a',
    primaryColorHover: '#ff7a95',
    primaryColorPressed: '#e04868',
    borderRadius: '8px',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    textColor1: '#e8e8e8',
    textColor2: '#b0b0b0',
    textColor3: '#888888',
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusLarge: '8px',
    borderRadiusSmall: '8px',
    heightMedium: '40px',
  },
  Input: {
    borderRadius: '8px',
    heightLarge: '48px',
  },
  Tag: {
    borderRadius: '8px',
  },
}
```

- [ ] **Step 2: 更新模板中的 NConfigProvider 主题引用**

将 `:theme="isDark ? darkTheme : undefined"` 改为同时为暗色模式提供 darkTheme 基础:
```html
<NConfigProvider :theme="isDark ? darkTheme : undefined" :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides">
```

（保持现有的 `darkTheme` import 不变，Naive UI 内置 darkTheme 提供暗色基础）

---

### Task 6: 重构 AppLayout.vue — 导航栏

**Files:**
- Modify: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: 读取当前文件**

Read `frontend/src/components/AppLayout.vue` 完整内容。

- [ ] **Step 2: 替换模板和样式为 Airbnb 导航风格**

将整个文件重写为:

```vue
<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NText, NDropdown } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Moon, Sunny } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import { computed } from 'vue'

const dark = defineModel<boolean>('dark', { default: false })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

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

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <NLayout :style="{ minHeight: '100vh', background: 'var(--color-canvas)' }">
    <NLayoutHeader
      :style="{
        padding: '0 40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: '80px',
        background: 'var(--color-canvas)',
        borderBottom: '1px solid var(--color-hairline-soft)',
        transition: 'background 0.3s ease, border-color 0.3s ease',
      }"
    >
      <!-- Logo -->
      <NText
        strong
        :style="{
          fontSize: '20px',
          cursor: 'pointer',
          fontWeight: 700,
          color: 'var(--color-primary)',
          letterSpacing: '-0.3px',
        }"
        @click="router.push('/')"
      >
        Blog
      </NText>

      <!-- Center Nav -->
      <NSpace align="center" :size="32">
        <NButton
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/') && route.path === '/' ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/') && route.path === '/' ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: 0,
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/')"
        >
          首页
        </NButton>
        <NButton
          v-if="auth.isAuthor"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/editor') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/editor') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: 0,
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/editor')"
        >
          创作
        </NButton>
        <NButton
          v-if="auth.isAuthor"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/drafts') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/drafts') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: 0,
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/drafts')"
        >
          草稿
        </NButton>
        <NButton
          v-if="auth.isLoggedIn"
          text
          :style="{
            fontSize: '14px',
            fontWeight: 600,
            color: isActive('/favorites') ? 'var(--color-ink)' : 'var(--color-muted)',
            borderBottom: isActive('/favorites') ? '2px solid var(--color-ink)' : '2px solid transparent',
            borderRadius: 0,
            paddingBottom: '4px',
            height: 'auto',
          }"
          @click="router.push('/favorites')"
        >
          收藏
        </NButton>
        <NDropdown v-if="auth.isAdmin" :options="adminOptions" @select="handleAdminSelect">
          <NButton
            text
            :style="{ fontSize: '14px', fontWeight: 600, color: 'var(--color-muted)', height: 'auto' }"
          >
            管理
          </NButton>
        </NDropdown>
      </NSpace>

      <!-- Right Utils -->
      <NSpace align="center" :size="12">
        <NButton quaternary circle @click="dark = !dark">
          <template #icon>
            <NIcon :component="dark ? Sunny : Moon" />
          </template>
        </NButton>

        <template v-if="auth.isLoggedIn">
          <NButton text :style="{ fontSize: '13px', color: 'var(--color-muted)' }" @click="router.push('/settings')">
            {{ auth.user?.username }}
          </NButton>
          <NButton
            size="small"
            :style="{
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--color-ink)',
              border: '1px solid var(--color-ink)',
              borderRadius: '8px',
            }"
            @click="handleLogout"
          >
            登出
          </NButton>
        </template>
        <template v-else>
          <NButton
            size="small"
            type="primary"
            :style="{ borderRadius: '8px', fontWeight: 500 }"
            @click="router.push('/login')"
          >
            登录
          </NButton>
        </template>
      </NSpace>
    </NLayoutHeader>

    <NLayoutContent :style="{ maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '32px' }">
      <slot />
    </NLayoutContent>
  </NLayout>
</template>
```

---

### Task 7: 改造 ArticleCard.vue — Photo-first 卡片 + 默认封面

**Files:**
- Modify: `frontend/src/components/ArticleCard.vue`

- [ ] **Step 1: 重写 ArticleCard.vue**

```vue
<script setup lang="ts">
import { NTag, NText, NSpace } from 'naive-ui'
import type { ArticleInfo } from '../types/api'
import { getCoverForArticle } from '../utils/covers'

const props = defineProps<{ article: ArticleInfo }>()

const coverStyle = getCoverForArticle(props.article.tags)
const hasCover = !!props.article.cover_image

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div
    class="card"
    :style="{
      borderRadius: '14px',
      overflow: 'hidden',
      cursor: 'pointer',
      transition: 'box-shadow 0.2s ease, transform 0.2s ease',
    }"
  >
    <!-- Cover Photo -->
    <div
      :style="{
        aspectRatio: '1 / 1',
        position: 'relative',
        background: hasCover ? undefined : coverStyle.gradient,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }"
    >
      <img
        v-if="hasCover"
        :src="article.cover_image!"
        :style="{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transition: 'transform 0.4s ease',
        }"
        alt=""
      />
      <span
        v-else
        :style="{ fontSize: '48px', opacity: 0.5, lineHeight: 1 }"
      >{{ coverStyle.icon }}</span>

      <!-- Floating badges -->
      <span
        v-if="article.is_pinned"
        :style="{
          position: 'absolute',
          top: '12px',
          left: '12px',
          background: 'var(--color-canvas)',
          color: 'var(--color-ink)',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '11px',
          fontWeight: 600,
          boxShadow: 'var(--shadow-card)',
        }"
      >精选</span>
    </div>

    <!-- Meta -->
    <div :style="{ padding: '16px' }">
      <div :style="{ display: 'flex', gap: '6px', marginBottom: '6px', flexWrap: 'wrap' }">
        <NTag v-if="article.is_draft" type="warning" size="small" :bordered="false">草稿</NTag>
        <NTag v-if="article.category" size="small" :bordered="false">{{ article.category.name }}</NTag>
      </div>

      <NText
        tag="h3"
        :style="{
          fontSize: '16px',
          fontWeight: 600,
          lineHeight: 1.25,
          marginBottom: '4px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }"
      >
        {{ article.title }}
      </NText>

      <NText v-if="article.summary" depth="2" :style="{ fontSize: '14px', marginBottom: '8px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }">
        {{ article.summary }}
      </NText>

      <div :style="{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }">
        <NSpace :size="12">
          <NText depth="3" :style="{ fontSize: '13px' }">
            {{ article.author?.username || '匿名' }}
          </NText>
          <NText depth="3" :style="{ fontSize: '13px' }">
            {{ formatDate(article.published_at || article.created_at) }}
          </NText>
        </NSpace>
        <NText depth="3" :style="{ fontSize: '13px' }">
          {{ article.view_count }} 阅读
        </NText>
      </div>

      <NSpace v-if="article.tags.length" :style="{ marginTop: '8px' }">
        <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
          {{ tag.name }}
        </NTag>
      </NSpace>
    </div>
  </div>
</template>

<style scoped>
.card:hover img {
  transform: scale(1.03);
}
</style>
```

---

### Task 8: 更新骨架屏 ArticleCardSkeleton.vue

**Files:**
- Modify: `frontend/src/components/ArticleCardSkeleton.vue`

- [ ] **Step 1: 重写为匹配新卡片布局的骨架屏**

```vue
<template>
  <div :style="{
    borderRadius: '14px',
    overflow: 'hidden',
    border: '1px solid var(--color-hairline-soft)',
    background: 'var(--color-canvas)',
  }">
    <div :style="{
      aspectRatio: '1 / 1',
      background: 'var(--color-surface-soft)',
      animation: 'pulse 1.5s ease-in-out infinite',
    }" />
    <div :style="{ padding: '16px' }">
      <div :style="{ height: '14px', width: '40%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '8px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ height: '18px', width: '90%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '6px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ height: '18px', width: '65%', background: 'var(--color-surface-soft)', borderRadius: '4px', marginBottom: '12px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      <div :style="{ display: 'flex', justifyContent: 'space-between' }">
        <div :style="{ height: '13px', width: '35%', background: 'var(--color-surface-soft)', borderRadius: '4px', animation: 'pulse 1.5s ease-in-out infinite' }" />
        <div :style="{ height: '13px', width: '20%', background: 'var(--color-surface-soft)', borderRadius: '4px', animation: 'pulse 1.5s ease-in-out infinite' }" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
```

---

### Task 9: 改造 CommentItem.vue — 集成 Identicon 头像

**Files:**
- Modify: `frontend/src/components/CommentItem.vue`

- [ ] **Step 1: 读取当前 CommentItem.vue 内容**

Read the file to understand the current structure before modifying.

- [ ] **Step 2: 在模板中添加头像显示**

对每条评论，在作者名前添加 identicon 头像。修改关键模板区域:

在评论作者行添加头像:
```vue
<div :style="{ display: 'flex', gap: '10px', alignItems: 'flex-start' }">
  <img
    :src="getIdenticonUrl(comment.author?.username || 'anonymous', comment.author?.avatar, 32)"
    :style="{ width: '32px', height: '32px', borderRadius: '8px', flexShrink: 0 }"
    alt=""
  />
  <div :style="{ flex: 1 }">
    <!-- 现有作者名、日期、内容等 -->
  </div>
</div>
```

在 `<script setup>` 顶部添加 import:
```typescript
import { getIdenticonUrl } from '../utils/identicon'
```

- [ ] **Step 3: 保持其余逻辑不变，只调整样式**

将玻璃相关 class 引用移除，替换为纯色背景和内联样式。

---

### Task 10: 改造 CommentSection.vue — 评论输入框 + 头像

**Files:**
- Modify: `frontend/src/components/CommentSection.vue`

- [ ] **Step 1: 读取当前文件**

Read `frontend/src/components/CommentSection.vue`。

- [ ] **Step 2: 在评论输入框左侧添加用户头像**

```vue
<div :style="{ display: 'flex', gap: '10px', alignItems: 'flex-start', marginBottom: '20px' }">
  <img
    v-if="auth.user"
    :src="getIdenticonUrl(auth.user.username, auth.user.avatar, 36)"
    :style="{ width: '36px', height: '36px', borderRadius: '8px', flexShrink: 0 }"
    alt=""
  />
  <div :style="{ flex: 1 }">
    <NInput
      v-model:value="newComment"
      type="textarea"
      placeholder="写下你的评论..."
      :autosize="{ minRows: 2, maxRows: 6 }"
      :style="{ borderRadius: '8px' }"
    />
    <!-- publish button etc -->
  </div>
</div>
```

添加 import:
```typescript
import { getIdenticonUrl } from '../utils/identicon'
```

- [ ] **Step 3: 移除玻璃样式，使用 card class**

评论列表每项用 `card` class 替代 `glass`。

---

### Task 11: 简化 GlassCard.vue

**Files:**
- Modify: `frontend/src/components/GlassCard.vue`

- [ ] **Step 1: 读取并重写 GlassCard.vue**

将组件简化为 Airbnb 风格的卡片 wrapper:

```vue
<script setup lang="ts">
</script>

<template>
  <div class="card" :style="{ padding: '24px', borderRadius: 'var(--radius-md)' }">
    <slot />
  </div>
</template>
```

移除毛玻璃效果、backdrop-blur、glow 属性。

---

### Task 12: 改造 HomeView.vue — Hero + 卡片网格

**Files:**
- Modify: `frontend/src/views/HomeView.vue`

- [ ] **Step 1: 读取当前 HomeView.vue**

Read the file to understand the full template structure.

- [ ] **Step 2: 重写 Hero 区域**

将极光渐变 Hero（第 93-130 行）替换为白底 Airbnb 风格:

```vue
<!-- Hero — 白底 + 搜索条 -->
<div :style="{ textAlign: 'center', padding: '80px 32px 64px' }">
  <h1 :style="{
    fontFamily: 'var(--font-family)',
    fontSize: '28px',
    fontWeight: 700,
    lineHeight: 1.43,
    color: 'var(--color-ink)',
    margin: '0 0 8px',
    letterSpacing: '0',
  }">
    用文字记录思考
  </h1>
  <p :style="{
    fontSize: '16px',
    color: 'var(--color-muted)',
    margin: '0 auto 32px',
    maxWidth: '480px',
  }">
    分享技术见解与日常感悟
  </p>

  <!-- Search Pill — Airbnb style -->
  <div :style="{ maxWidth: '500px', margin: '0 auto' }">
    <NInput
      v-model:value="searchKeyword"
      placeholder="搜索文章..."
      clearable
      round
      size="large"
      :style="{
        '--n-border': '1px solid var(--color-hairline)',
        '--n-color': 'var(--color-canvas)',
        '--n-color-focus': 'var(--color-canvas)',
        '--n-text-color': 'var(--color-ink)',
        '--n-placeholder-color': 'var(--color-muted)',
        '--n-height': '56px',
        '--n-font-size': '16px',
        '--n-border-radius': '9999px',
        '--n-box-shadow-focus': 'var(--shadow-card)',
      }"
    >
      <template #prefix>
        <NIcon :component="Search" />
      </template>
    </NInput>
  </div>
</div>
```

- [ ] **Step 3: 重写卡片列表为 CSS Grid 布局**

替换筛选栏的 glass class 为 inline styles:

```vue
<!-- 筛选栏 -->
<div :style="{
  background: 'var(--color-canvas)',
  border: '1px solid var(--color-hairline-soft)',
  borderRadius: '14px',
  padding: '14px 20px',
  marginBottom: '24px',
}">
  <NSpace :size="12" style="width: 100%;">
    <NSelect
      v-model:value="selectedCategory"
      :options="categories.map(c => ({ label: c.name, value: c.id }))"
      placeholder="分类筛选"
      clearable
      style="width: 150px;"
    />
    <NSelect
      v-model:value="selectedTag"
      :options="tags.map(t => ({ label: t.name, value: t.id }))"
      placeholder="标签筛选"
      clearable
      style="width: 150px;"
    />
    <NButton text @click="clearFilters">清除筛选</NButton>
    <div style="flex: 1;" />
    <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
      写文章
    </NButton>
  </NSpace>
</div>
```

- [ ] **Step 4: 将文章列表改为 2 列网格**

```vue
<div v-else :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }">
  <div
    v-for="article in articles"
    :key="article.id"
    @click="router.push(`/article/${article.id}`)"
  >
    <ArticleCard :article="article" />
  </div>
</div>
```

- [ ] **Step 5: 移除 `margin: -32px` 的外部 div 包裹**

将模板最外层的 `<div style="margin: -32px;">` 删除。

---

### Task 13: 改造 ArticleDetail.vue — 双栏布局

**Files:**
- Modify: `frontend/src/views/ArticleDetail.vue`

- [ ] **Step 1: 读取当前 ArticleDetail.vue 全文**

- [ ] **Step 2: 重写为双栏布局**

主要结构改为:
```vue
<template>
  <div :style="{ display: 'flex', gap: '32px', maxWidth: '1080px', margin: '0 auto' }">
    <!-- 左栏: 内容 64% -->
    <div :style="{ flex: '1 1 0%', minWidth: 0 }">
      <!-- 面包屑 + 标题 + 作者行（含 identicon）+ 正文 + 评论区 -->
    </div>
    <!-- 右栏: 侧边 32% -->
    <div :style="{ width: '300px', flexShrink: 0 }">
      <!-- Sticky: 目录 + 点赞/收藏 -->
      <div :style="{
        position: 'sticky',
        top: '112px',
        border: '1px solid var(--color-hairline-soft)',
        borderRadius: '14px',
        padding: '20px',
        boxShadow: 'var(--shadow-card)',
      }">
        <TableOfContents ... />
        <div :style="{ height: '1px', background: 'var(--color-hairline-soft)', margin: '16px 0' }" />
        <LikeButton ... />
        <FavoriteButton ... />
      </div>
    </div>
  </div>
</template>
```

作者行添加头像:
```vue
<div :style="{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '24px' }">
  <img
    :src="getIdenticonUrl(article.author?.username || 'anonymous', article.author?.avatar, 40)"
    :style="{ width: '40px', height: '40px', borderRadius: '8px' }"
    alt=""
  />
  <div>
    <div :style="{ fontSize: '14px', fontWeight: 600, color: 'var(--color-ink)' }">
      {{ article.author?.username }}
    </div>
    <div :style="{ fontSize: '13px', color: 'var(--color-muted)' }">
      {{ formatDate(article.published_at || article.created_at) }} · {{ article.view_count }} 阅读
    </div>
  </div>
</div>
```

添加 `<script setup>` import:
```typescript
import { getIdenticonUrl } from '../utils/identicon'
```

---

### Task 14: 改造 ArticleEditor.vue — 干净表单

**Files:**
- Modify: `frontend/src/views/ArticleEditor.vue`

- [ ] **Step 1: 读取当前 ArticleEditor.vue 全文**

- [ ] **Step 2: 移除所有 glass 卡片包裹**

将表单字段改为直接平铺，使用 stacked label 风格:

```vue
<!-- Title field -->
<div :style="{ marginBottom: '20px' }">
  <div :style="{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink)', marginBottom: '6px' }">标题</div>
  <NInput
    v-model:value="title"
    placeholder="输入文章标题..."
    size="large"
    :style="{ '--n-border-radius': '8px' }"
  />
</div>
```

- [ ] **Step 3: 按钮组改为 Airbnb 风格**

```vue
<div :style="{ display: 'flex', gap: '12px', alignItems: 'center', justifyContent: 'flex-end' }">
  <NButton
    :style="{
      color: 'var(--color-ink)',
      border: '1px solid var(--color-ink)',
      borderRadius: '8px',
      fontWeight: 500,
    }"
    @click="saveDraft"
  >
    存草稿
  </NButton>
  <NButton
    type="primary"
    :style="{ borderRadius: '8px', fontWeight: 500 }"
    @click="publish"
  >
    发布
  </NButton>
</div>
```

---

### Task 15: 改造 LoginView.vue — 极简表单

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

- [ ] **Step 1: 读取当前 LoginView.vue 全文**

- [ ] **Step 2: 重写为极简居中表单**

移除玻璃卡片包裹，表单直接居中在白底上:

```vue
<template>
  <div :style="{
    maxWidth: '360px',
    margin: '0 auto',
    padding: '80px 0',
  }">
    <h1 :style="{ fontSize: '24px', fontWeight: 700, color: 'var(--color-ink)', marginBottom: '4px' }">
      {{ isRegister ? '注册' : '登录' }}
    </h1>
    <p :style="{ fontSize: '14px', color: 'var(--color-muted)', marginBottom: '32px' }">
      {{ isRegister ? '创建你的账号' : '欢迎回来' }}
    </p>

    <!-- Username -->
    <div :style="{ marginBottom: '16px' }">
      <div :style="{ fontSize: '13px', fontWeight: 500, color: 'var(--color-ink)', marginBottom: '6px' }">用户名</div>
      <NInput
        v-model:value="username"
        placeholder="输入用户名"
        size="large"
        :style="{ '--n-border-radius': '8px' }"
      />
    </div>

    <!-- Password -->
    <div :style="{ marginBottom: '24px' }">
      <div :style="{ fontSize: '13px', fontWeight: 500, color: 'var(--color-ink)', marginBottom: '6px' }">密码</div>
      <NInput
        v-model:value="password"
        type="password"
        placeholder="输入密码"
        size="large"
        :style="{ '--n-border-radius': '8px' }"
      />
    </div>

    <!-- Submit -->
    <NButton
      type="primary"
      block
      size="large"
      :loading="loading"
      :style="{ borderRadius: '8px', height: '48px', fontWeight: 500, fontSize: '15px' }"
      @click="handleSubmit"
    >
      {{ isRegister ? '注册' : '登录' }}
    </NButton>

    <!-- Toggle -->
    <div :style="{ textAlign: 'center', marginTop: '16px', fontSize: '13px', color: 'var(--color-muted)' }">
      {{ isRegister ? '已有账号？' : '还没有账号？' }}
      <NButton text type="primary" @click="isRegister = !isRegister">
        {{ isRegister ? '登录' : '注册' }}
      </NButton>
    </div>
  </div>
</template>
```

---

### Task 16: 改造 ProfileView.vue — 个人主页

**Files:**
- Modify: `frontend/src/views/ProfileView.vue`

- [ ] **Step 1: 读取并重写 ProfileView**

关键改动:
- 头像居中顶部（80px identicon）
- 统计数字横排
- 操作按钮 Rausch 色
- 文章列表卡片网格
- 移除毛玻璃样式

---

### Task 17: 改造 FavoritesView.vue / DraftsView.vue

**Files:**
- Modify: `frontend/src/views/FavoritesView.vue`
- Modify: `frontend/src/views/DraftsView.vue`

- [ ] **Step 1: 统一改造两个页面**

关键改动:
- Tab 筛选: pill 按钮组（Ink 底 = 选中，浅灰底 = 未选中）
- 文章列表: 2 列卡片网格
- 空状态: 统一居中样式
- 移除所有 `glass` class

---

### Task 18: 改造 SettingsView.vue

**Files:**
- Modify: `frontend/src/views/SettingsView.vue`

- [ ] **Step 1: 读取并重写 SettingsView**

关键改动:
- Stacked label 表单布局
- Input 统一 8px 圆角 + 1px hairline
- 保存按钮 Rausch primary
- 移除毛玻璃卡片

---

### Task 19: 改造管理后台 — UserManage.vue

**Files:**
- Modify: `frontend/src/views/admin/UserManage.vue`

- [ ] **Step 1: 读取当前文件**

- [ ] **Step 2: 重写表格为 Airbnb 风格**

关键改动:
- 表头: 浅灰底色 + uppercase + letter-spacing
- 用户行: 28px identicon 头像 + 用户名
- 角色列: 浅灰 pill 标签
- 状态: 彩色圆点指示
- 操作: Rausch 链接色
- 分页器: Airbnb 风格

---

### Task 20: 改造管理后台 — CategoryManage / TagManage / AuditLogs

**Files:**
- Modify: `frontend/src/views/admin/CategoryManage.vue`
- Modify: `frontend/src/views/admin/TagManage.vue`
- Modify: `frontend/src/views/admin/AuditLogs.vue`

- [ ] **Step 1: 三个页面统一应用 Task 19 的表格风格**

与 UserManage 一致: 浅灰表头、pagination 样式、卡片边框替换。

---

### Task 21: 最终验证 — 完整构建 + 功能检查

- [ ] **Step 1: TypeScript 类型检查**

Run: `cd C:\Mywebsite_2\frontend; npx vue-tsc -b`
Expected: 无错误

- [ ] **Step 2: Vite 构建**

Run: `cd C:\Mywebsite_2\frontend; npm run build`
Expected: 构建成功

- [ ] **Step 3: 视觉回归检查清单**

- [ ] 亮色模式: 所有页面白底 + Rausch 品牌色
- [ ] 暗色模式: 切换后深灰底 + #ff5a7a 品牌色
- [ ] 导航栏: 80px 高, 底部分割线, 活跃 tab 下划线
- [ ] 首页: 白底 Hero + 2 列卡片网格 + 搜索 pill
- [ ] 卡片: Photo-first + 默认封面渐变 + hover 阴影
- [ ] 详情: 双栏布局, identicon 头像, sticky 侧边栏
- [ ] 编辑器: 干净表单, stacked labels
- [ ] 登录: 极简居中表单
- [ ] 管理: 清爽表格
- [ ] 评论: identicon 头像显示

- [ ] **Step 4: Commit 最终变更**

---

## 实施顺序

```
Layer 1: Task 1-5   (设计令牌 + 入口文件 + ThemeOverrides)
    ↓
Layer 2: Task 6     (AppLayout 导航栏)
    ↓
Layer 3: Task 7-11  (通用组件: Card, CommentItem, CommentSection, GlassCard)
    ↓
Layer 4: Task 12-20 (视图页面: Home → Detail → Editor → Login → Profile → Favorites/Drafts → Settings → Admin)
    ↓
Verify: Task 21     (构建 + 视觉检查)
```

# 博客动效系统 + 封面图移除 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为博客全部 6 个页面添加 GSAP 驱动的大胆创意动效，同时移除长期不可用的封面图功能。

**Architecture:** 分 4 层执行 —— Layer 1（3 个 composable + 2 项全局基础设施）、Layer 2（封面图移除 3 个组件）、Layer 3（6 个页面动效改造）、Layer 4（最终验证清理）。每层内任务独立可并行。

**Tech Stack:** GSAP 3 + ScrollTrigger + Flip, Vue 3 Composition API, Naive UI, TypeScript

---

### Task 1: useScrollReveal composable

**Files:**
- Create: `frontend/src/composables/useScrollReveal.ts`

**Purpose:** 封装 GSAP ScrollTrigger 统一滚动揭示逻辑，所有视图复用。

- [ ] **Step 1: 创建 composable**

```typescript
// frontend/src/composables/useScrollReveal.ts
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { onBeforeUnmount } from 'vue'

gsap.registerPlugin(ScrollTrigger)

export interface ScrollRevealOptions {
  y?: number
  duration?: number
  stagger?: number
  ease?: string
  start?: string
}

export function useScrollReveal(
  target: string | Element | Element[],
  options: ScrollRevealOptions = {}
) {
  const {
    y = 30,
    duration = 0.6,
    stagger = 0,
    ease = 'power2.out',
    start = 'top 85%',
  } = options

  const ctx = gsap.context(() => {
    const els = typeof target === 'string'
      ? document.querySelectorAll(target)
      : Array.isArray(target) ? target : [target]

    if (!els || els.length === 0) return

    gsap.fromTo(
      els as Element[],
      { opacity: 0, y },
      {
        opacity: 1,
        y: 0,
        duration,
        stagger,
        ease,
        scrollTrigger: {
          trigger: Array.isArray(target) || typeof target === 'string' ? (els[0] as Element) : target as Element,
          start,
          toggleActions: 'play none none none',
        },
      }
    )
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })

  return ctx
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useScrollReveal.ts
git commit -m "feat: add useScrollReveal composable with GSAP ScrollTrigger"
```

---

### Task 2: useCustomCursor composable + DynamicCursor component

**Files:**
- Create: `frontend/src/composables/useCustomCursor.ts`
- Create: `frontend/src/components/DynamicCursor.vue`

**Purpose:** 自定义圆形光标 + 点击涟漪效果，在 App.vue 全局挂载。

- [ ] **Step 1: 创建 useCustomCursor composable**

```typescript
// frontend/src/composables/useCustomCursor.ts
import { ref, onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'

export function useCustomCursor() {
  const cursorPos = ref({ x: -100, y: -100 })
  const cursorHover = ref(false)
  const ripples = ref<Array<{ id: number; x: number; y: number }>>([])
  let rippleId = 0

  function onMouseMove(e: MouseEvent) {
    cursorPos.value = { x: e.clientX, y: e.clientY }
  }

  function onMouseDown(e: MouseEvent) {
    ripples.value.push({ id: ++rippleId, x: e.clientX, y: e.clientY })
    setTimeout(() => {
      ripples.value = ripples.value.filter(r => r.id !== rippleId)
    }, 600)
  }

  function onMouseEnterLink() { cursorHover.value = true }
  function onMouseLeaveLink() { cursorHover.value = false }

  function bindHoverTargets() {
    const targets = document.querySelectorAll('a, button, [role="button"], input, textarea, .card, .n-button, .n-base-selection, .n-tag, .toc-link, .nav-item')
    targets.forEach(el => {
      el.addEventListener('mouseenter', onMouseEnterLink)
      el.addEventListener('mouseleave', onMouseLeaveLink)
    })
  }

  function unbindHoverTargets() {
    const targets = document.querySelectorAll('a, button, [role="button"], input, textarea, .card, .n-button, .n-base-selection, .n-tag, .toc-link, .nav-item')
    targets.forEach(el => {
      el.removeEventListener('mouseenter', onMouseEnterLink)
      el.removeEventListener('mouseleave', onMouseLeaveLink)
    })
  }

  function isMobile() {
    return window.matchMedia('(max-width: 768px)').matches || window.matchMedia('(pointer: coarse)').matches
  }

  const enabled = !isMobile()

  onMounted(() => {
    if (!enabled) return
    document.body.style.cursor = 'none'
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mousedown', onMouseDown)
    bindHoverTargets()
    const observer = new MutationObserver(() => {
      unbindHoverTargets()
      bindHoverTargets()
    })
    observer.observe(document.body, { childList: true, subtree: true })
    onBeforeUnmount(() => observer.disconnect())
  })

  onBeforeUnmount(() => {
    if (!enabled) return
    document.body.style.cursor = ''
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mousedown', onMouseDown)
    unbindHoverTargets()
  })

  return { cursorPos, cursorHover, ripples, enabled }
}
```

- [ ] **Step 2: 创建 DynamicCursor 组件**

```vue
<!-- frontend/src/components/DynamicCursor.vue -->
<script setup lang="ts">
import { useCustomCursor } from '../composables/useCustomCursor'

const { cursorPos, cursorHover, ripples, enabled } = useCustomCursor()
</script>

<template>
  <div v-if="enabled" style="position: fixed; inset: 0; pointer-events: none; z-index: 99999;">
    <!-- Main cursor dot -->
    <div
      :style="{
        position: 'fixed',
        left: `${cursorPos.x}px`,
        top: `${cursorPos.y}px`,
        width: cursorHover ? '12px' : '20px',
        height: cursorHover ? '12px' : '20px',
        borderRadius: '50%',
        border: `1px solid var(--color-primary)`,
        background: cursorHover ? 'var(--color-primary)' : 'transparent',
        transform: 'translate(-50%, -50%)',
        transition: 'width 0.2s ease, height 0.2s ease, background 0.2s ease',
        opacity: 0.6,
      }"
    />
    <!-- Ripples -->
    <div
      v-for="r in ripples"
      :key="r.id"
      :style="{
        position: 'fixed',
        left: `${r.x}px`,
        top: `${r.y}px`,
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        border: '1px solid var(--color-primary)',
        transform: 'translate(-50%, -50%)',
        opacity: 0,
        animation: 'cursor-ripple 0.6s ease-out forwards',
      }"
    />
  </div>
</template>

<style>
@keyframes cursor-ripple {
  0% { transform: translate(-50%, -50%) scale(0); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/composables/useCustomCursor.ts frontend/src/components/DynamicCursor.vue
git commit -m "feat: add custom cursor with click ripple effect"
```

---

### Task 3: useParallax composable

**Files:**
- Create: `frontend/src/composables/useParallax.ts`

**Purpose:** 多速视差滚动，用于 Hero 区域和文章封面。

- [ ] **Step 1: 创建 composable**

```typescript
// frontend/src/composables/useParallax.ts
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { onBeforeUnmount } from 'vue'

gsap.registerPlugin(ScrollTrigger)

export interface ParallaxTarget {
  el: string | Element
  speed: number  // 0 = fixed, 1 = normal scroll, 0.5 = half speed
}

export function useParallax(targets: ParallaxTarget[]) {
  const ctx = gsap.context(() => {
    for (const { el, speed } of targets) {
      const element = typeof el === 'string' ? document.querySelector(el) : el
      if (!element) continue

      gsap.to(element, {
        y: () => `${(speed - 1) * 100}%`,
        ease: 'none',
        scrollTrigger: {
          trigger: element,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
      })
    }
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })

  return ctx
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useParallax.ts
git commit -m "feat: add useParallax composable for multi-speed scroll effects"
```

---

### Task 4: App.vue — 页面过渡动画 + 全局光标挂载

**Files:**
- Modify: `frontend/src/App.vue`

**Purpose:** 添加 GSAP 驱动的页面淡入过渡，挂载 DynamicCursor，初始化 GSAP matchMedia。

- [ ] **Step 1: 读取当前 App.vue 完整内容**

当前 App.vue 结构：
```vue
<script setup lang="ts">
import { ref, watchEffect, onMounted } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import AppLayout from './components/AppLayout.vue'

const THEME_KEY = 'blog-theme'

function getSavedTheme(): boolean { ... }
const isDark = ref(getSavedTheme())

onMounted(() => { ... })
watchEffect(() => { ... })
// ... theme overrides ...
</script>

<template>
  <NConfigProvider ...>
    <NMessageProvider>
      <NDialogProvider>
        <AppLayout v-model:dark="isDark">
          <RouterView v-slot="{ Component, route: r }">
            <component :is="Component" :key="r.fullPath" />
          </RouterView>
        </AppLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
```

- [ ] **Step 2: 修改 script setup — 添加 GSAP 页面过渡逻辑**

在 script setup 中追加以下代码（在 `watchEffect` 之后）：

```typescript
import { gsap } from 'gsap'
import { useRoute } from 'vue-router'
import DynamicCursor from './components/DynamicCursor.vue'

const route = useRoute()

// GSAP matchMedia for responsive + reduced-motion
const mm = gsap.matchMedia()

mm.add('(prefers-reduced-motion: no-preference)', () => {
  // Animations enabled — nothing to configure globally
})

// Page transition: watch route changes
watch(
  () => route.fullPath,
  () => {
    // Animate page content on next tick after mount
    import('vue').then(({ nextTick }) => {
      nextTick(() => {
        const page = document.querySelector('.page-content')
        if (page) {
          gsap.fromTo(
            page,
            { opacity: 0, y: 8 },
            { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' }
          )
        }
      })
    })
  }
)
```

- [ ] **Step 3: 修改 template — 挂载 DynamicCursor + 包装过渡容器**

```html
<template>
  <NConfigProvider :theme="isDark ? darkTheme : undefined" :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <DynamicCursor />
        <AppLayout v-model:dark="isDark">
          <RouterView v-slot="{ Component, route: r }">
            <div class="page-content" :key="r.fullPath">
              <component :is="Component" />
            </div>
          </RouterView>
        </AppLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: add GSAP page transitions and custom cursor mount"
```

---

### Task 5: AppLayout — 导航栏滚动变形

**Files:**
- Modify: `frontend/src/components/AppLayout.vue`

**Purpose:** 滚动时导航栏从 80px 缩小到 56px，背景变为毛玻璃。

- [ ] **Step 1: 修改 AppLayout.vue script setup**

在 script setup 中追加：

```typescript
import { onMounted, onBeforeUnmount, ref } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const headerScrolled = ref(false)

onMounted(() => {
  ScrollTrigger.create({
    start: 'top -50',
    end: 'max',
    onEnter: () => { headerScrolled.value = true },
    onLeaveBack: () => { headerScrolled.value = false },
  })
})
```

- [ ] **Step 2: 修改 NLayoutHeader 动态绑定样式**

将 `NLayoutHeader` 的静态 `height: '80px'` 改为动态：

```html
<NLayoutHeader
  :style="{
    padding: '0 40px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    height: headerScrolled ? '56px' : '80px',
    background: headerScrolled
      ? 'color-mix(in srgb, var(--color-canvas) 85%, transparent)'
      : 'var(--color-canvas)',
    borderBottom: '1px solid var(--color-hairline-soft)',
    transition: 'height 0.3s ease, background 0.3s ease',
    backdropFilter: headerScrolled ? 'blur(12px)' : 'none',
    WebkitBackdropFilter: headerScrolled ? 'blur(12px)' : 'none',
  }"
>
```

- [ ] **Step 3: Logo 字号动态缩放**

将 Logo NText 的 fontSize 改为：
```html
:style="{
  fontSize: headerScrolled ? '18px' : '20px',
  cursor: 'pointer',
  fontWeight: 700,
  color: 'var(--color-primary)',
  letterSpacing: '-0.3px',
  transition: 'font-size 0.3s ease',
}"
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AppLayout.vue
git commit -m "feat: add nav scroll shrink with glassmorphism backdrop"
```

---

### Task 6: ArticleCard — 移除封面，纯文字卡片

**Files:**
- Modify: `frontend/src/components/ArticleCard.vue`

**Purpose:** 删除封面区域（img + 渐变 emoji），卡片变为纯文字布局。

- [ ] **Step 1: 替换 ArticleCard 完整内容**

```vue
<script setup lang="ts">
import { NTag, NText, NSpace } from 'naive-ui'
import type { ArticleInfo } from '../types/api'

const props = defineProps<{ article: ArticleInfo }>()

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
      padding: '20px',
      transition: 'box-shadow 0.3s ease, transform 0.3s ease',
    }"
  >
    <!-- Badges row -->
    <div :style="{ display: 'flex', gap: '6px', marginBottom: '10px', flexWrap: 'wrap' }">
      <NTag v-if="article.is_pinned" type="error" size="small" :bordered="false" round>精选</NTag>
      <NTag v-if="article.is_draft" type="warning" size="small" :bordered="false">草稿</NTag>
      <NTag v-if="article.category" size="small" :bordered="false">{{ article.category.name }}</NTag>
    </div>

    <!-- Title -->
    <NText
      tag="h3"
      :style="{
        fontSize: '17px',
        fontWeight: 600,
        lineHeight: 1.3,
        marginBottom: article.summary ? '6px' : '10px',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
        color: 'var(--color-ink)',
      }"
    >
      {{ article.title }}
    </NText>

    <!-- Summary -->
    <NText
      v-if="article.summary"
      depth="2"
      :style="{
        fontSize: '14px',
        marginBottom: '10px',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
      }"
    >
      {{ article.summary }}
    </NText>

    <!-- Footer -->
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

    <!-- Tags -->
    <NSpace v-if="article.tags && article.tags.length" :style="{ marginTop: '8px' }">
      <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
        {{ tag.name }}
      </NTag>
    </NSpace>
  </div>
</template>
```

- [ ] **Step 2: 删除不再需要的 imports 和 scoped style**

确认删除了：
- `import { ref } from 'vue'`
- `import { getCoverForArticle } from '../utils/covers'`
- `:hover img` scoped style（移除或保留但不影响）

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ArticleCard.vue
git commit -m "refactor: remove cover image from ArticleCard, pure text layout"
```

---

### Task 7: ArticleDetail — 移除封面图 + 阅读进度条 + 点赞粒子

**Files:**
- Modify: `frontend/src/views/ArticleDetail.vue`

**Purpose:** 删除封面图展示区，添加阅读进度条和点赞粒子爆发效果。

- [ ] **Step 1: 删除封面图相关代码**

删除 template 中 lines 134-151（`<!-- 封面图 -->` 块）：
```html
<!-- 封面图 -->
<div v-if="article.cover_image" ...>
  <img :src="article.cover_image" ... />
</div>
```

- [ ] **Step 2: 添加阅读进度条**

在 script setup 中添加：

```typescript
import { onMounted as onMountedGSAP, onBeforeUnmount } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const progressPercent = ref(0)

onMounted(() => {
  const progressCtx = gsap.context(() => {
    ScrollTrigger.create({
      trigger: '.article-content',
      start: 'top bottom',
      end: 'bottom bottom',
      onUpdate: (self) => {
        progressPercent.value = Math.round(self.progress * 100)
      },
    })
  })

  onBeforeUnmount(() => {
    progressCtx.revert()
  })
})
```

在 template 最顶部（NLayoutContent 范围内）添加：

```html
<!-- Reading progress bar -->
<div
  :style="{
    position: 'fixed',
    top: 0,
    left: 0,
    height: '2px',
    width: `${progressPercent}%`,
    background: 'var(--color-primary)',
    zIndex: 200,
    transition: 'width 0.1s linear',
  }"
/>
```

- [ ] **Step 3: 添加点赞粒子爆发**

修改 LikeButton 的包装 div，添加粒子容器。在 script setup 中添加：

```typescript
const likeParticles = ref<Array<{ id: number; x: number; y: number }>>([])
let likeParticleId = 0

function spawnLikeParticles(event: MouseEvent) {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  for (let i = 0; i < 10; i++) {
    const id = ++likeParticleId
    const angle = (Math.PI * 2 * i) / 10
    const distance = 30 + Math.random() * 20
    likeParticles.value.push({ id, x: cx + Math.cos(angle) * distance, y: cy + Math.sin(angle) * distance })
    setTimeout(() => {
      likeParticles.value = likeParticles.value.filter(p => p.id !== id)
    }, 800)
  }
}
```

在 template 侧边栏的 LikeButton 外面包装：

```html
<div style="position: relative;" @click="spawnLikeParticles">
  <LikeButton ... />
  <!-- Particles -->
  <div
    v-for="p in likeParticles"
    :key="p.id"
    :style="{
      position: 'fixed',
      left: `${p.x}px`,
      top: `${p.y}px`,
      width: '6px',
      height: '6px',
      borderRadius: '50%',
      background: 'var(--color-primary)',
      pointerEvents: 'none',
      zIndex: 9999,
      animation: 'like-particle 0.8s ease-out forwards',
    }"
  />
</div>
```

在 `<style>` 中添加：

```css
@keyframes like-particle {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.8; }
  100% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/ArticleDetail.vue
git commit -m "feat: remove cover image, add reading progress bar and like particles"
```

---

### Task 8: ArticleEditor — 移除封面图 + 流畅动效

**Files:**
- Modify: `frontend/src/views/ArticleEditor.vue`
- Modify: `frontend/src/composables/useDraftSave.ts`
- Delete: `frontend/src/utils/covers.ts`

**Purpose:** 删除封面图上传区域和 ImageUpload 引用，添加发布按钮脉冲和保存波纹。

- [ ] **Step 1: 修改 ArticleEditor script setup**

删除以下 imports 和变量：
```typescript
// 删除这些行:
import ImageUpload from '../components/ImageUpload.vue'
const coverImage = ref('')
const showImageUpload = ref(false)
```

删除 `getDraftData()` 中的 `cover_image: coverImage.value`。

删除 `handleImageUpload` 函数。

删除 `insertCoverImage` 函数。

在 watch 列表中删除 `coverImage`。

在 payload 中删除 `cover_image` 字段。

- [ ] **Step 2: 修改 ArticleEditor template**

删除封面图区块（封面图 NInput + 上传按钮 + 图片预览 + ImageUpload 弹窗）。

删除 `<NModal v-model:show="showImageUpload">` 整个块。

- [ ] **Step 3: 添加发布按钮脉冲动画**

在 `<style>` 块追加（如果不存在则添加）：

```css
@keyframes publish-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 56, 92, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(255, 56, 92, 0); }
}

.publish-btn {
  animation: publish-pulse 2s ease infinite;
}
```

给发布按钮添加 class：
```html
<NButton
  type="primary"
  class="publish-btn"
  ...
>
```

- [ ] **Step 4: 修改 useDraftSave.ts — 删除 cover_image 字段**

```typescript
// 从 DraftData 接口中删除:
cover_image: string

// 从 getDraftData() 中删除 cover_image 相关行
```

- [ ] **Step 5: 删除 covers.ts**

```bash
git rm frontend/src/utils/covers.ts
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/ArticleEditor.vue frontend/src/composables/useDraftSave.ts frontend/src/utils/covers.ts
git commit -m "refactor: remove cover image from editor, delete covers.ts, add publish pulse"
```

---

### Task 9: HomeView — Hero 弹性入场 + 3D Tilt 卡片

**Files:**
- Modify: `frontend/src/views/HomeView.vue`

**Purpose:** Hero 区域标题弹性入场动画，文章卡片 3D 倾斜跟随鼠标。

- [ ] **Step 1: 添加 Hero 弹性入场**

在 script setup 中添加：

```typescript
import { onMounted, onBeforeUnmount, ref } from 'vue'
import gsap from 'gsap'

const heroRevealed = ref(false)

onMounted(() => {
  const ctx = gsap.context(() => {
    const tl = gsap.timeline()
    tl.fromTo('.hero-title', { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.8, ease: 'elastic.out(1, 0.5)' })
    tl.fromTo('.hero-subtitle', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, '-=0.2')
    tl.fromTo('.hero-search', { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.5)' }, '-=0.1')
    tl.eventCallback('onComplete', () => { heroRevealed.value = true })
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })
})
```

- [ ] **Step 2: 给 Hero 元素添加 CSS class**

```html
<h1 class="hero-title" :style="{ ... }">用文字记录思考</h1>
<p class="hero-subtitle" :style="{ ... }">分享技术见解与日常感悟</p>
<div class="hero-search" :style="{ ... }">
  <NInput ... />
</div>
```

- [ ] **Step 3: 添加卡片 3D Tilt 效果 composable 调用**

在 script setup 中添加 3D tilt 逻辑：

```typescript
function handleCardMouseMove(e: MouseEvent, el: HTMLElement) {
  const rect = el.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  gsap.to(el, {
    rotateX: -y * 8,
    rotateY: x * 8,
    transformPerspective: 600,
    duration: 0.4,
    ease: 'power2.out',
  })
  // Glow follow
  const glow = el.querySelector('.card-glow') as HTMLElement
  if (glow) {
    glow.style.background = `radial-gradient(circle at ${(x + 0.5) * 100}% ${(y + 0.5) * 100}%, rgba(255,56,92,0.08), transparent 60%)`
  }
}

function handleCardMouseLeave(el: HTMLElement) {
  gsap.to(el, {
    rotateX: 0,
    rotateY: 0,
    duration: 0.4,
    ease: 'back.out(1.5)',
  })
  const glow = el.querySelector('.card-glow') as HTMLElement
  if (glow) glow.style.background = 'transparent'
}
```

- [ ] **Step 4: 修改卡片 wrapper 绑定事件**

将 ArticleCard 的 wrapper div 改为：

```html
<div
  v-for="article in articles"
  :key="article.id"
  :ref="el => { if (el) cardRefs[article.id] = el as HTMLElement }"
  style="perspective: 600px;"
  @click="router.push(`/article/${article.id}`)"
  @mousemove="(e: MouseEvent) => handleCardMouseMove(e, ($event.target as HTMLElement).closest('.card-wrapper') as HTMLElement)"
  @mouseleave="(e: MouseEvent) => handleCardMouseLeave(($event.target as HTMLElement).closest('.card-wrapper') as HTMLElement)"
>
  <div class="card-wrapper" style="position: relative; border-radius: 14px; overflow: hidden;">
    <div class="card-glow" style="position: absolute; inset: 0; pointer-events: none; z-index: 1; transition: background 0.3s ease;" />
    <ArticleCard :article="article" />
  </div>
</div>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/HomeView.vue
git commit -m "feat: add Hero bounce-in animation and 3D tilt cards to homepage"
```

---

### Task 10: LoginView — 品牌仪式感入场

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

**Purpose:** Logo 弹性入场 + 表单淡入 + 渐变色块背景动画。

- [ ] **Step 1: 添加入场动画**

在 script setup 中添加：

```typescript
import { onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'

onMounted(() => {
  const ctx = gsap.context(() => {
    const tl = gsap.timeline()
    tl.fromTo('.login-form', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' })
    // Animate background blobs
    gsap.to('.login-blob-1', {
      x: '10%', y: '-15%',
      duration: 20,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
    gsap.to('.login-blob-2', {
      x: '-8%', y: '10%',
      duration: 18,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })
})
```

- [ ] **Step 2: 添加背景色块和表单 class**

在 template 最外层 wrapper 修改：

```html
<div style="max-width: 360px; margin: 0 auto; padding: 80px 0; position: relative;">
  <!-- Background blobs -->
  <div class="login-blob-1" :style="{
    position: 'fixed',
    width: '400px',
    height: '400px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(255,56,92,0.08), transparent 70%)',
    top: '-100px',
    right: '-150px',
    pointerEvents: 'none',
    zIndex: 0,
    filter: 'blur(80px)',
  }" />
  <div class="login-blob-2" :style="{
    position: 'fixed',
    width: '300px',
    height: '300px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(255,56,92,0.06), transparent 70%)',
    bottom: '-80px',
    left: '-100px',
    pointerEvents: 'none',
    zIndex: 0,
    filter: 'blur(60px)',
  }" />

  <div class="login-form" style="position: relative; z-index: 1;">
    <!-- existing login/register form content -->
  </div>
</div>
```

将标题和表单内容包裹在 `<div class="login-form">` 中。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/LoginView.vue
git commit -m "feat: add brand entrance animation and gradient blobs to login"
```

---

### Task 11: FavoritesView + DraftsView — 3D 列表项 + 空状态动画

**Files:**
- Modify: `frontend/src/views/FavoritesView.vue`
- Modify: `frontend/src/views/DraftsView.vue`

**Purpose:** 列表页使用 3D tilt（轻度版 4deg），空状态有呼吸缩放动画。

- [ ] **Step 1: 修改 FavoritesView.vue**

添加 GSAP 滚动揭示：

```typescript
import { onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'

onMounted(() => {
  const ctx = gsap.context(() => {
    // Stagger reveal for list items
    gsap.fromTo('.fav-item', {
      opacity: 0, x: 20,
    }, {
      opacity: 1, x: 0,
      duration: 0.5,
      stagger: 0.06,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: '.fav-grid',
        start: 'top 85%',
        toggleActions: 'play none none none',
      },
    })
    // Empty state breathing
    gsap.to('.fav-empty', {
      scale: 1.03,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })
})
```

给每个元素添加 class：
- Grid 容器：`class="fav-grid"`
- 每个卡片 wrapper：`class="fav-item"`
- NEmpty：`class="fav-empty"`

与 HomeView 相同的 3D tilt 逻辑（max 4deg 而非 8deg）。

- [ ] **Step 2: 修改 DraftsView.vue（同理）**

相同的 stagger reveal + 3D tilt（max 4deg）+ 空状态呼吸。

```typescript
gsap.fromTo('.draft-item', {
  opacity: 0, x: 20,
}, {
  opacity: 1, x: 0,
  duration: 0.5,
  stagger: 0.06,
  ease: 'power2.out',
  scrollTrigger: {
    trigger: '.draft-grid',
    start: 'top 85%',
    toggleActions: 'play none none none',
  },
})
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/FavoritesView.vue frontend/src/views/DraftsView.vue
git commit -m "feat: add 3D tilt list items and empty state breathing to favorites/drafts"
```

---

### Task 12: SettingsView + ProfileView — 微交互动效

**Files:**
- Modify: `frontend/src/views/SettingsView.vue`
- Modify: `frontend/src/views/ProfileView.vue`

**Purpose:** 开关切换弹性触感，保存成功弹跳确认。

- [ ] **Step 1: 修改 SettingsView.vue**

在 `saveProfile` 和 `changePassword` 函数成功时添加弹跳动画：

```typescript
import gsap from 'gsap'

// 在 message.success 之后添加:
// 给保存按钮添加弹跳
nextTick(() => {
  const btn = document.querySelector('.save-btn') as HTMLElement
  if (btn) {
    gsap.fromTo(btn, { scale: 1 }, { scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: 'power2.out' })
  }
})
```

给保存按钮添加 class：`class="save-btn"`

开关弹性动画通过全局 CSS 处理：
```css
.n-switch .n-switch__button {
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

- [ ] **Step 2: 修改 ProfileView.vue**

添加 GSAP stagger 揭示用户信息卡片内容：

```typescript
import { onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'

onMounted(() => {
  const ctx = gsap.context(() => {
    gsap.fromTo('.profile-section > *', {
      opacity: 0, y: 16,
    }, {
      opacity: 1, y: 0,
      duration: 0.4,
      stagger: 0.05,
      ease: 'power2.out',
    })
  })

  onBeforeUnmount(() => {
    ctx.revert()
  })
})
```

给用户信息卡片添加 class：`class="profile-section"`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/SettingsView.vue frontend/src/views/ProfileView.vue
git commit -m "feat: add micro-interactions to settings and profile pages"
```

---

### Task 13: transitions.css — 清理旧动效

**Files:**
- Modify: `frontend/src/styles/transitions.css`

**Purpose:** 移除旧的 Glassmorphism 动效（aurora-shimmer 等），保留骨架屏和必要的 keyframes。

- [ ] **Step 1: 替换 transitions.css**

```css
/* ===== Blog Animation System ===== */

/* Skeleton Pulse */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.5; }
}
.skeleton-pulse {
  animation: skeleton-pulse 1.8s ease-in-out infinite;
  background: var(--color-surface-soft);
  border-radius: 6px;
}

/* Reduced motion: disable all non-essential animations */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/styles/transitions.css
git commit -m "refactor: clean up old glassmorphism animations, keep skeleton pulse"
```

---

### Task 14: 全局视差层 — HomeView Hero 区域

**Files:**
- Modify: `frontend/src/views/HomeView.vue`

**Purpose:** 在 HomeView 的 Hero 区域添加视差装饰元素（使用已创建的 useParallax）。

- [ ] **Step 1: 添加视差装饰圆**

在 HomeView 的 Hero div 内添加视差背景装饰：

```html
<!-- Parallax decoration circles -->
<div class="hero-parallax-1" :style="{
  position: 'absolute',
  width: '200px',
  height: '200px',
  borderRadius: '50%',
  border: '1px solid var(--color-primary)',
  opacity: 0.08,
  top: '-80px',
  right: '10%',
  pointerEvents: 'none',
}" />
<div class="hero-parallax-2" :style="{
  position: 'absolute',
  width: '120px',
  height: '120px',
  borderRadius: '50%',
  background: 'var(--color-primary)',
  opacity: 0.04,
  bottom: '-40px',
  left: '5%',
  pointerEvents: 'none',
}" />
```

- [ ] **Step 2: 使用 useParallax**

```typescript
import { useParallax } from '../composables/useParallax'

// in onMounted:
useParallax([
  { el: '.hero-parallax-1', speed: 0.3 },
  { el: '.hero-parallax-2', speed: 0.5 },
])
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/HomeView.vue
git commit -m "feat: add parallax decoration elements to homepage hero"
```

---

### Task 15: 最终验证 — 全量检查 + reduced-motion + 移动端降级

**Files:**
- Modify: `frontend/src/composables/useCustomCursor.ts` (已有移动端检测)
- Modify: `frontend/src/composables/useScrollReveal.ts` (已有 matchMedia 基础)
- Verify: 所有已修改文件

**Purpose:** 确保所有动画在 reduced-motion 和移动端正确降级。

- [ ] **Step 1: 验证清单**

检查以下项目：
1. `prefers-reduced-motion: reduce` 时 transitions.css 禁用所有动画
2. 移动端 (<768px) 自定义光标自动禁用（已实现）
3. 所有 GSAP context 在 `onBeforeUnmount` 中 `revert()`
4. 首页卡片 3D tilt 在触摸设备上不触发
5. ScrollTrigger 在窗口 resize 时刷新

- [ ] **Step 2: 添加移动端 touch 检测到 HomeView**

```typescript
const isTouchDevice = window.matchMedia('(pointer: coarse)').matches

// 仅在非触摸设备上绑定 tilt 事件
function handleCardMouseMove(...) {
  if (isTouchDevice) return
  // existing logic
}
```

- [ ] **Step 3: 确认所有 imports 无未使用引用**

运行 TypeScript 检查：
```bash
cd frontend && npx vue-tsc --noEmit
```

修复任何类型错误。

- [ ] **Step 4: 确认 covers.ts 引用已全部移除**

```bash
grep -r "covers" frontend/src --include="*.ts" --include="*.vue"
```
应无输出。

- [ ] **Step 5: 删除 ImageUpload.vue 引用（如仅在 editor 使用）**

检查是否还有其他地方引用 ImageUpload：
```bash
grep -r "ImageUpload" frontend/src --include="*.ts" --include="*.vue"
```
应仅在 ImageUpload.vue 自身中。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: final verification, mobile/touch degradation, type check"
```

---

## 任务依赖图

```
Layer 1 (可并行):
  Task 1 (useScrollReveal) ──┐
  Task 2 (useCustomCursor)  ──┼──→ Task 4 (App.vue 过渡+光标)
  Task 3 (useParallax)      ──┘      Task 5 (AppLayout 导航)

Layer 2 (封面移除，可并行):
  Task 6 (ArticleCard)       ──┐
  Task 7 (ArticleDetail)     ──┼──→ 所有视图可用新卡片
  Task 8 (ArticleEditor)     ──┘

Layer 3 (页面动效，依赖 Layer 1+2，内部可并行):
  Task  9 (HomeView Hero+Tilt+视差)
  Task 10 (LoginView 品牌入场)
  Task 11 (Favorites+Drafts)
  Task 12 (Settings+Profile)

Layer 4 (清理验证):
  Task 13 (transitions.css)
  Task 14 (HomeView 视差层)
  Task 15 (最终验证)
```

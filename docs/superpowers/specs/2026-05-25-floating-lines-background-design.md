# FloatingLines 动态背景集成设计

## 概述

将 React Bits 的 `FloatingLines` 组件适配为 Vue 3 SFC，作为全站全局 WebGL 动态背景。使用 Three.js 着色器渲染动画波浪线条，支持鼠标交互。

## 需求来源

- `background.md` — 用户提供的 React FloatingLines 组件参考
- 用户确认：全站背景、默认配色、全交互效果

## 架构

```
App.vue
├── NConfigProvider / NMessageProvider / NDialogProvider
│   ├── FloatingLines.vue        ← 新增：z-index: 0, position: fixed
│   ├── DynamicCursor.vue        
│   ├── AppLayout.vue            ← z-index: 1+
│   │   └── RouterView
```

## 组件设计

### FloatingLines.vue

**职责：** 全屏 Three.js WebGL 背景，渲染上下三层波浪线条，支持鼠标交互。

**Props：**

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| linesGradient | string[] | [] | 渐变颜色数组（hex），最多 8 色 |
| enabledWaves | string[] | ['top','middle','bottom'] | 启用的波浪层 |
| lineCount | number\|number[] | [6] | 每层线条数 |
| lineDistance | number\|number[] | [5] | 线条间距 |
| animationSpeed | number | 1 | 动画速度倍率 |
| interactive | boolean | true | 鼠标交互开关 |
| bendRadius | number | 5 | 鼠标弯曲影响半径 |
| bendStrength | number | -0.5 | 弯曲强度 |
| mouseDamping | number | 0.05 | 鼠标平滑系数 |
| parallax | boolean | true | 视差效果开关 |
| parallaxStrength | number | 0.2 | 视差强度 |
| mixBlendMode | string | 'screen' | CSS 混合模式 |

**App.vue 中使用配置：**
```html
<FloatingLines
  :lines-gradient="['#E947F5', '#2F4BA2']"
  :enabled-waves="['top', 'middle', 'bottom']"
  :line-count="[10, 15, 20]"
  :line-distance="[8, 6, 4]"
  :bend-radius="5"
  :bend-strength="-0.5"
  :interactive="true"
  :parallax="true"
  :animation-speed="0.6"
/>
```

## 技术细节

### React → Vue 翻译

| React | Vue 3 |
|---|---|
| useRef(null) | ref<HTMLElement>() + template ref |
| useEffect(setup, deps) | onMounted(setup) + watch(deps) |
| useState(init) | ref(init) |
| ref.current | ref.value |
| return cleanup | onUnmounted(cleanup) |

### Three.js 生命周期

1. `onMounted` — 创建 Scene、OrthographicCamera、WebGLRenderer、ShaderMaterial、PlaneGeometry
2. `ResizeObserver` — 监听容器大小，更新 renderer 尺寸和 iResolution
3. `requestAnimationFrame` — 渲染循环，更新 iTime 和鼠标 uniforms
4. `onUnmounted` — 清理所有资源（cancelAnimationFrame、dispose geometry/material/renderer、disconnect ResizeObserver、移除事件监听）

### 着色器

约 200 行 GLSL 原样保留。三层波浪（top/middle/bottom），每层独立控制线条数、间距、位置、旋转。鼠标交互通过 `bendRadius` 和 `bendStrength` 控制径向衰减弯曲，`mouseDamping` 控制平滑。

### 主题适配

- 固定配色 `['#E947F5', '#2F4BA2']`，不随明暗主题切换
- `mixBlendMode: 'screen'` 在亮/暗背景下均自然融合
- 不需要额外的主题切换逻辑

## 文件操作

| 文件 | 操作 | 说明 |
|---|---|---|
| frontend/src/components/FloatingLines.vue | 新建 | 约 400+ 行，含着色器 |
| frontend/src/App.vue | 修改 | 引入组件 + 模板中放置 |
| frontend/package.json | 修改 | 添加 `three` 依赖 |

## 性能注意事项

- `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))` 限制像素比
- `ResizeObserver` 而非 `window.resize` 事件，更高效
- `requestAnimationFrame` 自动在页面不可见时暂停
- 组件卸载时完全清理 WebGL 上下文

## 验证

1. `npm run dev` 启动 → 首页和所有页面均有动态线条背景
2. 移动鼠标 → 线条跟随弯曲 + 视差偏移
3. 切换明暗主题 → 背景线条配色不变，与两种主题均协调
4. 页面切换 → 背景不受路由变化影响（在 App.vue 根层）
5. 移动端 → 触摸交互正常，无性能问题

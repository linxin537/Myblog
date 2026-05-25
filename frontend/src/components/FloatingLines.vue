<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Clock, Mesh, OrthographicCamera, PlaneGeometry, Scene,
  ShaderMaterial, Vector2, Vector3, WebGLRenderer
} from 'three'

const MAX_GRADIENT_STOPS = 8

const props = withDefaults(defineProps<{
  linesGradient?: string[]
  enabledWaves?: string[]
  lineCount?: number | number[]
  lineDistance?: number | number[]
  topWavePosition?: { x: number; y: number; rotate: number }
  middleWavePosition?: { x: number; y: number; rotate: number }
  bottomWavePosition?: { x: number; y: number; rotate: number }
  animationSpeed?: number
  interactive?: boolean
  bendRadius?: number
  bendStrength?: number
  mouseDamping?: number
  parallax?: boolean
  parallaxStrength?: number
  mixBlendMode?: string
}>(), {
  linesGradient: () => [],
  enabledWaves: () => ['top', 'middle', 'bottom'],
  lineCount: () => [6],
  lineDistance: () => [5],
  topWavePosition: undefined,
  middleWavePosition: undefined,
  bottomWavePosition: () => ({ x: 2.0, y: -0.7, rotate: -1 }),
  animationSpeed: 1,
  interactive: true,
  bendRadius: 5.0,
  bendStrength: -0.5,
  mouseDamping: 0.05,
  parallax: true,
  parallaxStrength: 0.2,
  mixBlendMode: 'screen',
})

const containerRef = ref<HTMLElement>()

const vertexShader = /* glsl */ `
precision highp float;

void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`

const fragmentShader = /* glsl */ `
precision highp float;

uniform float iTime;
uniform vec3  iResolution;
uniform float animationSpeed;

uniform bool enableTop;
uniform bool enableMiddle;
uniform bool enableBottom;

uniform int topLineCount;
uniform int middleLineCount;
uniform int bottomLineCount;

uniform float topLineDistance;
uniform float middleLineDistance;
uniform float bottomLineDistance;

uniform vec3 topWavePosition;
uniform vec3 middleWavePosition;
uniform vec3 bottomWavePosition;

uniform vec2 iMouse;
uniform bool interactive;
uniform float bendRadius;
uniform float bendStrength;
uniform float bendInfluence;

uniform bool parallax;
uniform float parallaxStrength;
uniform vec2 parallaxOffset;

uniform vec3 lineGradient[8];
uniform int lineGradientCount;

const vec3 BLACK = vec3(0.0);
const vec3 PINK  = vec3(233.0, 71.0, 245.0) / 255.0;
const vec3 BLUE  = vec3(47.0,  75.0, 162.0) / 255.0;

mat2 rotate(float r) {
  return mat2(cos(r), sin(r), -sin(r), cos(r));
}

vec3 background_color(vec2 uv) {
  vec3 col = vec3(0.0);
  float y = sin(uv.x - 0.2) * 0.3 - 0.1;
  float m = uv.y - y;
  col += mix(BLUE, BLACK, smoothstep(0.0, 1.0, abs(m)));
  col += mix(PINK, BLACK, smoothstep(0.0, 1.0, abs(m - 0.8)));
  return col * 0.5;
}

vec3 getLineColor(float t, vec3 baseColor) {
  if (lineGradientCount <= 0) {
    return baseColor;
  }
  vec3 gradientColor;
  if (lineGradientCount == 1) {
    gradientColor = lineGradient[0];
  } else {
    float clampedT = clamp(t, 0.0, 0.9999);
    float scaled = clampedT * float(lineGradientCount - 1);
    int idx = int(floor(scaled));
    float f = fract(scaled);
    int idx2 = min(idx + 1, lineGradientCount - 1);
    vec3 c1 = lineGradient[idx];
    vec3 c2 = lineGradient[idx2];
    gradientColor = mix(c1, c2, f);
  }
  return gradientColor * 0.5;
}

float wave(vec2 uv, float offset, vec2 screenUv, vec2 mouseUv, bool shouldBend) {
  float time = iTime * animationSpeed;
  float x_offset   = offset;
  float x_movement = time * 0.1;
  float amp        = sin(offset + time * 0.2) * 0.3;
  float y          = sin(uv.x + x_offset + x_movement) * amp;
  if (shouldBend) {
    vec2 d = screenUv - mouseUv;
    float influence = exp(-dot(d, d) * bendRadius);
    float bendOffset = (mouseUv.y - screenUv.y) * influence * bendStrength * bendInfluence;
    y += bendOffset;
  }
  float m = uv.y - y;
  return 0.0175 / max(abs(m) + 0.01, 1e-3) + 0.01;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 baseUv = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
  baseUv.y *= -1.0;
  if (parallax) {
    baseUv += parallaxOffset;
  }
  vec3 col = vec3(0.0);
  vec3 b = lineGradientCount > 0 ? vec3(0.0) : background_color(baseUv);
  vec2 mouseUv = vec2(0.0);
  if (interactive) {
    mouseUv = (2.0 * iMouse - iResolution.xy) / iResolution.y;
    mouseUv.y *= -1.0;
  }
  if (enableBottom) {
    for (int i = 0; i < 50; ++i) {
      if (i >= bottomLineCount) break;
      float fi = float(i);
      float t = fi / max(float(bottomLineCount - 1), 1.0);
      vec3 lineCol = getLineColor(t, b);
      float angle = bottomWavePosition.z * log(length(baseUv) + 1.0);
      vec2 ruv = baseUv * rotate(angle);
      col += lineCol * wave(
        ruv + vec2(bottomLineDistance * fi + bottomWavePosition.x, bottomWavePosition.y),
        1.5 + 0.2 * fi, baseUv, mouseUv, interactive
      ) * 0.2;
    }
  }
  if (enableMiddle) {
    for (int i = 0; i < 50; ++i) {
      if (i >= middleLineCount) break;
      float fi = float(i);
      float t = fi / max(float(middleLineCount - 1), 1.0);
      vec3 lineCol = getLineColor(t, b);
      float angle = middleWavePosition.z * log(length(baseUv) + 1.0);
      vec2 ruv = baseUv * rotate(angle);
      col += lineCol * wave(
        ruv + vec2(middleLineDistance * fi + middleWavePosition.x, middleWavePosition.y),
        2.0 + 0.15 * fi, baseUv, mouseUv, interactive
      );
    }
  }
  if (enableTop) {
    for (int i = 0; i < 50; ++i) {
      if (i >= topLineCount) break;
      float fi = float(i);
      float t = fi / max(float(topLineCount - 1), 1.0);
      vec3 lineCol = getLineColor(t, b);
      float angle = topWavePosition.z * log(length(baseUv) + 1.0);
      vec2 ruv = baseUv * rotate(angle);
      ruv.x *= -1.0;
      col += lineCol * wave(
        ruv + vec2(topLineDistance * fi + topWavePosition.x, topWavePosition.y),
        1.0 + 0.2 * fi, baseUv, mouseUv, interactive
      ) * 0.1;
    }
  }
  fragColor = vec4(col, 1.0);
}

void main() {
  vec4 color = vec4(0.0);
  mainImage(color, gl_FragCoord.xy);
  gl_FragColor = color;
}
`

function hexToVec3(hex: string): Vector3 {
  let value = hex.trim()
  if (value.startsWith('#')) {
    value = value.slice(1)
  }
  let r = 255, g = 255, b = 255
  if (value.length === 3) {
    r = parseInt(value[0] + value[0], 16)
    g = parseInt(value[1] + value[1], 16)
    b = parseInt(value[2] + value[2], 16)
  } else if (value.length === 6) {
    r = parseInt(value.slice(0, 2), 16)
    g = parseInt(value.slice(2, 4), 16)
    b = parseInt(value.slice(4, 6), 16)
  }
  return new Vector3(r / 255, g / 255, b / 255)
}

function getLineCount(waveType: string, enabledWaves: string[], lineCount: number | number[]): number {
  if (typeof lineCount === 'number') return lineCount
  if (!enabledWaves.includes(waveType)) return 0
  const index = enabledWaves.indexOf(waveType)
  return lineCount[index] ?? 6
}

function getLineDistance(waveType: string, enabledWaves: string[], lineDistance: number | number[]): number {
  if (typeof lineDistance === 'number') return lineDistance
  if (!enabledWaves.includes(waveType)) return 0.1
  const index = enabledWaves.indexOf(waveType)
  return lineDistance[index] ?? 0.1
}

onMounted(() => {
  const container = containerRef.value
  if (!container) return

  const scene = new Scene()
  const camera = new OrthographicCamera(-1, 1, 1, -1, 0, 1)
  camera.position.z = 1

  const renderer = new WebGLRenderer({ antialias: true, alpha: false })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.domElement.style.width = '100%'
  renderer.domElement.style.height = '100%'
  renderer.domElement.style.pointerEvents = 'none'
  container.appendChild(renderer.domElement)

  const topLineCount = getLineCount('top', props.enabledWaves, props.lineCount)
  const middleLineCount = getLineCount('middle', props.enabledWaves, props.lineCount)
  const bottomLineCount = getLineCount('bottom', props.enabledWaves, props.lineCount)
  const topLineDistance = getLineDistance('top', props.enabledWaves, props.lineDistance) * 0.01
  const middleLineDistance = getLineDistance('middle', props.enabledWaves, props.lineDistance) * 0.01
  const bottomLineDistance = getLineDistance('bottom', props.enabledWaves, props.lineDistance) * 0.01

  const uniforms = {
    iTime: { value: 0 },
    iResolution: { value: new Vector3(1, 1, 1) },
    animationSpeed: { value: props.animationSpeed },
    enableTop: { value: props.enabledWaves.includes('top') },
    enableMiddle: { value: props.enabledWaves.includes('middle') },
    enableBottom: { value: props.enabledWaves.includes('bottom') },
    topLineCount: { value: topLineCount },
    middleLineCount: { value: middleLineCount },
    bottomLineCount: { value: bottomLineCount },
    topLineDistance: { value: topLineDistance },
    middleLineDistance: { value: middleLineDistance },
    bottomLineDistance: { value: bottomLineDistance },
    topWavePosition: {
      value: new Vector3(
        props.topWavePosition?.x ?? 10.0,
        props.topWavePosition?.y ?? 0.5,
        props.topWavePosition?.rotate ?? -0.4
      )
    },
    middleWavePosition: {
      value: new Vector3(
        props.middleWavePosition?.x ?? 5.0,
        props.middleWavePosition?.y ?? 0.0,
        props.middleWavePosition?.rotate ?? 0.2
      )
    },
    bottomWavePosition: {
      value: new Vector3(
        props.bottomWavePosition?.x ?? 2.0,
        props.bottomWavePosition?.y ?? -0.7,
        props.bottomWavePosition?.rotate ?? 0.4
      )
    },
    iMouse: { value: new Vector2(-1000, -1000) },
    interactive: { value: props.interactive },
    bendRadius: { value: props.bendRadius },
    bendStrength: { value: props.bendStrength },
    bendInfluence: { value: 0 },
    parallax: { value: props.parallax },
    parallaxStrength: { value: props.parallaxStrength },
    parallaxOffset: { value: new Vector2(0, 0) },
    lineGradient: {
      value: Array.from({ length: MAX_GRADIENT_STOPS }, () => new Vector3(1, 1, 1))
    },
    lineGradientCount: { value: 0 }
  }

  // Apply gradient from props
  if (props.linesGradient && props.linesGradient.length > 0) {
    const stops = props.linesGradient.slice(0, MAX_GRADIENT_STOPS)
    uniforms.lineGradientCount.value = stops.length
    stops.forEach((hex, i) => {
      const color = hexToVec3(hex)
      uniforms.lineGradient.value[i].set(color.x, color.y, color.z)
    })
  }

  const material = new ShaderMaterial({ uniforms, vertexShader, fragmentShader })
  const geometry = new PlaneGeometry(2, 2)
  const mesh = new Mesh(geometry, material)
  scene.add(mesh)

  const clock = new Clock()

  const setSize = () => {
    const width = container.clientWidth || 1
    const height = container.clientHeight || 1
    renderer.setSize(width, height, false)
    uniforms.iResolution.value.set(renderer.domElement.width, renderer.domElement.height, 1)
  }

  setSize()

  const ro = new ResizeObserver(() => { setSize() })
  ro.observe(container)

  // Mouse tracking
  const targetMouse = new Vector2(-1000, -1000)
  const currentMouse = new Vector2(-1000, -1000)
  let targetInfluence = 0
  let currentInfluence = 0
  const targetParallax = new Vector2(0, 0)
  const currentParallax = new Vector2(0, 0)

  const handlePointerMove = (event: PointerEvent) => {
    const rect = renderer.domElement.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    const dpr = renderer.getPixelRatio()
    targetMouse.set(x * dpr, (rect.height - y) * dpr)
    targetInfluence = 1.0
    if (props.parallax) {
      const centerX = rect.width / 2
      const centerY = rect.height / 2
      const offsetX = (x - centerX) / rect.width
      const offsetY = -(y - centerY) / rect.height
      targetParallax.set(offsetX * props.parallaxStrength, offsetY * props.parallaxStrength)
    }
  }

  const handlePointerLeave = () => {
    targetInfluence = 0.0
  }

  if (props.interactive) {
    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerleave', handlePointerLeave)
  }

  // Render loop
  let raf = 0
  let active = true
  const renderLoop = () => {
    if (!active) return
    uniforms.iTime.value = clock.getElapsedTime()

    if (props.interactive) {
      currentMouse.lerp(targetMouse, props.mouseDamping)
      uniforms.iMouse.value.copy(currentMouse)
      currentInfluence += (targetInfluence - currentInfluence) * props.mouseDamping
      uniforms.bendInfluence.value = currentInfluence
    }

    if (props.parallax) {
      currentParallax.lerp(targetParallax, props.mouseDamping)
      uniforms.parallaxOffset.value.copy(currentParallax)
    }

    renderer.render(scene, camera)
    raf = requestAnimationFrame(renderLoop)
  }
  renderLoop()

  // Cleanup
  onUnmounted(() => {
    active = false
    cancelAnimationFrame(raf)
    ro.disconnect()
    if (props.interactive) {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerleave', handlePointerLeave)
    }
    geometry.dispose()
    material.dispose()
    renderer.dispose()
    renderer.forceContextLoss()
    if (renderer.domElement.parentElement) {
      renderer.domElement.parentElement.removeChild(renderer.domElement)
    }
  })
})
</script>

<template>
  <div ref="containerRef" class="floating-lines-container" :style="{ mixBlendMode: props.mixBlendMode }" />
</template>

<style scoped>
.floating-lines-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}
</style>

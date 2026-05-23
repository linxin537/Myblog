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

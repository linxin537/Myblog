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

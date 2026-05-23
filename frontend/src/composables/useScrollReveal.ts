import { onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

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
  if (typeof window === 'undefined') return

  const {
    y = 30,
    duration = 0.6,
    stagger = 0,
    ease = 'power2.out',
    start = 'top 85%',
  } = options

  let ctx: gsap.Context | undefined

  onMounted(() => {
    ctx = gsap.context(() => {
      gsap.fromTo(
        target,
        { opacity: 0, y },
        {
          opacity: 1,
          y: 0,
          duration,
          stagger,
          ease,
          scrollTrigger: {
            trigger: Array.isArray(target) ? target[0] : target as Element,
            start,
            toggleActions: 'play none none none',
          },
        }
      )
    })
  })

  onBeforeUnmount(() => {
    ctx?.revert()
  })
}

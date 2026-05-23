// frontend/src/composables/useParallax.ts
import { onMounted, onBeforeUnmount } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export interface ParallaxTarget {
  el: string | Element
  speed: number  // 0 = fixed, 1 = normal scroll, 0.5 = half speed
}

export function useParallax(targets: ParallaxTarget[]) {
  if (typeof window === 'undefined') return

  let ctx: gsap.Context | undefined

  onMounted(() => {
    ctx = gsap.context(() => {
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
  })

  onBeforeUnmount(() => {
    ctx?.revert()
  })
}

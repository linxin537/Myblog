<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { NPagination, NEmpty, NSpin, NText } from 'naive-ui'
import { getFavorites } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import type { ArticleInfo } from '../types/api'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

const articles = ref<ArticleInfo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 10

async function load() {
  loading.value = true
  try {
    const { data } = await getFavorites({ page: page.value, page_size: pageSize })
    if (data.code === 0) {
      articles.value = (data.data || []) as ArticleInfo[]
      total.value = data.pagination?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function onPageChange(p: number) {
  page.value = p
  load()
}

let animCtx: gsap.Context | undefined

onMounted(() => {
  load()
  animCtx = gsap.context(() => {
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
})

onBeforeUnmount(() => {
  animCtx?.revert()
})

function handleCardMouseMove(e: MouseEvent) {
  const card = (e.currentTarget as HTMLElement).querySelector('.card-wrapper') as HTMLElement
  if (!card) return
  const rect = card.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  gsap.to(card, {
    rotateX: -y * 4,
    rotateY: x * 4,
    transformPerspective: 600,
    duration: 0.4,
    ease: 'power2.out',
  })
  const glow = card.querySelector('.card-glow') as HTMLElement
  if (glow) {
    glow.style.background = `radial-gradient(circle at ${(x + 0.5) * 100}% ${(y + 0.5) * 100}%, rgba(255,56,92,0.06), transparent 60%)`
  }
}

function handleCardMouseLeave(e: MouseEvent) {
  const card = (e.currentTarget as HTMLElement).querySelector('.card-wrapper') as HTMLElement
  if (!card) return
  gsap.to(card, {
    rotateX: 0, rotateY: 0,
    duration: 0.4,
    ease: 'back.out(1.5)',
  })
  const glow = card.querySelector('.card-glow') as HTMLElement
  if (glow) glow.style.background = 'transparent'
}
</script>

<template>
  <div :style="{ maxWidth: '820px', margin: '0 auto', paddingTop: '24px' }">
    <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700, marginBottom: '24px', display: 'block' }">
      我的收藏
    </NText>

    <NSpin :show="loading">
      <template v-if="!loading && articles.length === 0">
        <NEmpty class="fav-empty" description="还没有收藏任何文章" />
      </template>
      <div
        v-else
        class="fav-grid"
        :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }"
      >
        <div
          v-for="article in articles"
          :key="article.id"
          class="fav-item"
          style="perspective: 600px;"
          @click="router.push(`/article/${article.id}`)"
          @mousemove="handleCardMouseMove"
          @mouseleave="handleCardMouseLeave"
        >
          <div class="card-wrapper" style="position: relative; border-radius: 14px; overflow: hidden;">
            <div class="card-glow" style="position: absolute; inset: 0; pointer-events: none; z-index: 1; transition: background 0.3s ease;" />
            <ArticleCard :article="article" />
          </div>
        </div>
      </div>
      <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 32px;">
        <NPagination
          :page="page"
          :page-size="pageSize"
          :item-count="total"
          @update:page="onPageChange"
        />
      </div>
    </NSpin>
  </div>
</template>

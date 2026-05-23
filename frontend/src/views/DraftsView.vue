<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NText, NSpin, NEmpty, NPopconfirm, useMessage } from 'naive-ui'
import { getArticles, deleteArticle } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import type { ArticleInfo } from '../types/api'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const message = useMessage()
const articles = ref<ArticleInfo[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await getArticles({ is_draft: true, page_size: 50 })
    if (data.code === 0) {
      articles.value = (data.data || []) as ArticleInfo[]
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  const { data } = await deleteArticle(id)
  if (data.code === 0) {
    message.success('草稿已删除')
    load()
  } else {
    message.error(data.message)
  }
}

let animCtx: gsap.Context | undefined

onMounted(() => {
  load()
  animCtx = gsap.context(() => {
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
    gsap.to('.draft-empty', {
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
    <div :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }">
      <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700 }">草稿管理</NText>
      <NButton type="primary" @click="router.push('/editor')">新建文章</NButton>
    </div>

    <NSpin :show="loading">
      <NEmpty class="draft-empty" v-if="!loading && articles.length === 0" description="暂无草稿">
        <template #extra>
          <NButton type="primary" @click="router.push('/editor')">开始写作</NButton>
        </template>
      </NEmpty>
      <div
        v-else
        class="draft-grid"
        :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }"
      >
        <div
          v-for="article in articles"
          :key="article.id"
          class="draft-item"
          style="perspective: 600px;"
          @mousemove="handleCardMouseMove"
          @mouseleave="handleCardMouseLeave"
        >
          <div class="card-wrapper" style="position: relative; border-radius: 14px; overflow: hidden; border: 1px solid var(--color-hairline-soft);">
            <div class="card-glow" style="position: absolute; inset: 0; pointer-events: none; z-index: 1; transition: background 0.3s ease;" />
            <div @click="router.push(`/editor/${article.id}`)">
              <ArticleCard :article="article" />
            </div>
            <!-- Draft action overlay -->
            <div :style="{ position: 'absolute', top: '8px', right: '8px', display: 'flex', gap: '6px', zIndex: 2 }">
              <NButton size="tiny" :style="{ '--n-border-radius': '6px' }" @click="router.push(`/editor/${article.id}`)">编辑</NButton>
              <NPopconfirm @positive-click="() => handleDelete(article.id)">
                <template #trigger>
                  <NButton size="tiny" type="error" secondary :style="{ '--n-border-radius': '6px' }">删除</NButton>
                </template>
                确定删除这个草稿？
              </NPopconfirm>
            </div>
          </div>
        </div>
      </div>
    </NSpin>
  </div>
</template>

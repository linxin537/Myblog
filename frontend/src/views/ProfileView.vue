<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useHead } from '@unhead/vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NText, NSpace, NTag, NSpin, NResult, NPagination, NEmpty } from 'naive-ui'
import client from '../api/client'
import ArticleCard from '../components/ArticleCard.vue'
import type { UserInfo, ArticleInfo, ApiResponse } from '../types/api'
import { getIdenticonUrl } from '../utils/identicon'
import gsap from 'gsap'

const route = useRoute()
const router = useRouter()

useHead({
  title: () => `${route.params.username} 的个人主页`,
  meta: [
    { name: 'description', content: () => `${route.params.username} 的个人主页` },
  ],
})

interface ProfileData extends UserInfo {
  article_count: number
  total_views: number
  articles: ArticleInfo[]
}

const profile = ref<ProfileData | null>(null)
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 10

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function loadProfile() {
  loading.value = true
  try {
    const username = route.params.username as string
    const { data } = await client.get<ApiResponse<ProfileData>>(`/users/${username}/profile`, {
      params: { page: page.value, page_size: pageSize },
    })
    if (data.code === 0 && data.data) {
      profile.value = data.data
      total.value = data.data.article_count
    }
  } finally {
    loading.value = false
  }
}

function onPageChange(p: number) {
  page.value = p
  loadProfile()
}

let animCtx: gsap.Context | undefined

onMounted(loadProfile)

watch(profile, () => {
  if (profile.value) {
    nextTick(() => {
      animCtx?.revert()
      animCtx = gsap.context(() => {
        gsap.fromTo('.profile-section > *', {
          opacity: 0, y: 16,
        }, {
          opacity: 1, y: 0,
          duration: 0.4,
          stagger: 0.05,
          ease: 'power2.out',
        })
      })
    })
  }
})

onBeforeUnmount(() => {
  animCtx?.revert()
})
</script>

<template>
  <div style="max-width: 820px; margin: 0 auto; padding-top: 24px;">
    <NSpin :show="loading">
      <NResult
        v-if="!loading && !profile"
        status="404"
        title="用户不存在"
      >
        <template #footer>
          <NButton @click="router.push('/')">返回首页</NButton>
        </template>
      </NResult>

      <template v-else-if="profile">
        <!-- 用户信息卡片 -->
        <div
          class="profile-section card"
          :style="{
            padding: '40px 32px 32px',
            marginBottom: '32px',
            textAlign: 'center',
          }"
        >
          <img
            :src="getIdenticonUrl(profile.username, profile.avatar, 96)"
            :style="{
              width: '96px',
              height: '96px',
              borderRadius: '50%',
              marginBottom: '16px',
            }"
            alt=""
          />
          <NText tag="h1" style="font-size: 28px; font-weight: 700; margin-bottom: 4px; display: block;">
            {{ profile.username }}
          </NText>
          <NTag v-if="profile.role === 'admin'" type="error" size="small" round :bordered="false">管理员</NTag>
          <NTag v-else-if="profile.role === 'author'" type="info" size="small" round :bordered="false">作者</NTag>
          <NText v-if="profile.bio" :depth="2" :style="{ display: 'block', marginTop: '16px', fontSize: '14px', color: 'var(--color-muted)' }">
            {{ profile.bio }}
          </NText>
          <NSpace justify="center" :style="{ marginTop: '20px' }">
            <div :style="{ textAlign: 'center', padding: '0 16px' }">
              <NText :style="{ fontSize: '18px', fontWeight: 600, display: 'block' }">{{ profile.article_count }}</NText>
              <NText depth="3" :style="{ fontSize: '12px', color: 'var(--color-muted)' }">文章</NText>
            </div>
            <div :style="{ width: '1px', background: 'var(--color-hairline-soft)', alignSelf: 'stretch' }" />
            <div :style="{ textAlign: 'center', padding: '0 16px' }">
              <NText :style="{ fontSize: '18px', fontWeight: 600, display: 'block' }">{{ profile.total_views }}</NText>
              <NText depth="3" :style="{ fontSize: '12px', color: 'var(--color-muted)' }">阅读</NText>
            </div>
            <div :style="{ width: '1px', background: 'var(--color-hairline-soft)', alignSelf: 'stretch' }" />
            <div :style="{ textAlign: 'center', padding: '0 16px' }">
              <NText :style="{ fontSize: '18px', fontWeight: 600, display: 'block' }">{{ formatDate(profile.created_at) }}</NText>
              <NText depth="3" :style="{ fontSize: '12px', color: 'var(--color-muted)' }">加入</NText>
            </div>
          </NSpace>
        </div>

        <!-- 文章列表 -->
        <NText tag="h3" :style="{ fontSize: '20px', fontWeight: 600, marginBottom: '16px', display: 'block' }">发布的文章</NText>
        <NEmpty v-if="profile.articles.length === 0" description="暂无文章" />
        <div
          v-else
          :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }"
        >
          <div
            v-for="article in profile.articles"
            :key="article.id"
            @click="router.push(`/article/${article.id}`)"
          >
            <ArticleCard :article="article" />
          </div>
        </div>
        <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 32px;">
          <NPagination :page="page" :page-size="pageSize" :item-count="total" @update:page="onPageChange" />
        </div>
      </template>
    </NSpin>
  </div>
</template>

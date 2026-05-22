<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NText, NSpace, NTag, NSpin, NResult, NPagination, NEmpty } from 'naive-ui'
import client from '../api/client'
import ArticleCard from '../components/ArticleCard.vue'
import type { UserInfo, ArticleInfo, ApiResponse, PaginatedResponse } from '../types/api'

const route = useRoute()
const router = useRouter()

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

onMounted(loadProfile)
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
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
        <div class="glass" style="padding: 32px; border-radius: 16px; margin-bottom: 32px; text-align: center;">
          <NText tag="h1" style="font-size: 28px; font-weight: 700; margin-bottom: 8px;">
            {{ profile.username }}
          </NText>
          <NTag v-if="profile.role === 'admin'" type="error" size="small" round>管理员</NTag>
          <NTag v-else-if="profile.role === 'author'" type="info" size="small" round>作者</NTag>
          <NText v-if="profile.bio" depth="2" style="display: block; margin-top: 16px; font-size: 14px;">
            {{ profile.bio }}
          </NText>
          <NSpace justify="center" style="margin-top: 16px;">
            <NText depth="3" style="font-size: 13px;">{{ profile.article_count }} 篇文章</NText>
            <NText depth="3" style="font-size: 13px;">{{ profile.total_views }} 次阅读</NText>
            <NText depth="3" style="font-size: 13px;">{{ formatDate(profile.created_at) }} 加入</NText>
          </NSpace>
        </div>

        <!-- 文章列表 -->
        <NText tag="h3" style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">发布的文章</NText>
        <NEmpty v-if="profile.articles.length === 0" description="暂无文章" />
        <div v-else>
          <ArticleCard
            v-for="article in profile.articles"
            :key="article.id"
            :article="article"
            style="margin-bottom: 16px;"
          />
          <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 24px;">
            <NPagination :page="page" :page-size="pageSize" :item-count="total" @update:page="onPageChange" />
          </div>
        </div>
      </template>
    </NSpin>
  </div>
</template>

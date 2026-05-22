<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpace, NText, NSpin } from 'naive-ui'
import { FileTrayFull, Eye, Heart, Star } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import client from '../api/client'
import type { ApiResponse } from '../types/api'

interface StatsData {
  total_articles: number
  total_drafts: number
  total_views: number
  total_likes: number
  total_favorites: number
  total_comments: number
}

const stats = ref<StatsData>({
  total_articles: 0, total_drafts: 0, total_views: 0,
  total_likes: 0, total_favorites: 0, total_comments: 0,
})
const loading = ref(true)

async function load() {
  try {
    const { data } = await client.get<ApiResponse<StatsData>>('/users/me/stats')
    if (data.code === 0 && data.data) {
      stats.value = data.data
    }
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <NSpin :show="loading">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px;">
      <div class="glass" style="padding: 20px; border-radius: 12px; text-align: center;">
        <NIcon :component="FileTrayFull" size="22" color="var(--accent)" />
        <NText tag="div" style="font-size: 28px; font-weight: 700; margin-top: 8px;">{{ stats.total_articles }}</NText>
        <NText depth="3" style="font-size: 13px;">已发布文章</NText>
      </div>
      <div class="glass" style="padding: 20px; border-radius: 12px; text-align: center;">
        <NIcon :component="FileTrayFull" size="22" color="#f0a020" />
        <NText tag="div" style="font-size: 28px; font-weight: 700; margin-top: 8px;">{{ stats.total_drafts }}</NText>
        <NText depth="3" style="font-size: 13px;">草稿</NText>
      </div>
      <div class="glass" style="padding: 20px; border-radius: 12px; text-align: center;">
        <NIcon :component="Eye" size="22" color="#2080f0" />
        <NText tag="div" style="font-size: 28px; font-weight: 700; margin-top: 8px;">{{ stats.total_views }}</NText>
        <NText depth="3" style="font-size: 13px;">总阅读</NText>
      </div>
      <div class="glass" style="padding: 20px; border-radius: 12px; text-align: center;">
        <NIcon :component="Heart" size="22" color="#d03050" />
        <NText tag="div" style="font-size: 28px; font-weight: 700; margin-top: 8px;">{{ stats.total_likes }}</NText>
        <NText depth="3" style="font-size: 13px;">获赞</NText>
      </div>
      <div class="glass" style="padding: 20px; border-radius: 12px; text-align: center;">
        <NIcon :component="Star" size="22" color="#f0a020" />
        <NText tag="div" style="font-size: 28px; font-weight: 700; margin-top: 8px;">{{ stats.total_favorites }}</NText>
        <NText depth="3" style="font-size: 13px;">被收藏</NText>
      </div>
    </div>
  </NSpin>
</template>

<script setup lang="ts">
import { NTag, NText, NTime, NSpace, NEl } from 'naive-ui'
import type { ArticleInfo } from '../types/api'

const props = defineProps<{ article: ArticleInfo }>()

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="glass-aurora scale-in" style="padding: 24px; cursor: pointer;">
    <div v-if="article.cover_image" style="margin: -24px -24px 20px -24px; border-radius: 15px 15px 0 0; overflow: hidden; max-height: 220px;">
      <img :src="article.cover_image" style="width: 100%; height: 220px; object-fit: cover; transition: transform 0.5s ease;" alt="" />
    </div>

    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <NTag v-if="article.is_pinned" type="error" size="small" round>置顶</NTag>
      <NTag v-if="article.is_draft" type="warning" size="small" round>草稿</NTag>
      <NTag v-if="article.category" type="info" size="small" round>{{ article.category.name }}</NTag>
    </div>

    <NText tag="h2" style="font-size: 20px; font-weight: 700; margin-bottom: 8px; line-height: 1.4;">
      {{ article.title }}
    </NText>

    <NText v-if="article.summary" depth="2" style="margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
      {{ article.summary }}
    </NText>

    <NSpace align="center" style="margin-top: 12px;">
      <NText depth="3" style="font-size: 13px;">
        {{ article.author?.username || '匿名' }}
      </NText>
      <NText depth="3" style="font-size: 13px;">
        {{ formatDate(article.published_at || article.created_at) }}
      </NText>
      <NText depth="3" style="font-size: 13px;">
        {{ article.view_count }} 次阅读
      </NText>
    </NSpace>

    <NSpace v-if="article.tags.length" style="margin-top: 8px;">
      <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
        {{ tag.name }}
      </NTag>
    </NSpace>
  </div>
</template>

<style scoped>
.glass-aurora:hover img {
  transform: scale(1.03);
}
</style>

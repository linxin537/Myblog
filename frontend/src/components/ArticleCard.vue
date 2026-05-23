<script setup lang="ts">
import { NTag, NText, NSpace } from 'naive-ui'
import type { ArticleInfo } from '../types/api'
import { formatReadingTime } from '../composables/useReadingTime'

const props = defineProps<{ article: ArticleInfo }>()

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div
    class="card"
    :style="{
      borderRadius: '14px',
      overflow: 'hidden',
      cursor: 'pointer',
      padding: '20px',
      transition: 'box-shadow 0.3s ease, transform 0.3s ease',
    }"
  >
    <!-- Badges row -->
    <div :style="{ display: 'flex', gap: '6px', marginBottom: '10px', flexWrap: 'wrap' }">
      <NTag v-if="article.is_pinned" type="error" size="small" :bordered="false" round>精选</NTag>
      <NTag v-if="article.is_draft" type="warning" size="small" :bordered="false">草稿</NTag>
      <NTag v-if="article.category" size="small" :bordered="false">{{ article.category.name }}</NTag>
    </div>

    <!-- Title -->
    <NText
      tag="h3"
      :style="{
        fontSize: '17px',
        fontWeight: 600,
        lineHeight: 1.3,
        marginBottom: article.summary ? '6px' : '10px',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
        color: 'var(--color-ink)',
      }"
    >
      {{ article.title }}
    </NText>

    <!-- Summary -->
    <NText
      v-if="article.summary"
      depth="2"
      :style="{
        fontSize: '14px',
        marginBottom: '10px',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
      }"
    >
      {{ article.summary }}
    </NText>

    <!-- Footer -->
    <div :style="{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }">
      <NSpace :size="12">
        <NText depth="3" :style="{ fontSize: '13px' }">
          {{ article.author?.username || '匿名' }}
        </NText>
        <NText depth="3" :style="{ fontSize: '13px' }">
          {{ formatDate(article.published_at || article.created_at) }}
        </NText>
      </NSpace>
      <NText depth="3" :style="{ fontSize: '13px' }">
        {{ article.view_count }} 阅读
      </NText>
      <NText depth="3" :style="{ fontSize: '13px' }">
        · {{ formatReadingTime(article.summary || '') }}
      </NText>
    </div>

    <!-- Tags -->
    <NSpace v-if="article.tags && article.tags.length" :style="{ marginTop: '8px' }">
      <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
        {{ tag.name }}
      </NTag>
    </NSpace>
  </div>
</template>

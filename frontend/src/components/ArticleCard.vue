<script setup lang="ts">
import { NTag, NText, NSpace } from 'naive-ui'
import type { ArticleInfo } from '../types/api'
import { getCoverForArticle } from '../utils/covers'

const props = defineProps<{ article: ArticleInfo }>()

const coverStyle = getCoverForArticle(props.article.tags)
const hasCover = !!props.article.cover_image

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
    }"
  >
    <!-- Cover Photo -->
    <div
      :style="{
        aspectRatio: '1 / 1',
        position: 'relative',
        background: hasCover ? undefined : coverStyle.gradient,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }"
    >
      <img
        v-if="hasCover"
        :src="article.cover_image!"
        :style="{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transition: 'transform 0.4s ease',
        }"
        alt=""
      />
      <span
        v-else
        :style="{ fontSize: '48px', opacity: 0.45, lineHeight: 1, userSelect: 'none' }"
      >{{ coverStyle.icon }}</span>

      <!-- Floating badges -->
      <span
        v-if="article.is_pinned"
        :style="{
          position: 'absolute',
          top: '12px',
          left: '12px',
          background: 'var(--color-canvas)',
          color: 'var(--color-ink)',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '11px',
          fontWeight: 600,
          boxShadow: 'var(--shadow-card)',
        }"
      >精选</span>
    </div>

    <!-- Meta -->
    <div :style="{ padding: '16px' }">
      <div :style="{ display: 'flex', gap: '6px', marginBottom: '6px', flexWrap: 'wrap' }">
        <NTag v-if="article.is_draft" type="warning" size="small" :bordered="false">草稿</NTag>
        <NTag v-if="article.category" size="small" :bordered="false">{{ article.category.name }}</NTag>
      </div>

      <NText
        tag="h3"
        :style="{
          fontSize: '16px',
          fontWeight: 600,
          lineHeight: 1.25,
          marginBottom: article.summary ? '4px' : '8px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }"
      >
        {{ article.title }}
      </NText>

      <NText
        v-if="article.summary"
        depth="2"
        :style="{
          fontSize: '14px',
          marginBottom: '8px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }"
      >
        {{ article.summary }}
      </NText>

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
      </div>

      <NSpace v-if="article.tags && article.tags.length" :style="{ marginTop: '8px' }">
        <NTag v-for="tag in article.tags" :key="tag.id" size="tiny" :bordered="false">
          {{ tag.name }}
        </NTag>
      </NSpace>
    </div>
  </div>
</template>

<style scoped>
.card:hover img {
  transform: scale(1.03);
}
</style>

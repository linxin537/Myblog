<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NText, NSpace, NSpin, NResult, NPopconfirm, useMessage } from 'naive-ui'
import { marked } from 'marked'
import { getArticle, deleteArticle } from '../api/articles'
import { useAuthStore } from '../stores/auth'
import type { ArticleDetail as ArticleDetailType } from '../types/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const article = ref<ArticleDetailType | null>(null)
const loading = ref(true)

const canEdit = () => {
  if (!auth.user || !article.value) return false
  return auth.isAdmin || auth.user.id === article.value.author_id
}

function renderMarkdown(content: string) {
  return marked(content, { breaks: true, gfm: true })
}

async function loadArticle() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const { data } = await getArticle(id)
    if (data.code === 0 && data.data) {
      article.value = data.data as ArticleDetailType
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!article.value) return
  const { data } = await deleteArticle(article.value.id)
  if (data.code === 0) {
    message.success('文章已删除')
    router.push('/')
  } else {
    message.error(data.message)
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(loadArticle)
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
    <NSpin :show="loading">
      <NResult
        v-if="!loading && !article"
        status="404"
        title="文章不存在"
        description="这篇文章可能已被删除或从未存在"
      >
        <template #footer>
          <NButton @click="router.push('/')">返回首页</NButton>
        </template>
      </NResult>

      <article v-else-if="article">
        <!-- 封面图 -->
        <div
          v-if="article.cover_image"
          class="glass"
          style="margin-bottom: 24px; padding: 0; overflow: hidden; border-radius: 16px; max-height: 400px;"
        >
          <img
            :src="article.cover_image"
            style="width: 100%; height: 400px; object-fit: cover; display: block;"
            alt=""
          />
        </div>

        <!-- 标题 -->
        <NText tag="h1" style="font-size: 32px; font-weight: 800; margin-bottom: 16px; line-height: 1.3;">
          {{ article.title }}
        </NText>

        <!-- 元信息 -->
        <NSpace align="center" style="margin-bottom: 24px; flex-wrap: wrap;">
          <NTag v-if="article.is_pinned" type="error" size="small" round>置顶</NTag>
          <NTag v-if="article.is_draft" type="warning" size="small" round>草稿</NTag>
          <NTag v-if="article.category" type="info" size="small" round>
            {{ article.category.name }}
          </NTag>
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

        <!-- 标签 -->
        <NSpace v-if="article.tags && article.tags.length" style="margin-bottom: 24px;">
          <NTag
            v-for="tag in article.tags"
            :key="tag.id"
            size="small"
            :bordered="false"
            style="cursor: pointer;"
            @click="router.push(`/?tag_id=${tag.id}`)"
          >
            #{{ tag.name }}
          </NTag>
        </NSpace>

        <!-- 分割线 -->
        <div style="border-top: 1px solid var(--border-glass); margin: 24px 0;" />

        <!-- Markdown 内容 -->
        <div
          class="article-content"
          v-html="renderMarkdown(article.content)"
          style="line-height: 1.8; font-size: 16px;"
        />

        <!-- 底部操作 -->
        <div style="border-top: 1px solid var(--border-glass); margin-top: 48px; padding-top: 24px; display: flex; gap: 12px; justify-content: space-between;">
          <NButton @click="router.push('/')">返回列表</NButton>
          <NSpace v-if="canEdit()">
            <NButton type="primary" @click="router.push(`/editor/${article.id}`)">编辑</NButton>
            <NPopconfirm @positive-click="handleDelete">
              <template #trigger>
                <NButton type="error" secondary>删除</NButton>
              </template>
              确定要删除这篇文章吗？
            </NPopconfirm>
          </NSpace>
        </div>
      </article>
    </NSpin>
  </div>
</template>

<style>
.article-content h1 { font-size: 28px; margin: 24px 0 12px; }
.article-content h2 { font-size: 24px; margin: 20px 0 10px; }
.article-content h3 { font-size: 20px; margin: 16px 0 8px; }
.article-content p { margin-bottom: 16px; }
.article-content img { max-width: 100%; border-radius: 8px; margin: 12px 0; }
.article-content pre { background: rgba(0,0,0,0.05); border-radius: 8px; padding: 16px; overflow-x: auto; margin: 16px 0; }
.article-content code { font-family: 'JetBrains Mono', monospace; font-size: 14px; }
.article-content blockquote { border-left: 3px solid var(--accent); padding-left: 16px; margin: 16px 0; color: var(--text-secondary); }
.article-content table { width: 100%; border-collapse: collapse; margin: 16px 0; }
.article-content th, .article-content td { border: 1px solid var(--border-glass); padding: 8px 12px; text-align: left; }
.article-content th { background: rgba(0,0,0,0.03); }
.article-content a { color: var(--accent); }
</style>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NText, NSpace, NSpin, NResult, NPopconfirm, useMessage } from 'naive-ui'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { getArticle, deleteArticle } from '../api/articles'
import { useAuthStore } from '../stores/auth'
import CommentSection from '../components/CommentSection.vue'
import LikeButton from '../components/LikeButton.vue'
import FavoriteButton from '../components/FavoriteButton.vue'
import TableOfContents from '../components/TableOfContents.vue'
import type { ArticleDetail as ArticleDetailType } from '../types/api'

marked.setOptions({
  highlight(code: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const article = ref<ArticleDetailType | null>(null)
const loading = ref(true)
const likeCount = ref(0)
const isLiked = ref(false)
const favoriteCount = ref(0)
const isFavorited = ref(false)
const tocHeadings = ref<{ id: string; text: string; level: number }[]>([])

const canEdit = () => {
  if (!auth.user || !article.value) return false
  return auth.isAdmin || auth.user.id === article.value.author_id
}

function extractHeadings(content: string) {
  const headings: { id: string; text: string; level: number }[] = []
  const tokens = marked.lexer(content)
  for (const token of tokens) {
    if (token.type === 'heading' && token.depth <= 3) {
      const text = token.tokens?.filter(t => t.type === 'text').map(t => t.text).join('') || ''
      const id = text.toLowerCase().replace(/[^\w一-鿿]+/g, '-').replace(/(^-|-$)/g, '')
      headings.push({ id: id || `heading-${headings.length}`, text, level: token.depth })
    }
  }
  return headings
}

function renderMarkdown(content: string) {
  const raw = marked(content, { breaks: true, gfm: true, headerIds: true }) as string
  return DOMPurify.sanitize(raw)
}

async function loadArticle() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const { data } = await getArticle(id)
    if (data.code === 0 && data.data) {
      article.value = data.data as ArticleDetailType
      isLiked.value = data.data.is_liked
      likeCount.value = data.data.like_count
      isFavorited.value = data.data.is_favorited
      favoriteCount.value = data.data.favorite_count
      tocHeadings.value = extractHeadings(data.data.content)
      await nextTick()
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

      <article v-else-if="article" style="display: flex; gap: 40px; position: relative;">
        <!-- 目录侧边栏 -->
        <TableOfContents :headings="tocHeadings" />

        <div style="flex: 1; min-width: 0;">
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
          <LikeButton
            :article-id="article.id"
            :initial-liked="isLiked"
            :initial-count="likeCount"
            @update:liked="(v: boolean) => isLiked = v"
            @update:count="(v: number) => likeCount = v"
          />
          <FavoriteButton
            :article-id="article.id"
            :initial-favorited="isFavorited"
            :initial-count="favoriteCount"
            @update:favorited="(v: boolean) => isFavorited = v"
            @update:count="(v: number) => favoriteCount = v"
          />
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

        <!-- 评论区 -->
        <div style="margin-top: 48px; border-top: 1px solid var(--border-glass); padding-top: 32px;">
          <CommentSection :article-id="article.id" />
        </div>
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

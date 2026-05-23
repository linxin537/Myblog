<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NSpace, NSpin, NResult, NPopconfirm, useMessage } from 'naive-ui'
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
import { getIdenticonUrl } from '../utils/identicon'

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
  <div :style="{ display: 'flex', gap: '32px', maxWidth: '1080px', margin: '0 auto', paddingTop: '24px' }">
    <NSpin :show="loading" style="width: 100%">
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

      <div v-else-if="article" :style="{ display: 'flex', gap: '32px', width: '100%' }">
        <!-- 左栏：文章主体 -->
        <div :style="{ flex: '1 1 0%', minWidth: 0 }">
          <!-- 封面图 -->
          <div
            v-if="article.cover_image"
            :style="{
              marginBottom: '28px',
              padding: '0',
              overflow: 'hidden',
              borderRadius: '16px',
              maxHeight: '420px',
              border: '1px solid var(--color-hairline-soft)',
            }"
          >
            <img
              :src="article.cover_image"
              style="width: 100%; height: 420px; object-fit: cover; display: block;"
              alt=""
            />
          </div>

          <!-- 标题 -->
          <h1 style="font-family: 'Fraunces', 'Noto Serif SC', serif; font-size: 40px; font-weight: 600; margin: 0 0 20px; line-height: 1.18; letter-spacing: -0.5px; color: var(--color-ink);">
            {{ article.title }}
          </h1>

          <!-- 元信息 -->
          <NSpace align="center" style="margin-bottom: 24px; flex-wrap: wrap;">
            <NTag v-if="article.is_pinned" type="error" size="small" round>置顶</NTag>
            <NTag v-if="article.is_draft" type="warning" size="small" round>草稿</NTag>
            <NTag v-if="article.category" type="info" size="small" round>
              {{ article.category.name }}
            </NTag>
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

          <!-- 作者信息行（带 Identicon 头像） -->
          <div :style="{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '24px' }">
            <img
              :src="getIdenticonUrl(article.author?.username || 'anonymous', article.author?.avatar, 40)"
              :style="{ width: '40px', height: '40px', borderRadius: '8px' }"
              alt=""
            />
            <div>
              <div :style="{ fontSize: '14px', fontWeight: 600, color: 'var(--color-ink)' }">
                {{ article.author?.username }}
              </div>
              <div :style="{ fontSize: '13px', color: 'var(--color-muted)' }">
                {{ formatDate(article.published_at || article.created_at) }} · {{ article.view_count }} 阅读
              </div>
            </div>
          </div>

          <!-- 分割线 -->
          <div :style="{ height: '1px', background: 'var(--color-hairline-soft)', margin: '24px 0' }" />

          <!-- Markdown 内容 -->
          <div
            class="article-content"
            v-html="renderMarkdown(article.content)"
            style="line-height: 1.8; font-size: 16px;"
          />

          <!-- 底部操作 -->
          <div :style="{ borderTop: '1px solid var(--color-hairline-soft)', marginTop: '48px', paddingTop: '24px', display: 'flex', gap: '12px', justifyContent: 'space-between' }">
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
          <div :style="{ marginTop: '48px', borderTop: '1px solid var(--color-hairline-soft)', paddingTop: '32px' }">
            <CommentSection :article-id="article.id" />
          </div>
        </div>

        <!-- 右栏：300px 粘性侧边栏 -->
        <div :style="{ width: '300px', flexShrink: 0 }">
          <div :style="{
            position: 'sticky',
            top: '112px',
            border: '1px solid var(--color-hairline-soft)',
            borderRadius: '14px',
            padding: '20px',
            background: 'var(--color-canvas)',
            boxShadow: 'var(--shadow-card)',
          }">
            <TableOfContents :headings="tocHeadings" />
            <div :style="{ height: '1px', background: 'var(--color-hairline-soft)', margin: '16px 0' }" />
            <NSpace vertical>
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
          </div>
        </div>
      </div>
    </NSpin>
  </div>
</template>

<style>
.article-content h1 { font-family: 'Fraunces', 'Noto Serif SC', serif; font-size: 30px; font-weight: 600; margin: 32px 0 14px; letter-spacing: -0.3px; }
.article-content h2 { font-family: 'Fraunces', 'Noto Serif SC', serif; font-size: 24px; font-weight: 600; margin: 28px 0 12px; letter-spacing: -0.2px; }
.article-content h3 { font-size: 20px; font-weight: 600; margin: 20px 0 10px; }
.article-content p { margin-bottom: 18px; line-height: 1.8; }
.article-content img { max-width: 100%; border-radius: 10px; margin: 16px 0; }
.article-content pre { background: var(--color-surface-soft); border: 1px solid var(--color-hairline-soft); border-radius: 10px; padding: 20px; overflow-x: auto; margin: 20px 0; }
.article-content code { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 14px; }
.article-content blockquote { border-left: 3px solid var(--color-primary); padding-left: 18px; margin: 20px 0; color: var(--color-body); font-style: italic; }
.article-content table { width: 100%; border-collapse: collapse; margin: 20px 0; }
.article-content th, .article-content td { border: 1px solid var(--color-hairline-soft); padding: 10px 14px; text-align: left; }
.article-content th { background: var(--color-surface-soft); font-weight: 600; }
.article-content a { color: var(--color-primary); }
</style>

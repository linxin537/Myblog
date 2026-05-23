<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NInput, NSelect, NPagination, NButton, NSpin, NEmpty, NSpace } from 'naive-ui'
import { Search } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import ArticleCard from '../components/ArticleCard.vue'
import ArticleCardSkeleton from '../components/ArticleCardSkeleton.vue'
import { useAuthStore } from '../stores/auth'
import { getArticles } from '../api/articles'
import { getCategories } from '../api/categories'
import { getTags } from '../api/tags'
import type { ArticleInfo, CategoryInfo, TagInfo } from '../types/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const articles = ref<ArticleInfo[]>([])
const categories = ref<CategoryInfo[]>([])
const tags = ref<TagInfo[]>([])
const loading = ref(false)
const initialLoading = ref(true)
const total = ref(0)
const page = ref(1)
const pageSize = 10

const searchKeyword = ref('')
const selectedCategory = ref<number | null>(null)
const selectedTag = ref<number | null>(null)

async function loadArticles() {
  loading.value = true
  try {
    const { data } = await getArticles({
      page: page.value,
      page_size: pageSize,
      category_id: selectedCategory.value ?? undefined,
      tag_id: selectedTag.value ?? undefined,
      search: searchKeyword.value || undefined,
    })
    if (data.code === 0) {
      articles.value = (data.data || []) as ArticleInfo[]
      if (data.pagination) {
        total.value = data.pagination.total
      }
    }
  } finally {
    loading.value = false
    initialLoading.value = false
  }
}

async function loadFilters() {
  const [catRes, tagRes] = await Promise.all([getCategories(), getTags()])
  if (catRes.data.code === 0) categories.value = catRes.data.data || []
  if (tagRes.data.code === 0) tags.value = tagRes.data.data || []
}

function onPageChange(p: number) {
  page.value = p
}

function clearFilters() {
  searchKeyword.value = ''
  selectedCategory.value = null
  selectedTag.value = null
  page.value = 1
}

watch([page, selectedCategory, selectedTag], () => {
  loadArticles()
})

watch(searchKeyword, () => {
  page.value = 1
  loadArticles()
})

onMounted(() => {
  if (route.query.tag_id) {
    selectedTag.value = Number(route.query.tag_id)
  }
  loadFilters()
  loadArticles()
})
</script>

<template>
    <!-- Hero -->
    <div :style="{ textAlign: 'center', padding: '80px 32px 64px' }">
      <h1 :style="{
        fontSize: '28px',
        fontWeight: 700,
        lineHeight: 1.43,
        color: 'var(--color-ink)',
        margin: '0 0 8px',
        letterSpacing: '0',
      }">
        用文字记录思考
      </h1>
      <p :style="{
        fontSize: '16px',
        color: 'var(--color-muted)',
        margin: '0 auto 32px',
        maxWidth: '480px',
      }">
        分享技术见解与日常感悟
      </p>

      <!-- Search Pill -->
      <div :style="{ maxWidth: '500px', margin: '0 auto' }">
        <NInput
          v-model:value="searchKeyword"
          placeholder="搜索文章..."
          clearable
          round
          size="large"
          :style="{
            '--n-border': '1px solid var(--color-hairline)',
            '--n-color': 'var(--color-canvas)',
            '--n-color-focus': 'var(--color-canvas)',
            '--n-text-color': 'var(--color-ink)',
            '--n-placeholder-color': 'var(--color-muted-soft)',
            '--n-height': '56px',
            '--n-font-size': '16px',
            '--n-border-radius': '9999px',
            '--n-box-shadow-focus': 'var(--shadow-card)',
          }"
        >
          <template #prefix>
            <NIcon :component="Search" />
          </template>
        </NInput>
      </div>
    </div>

    <!-- 筛选栏 + 列表 -->
    <div style="max-width: 780px; margin: 0 auto; padding: 0 32px 64px;">
      <div :style="{
        background: 'var(--color-canvas)',
        border: '1px solid var(--color-hairline-soft)',
        borderRadius: '14px',
        padding: '14px 20px',
        marginBottom: '24px',
      }">
        <NSpace :size="12" style="width: 100%;">
          <NSelect
            v-model:value="selectedCategory"
            :options="categories.map(c => ({ label: c.name, value: c.id }))"
            placeholder="分类筛选"
            clearable
            style="width: 150px;"
          />
          <NSelect
            v-model:value="selectedTag"
            :options="tags.map(t => ({ label: t.name, value: t.id }))"
            placeholder="标签筛选"
            clearable
            style="width: 150px;"
          />
          <NButton text @click="clearFilters">清除筛选</NButton>
          <div style="flex: 1;" />
          <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
            写文章
          </NButton>
        </NSpace>
      </div>

      <template v-if="initialLoading">
        <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }">
          <ArticleCardSkeleton v-for="i in 4" :key="i" />
        </div>
      </template>

      <NSpin v-else :show="loading">
        <div v-if="!loading && articles.length === 0" style="padding: 80px 0;">
          <NEmpty description="还没有文章">
            <template #extra>
              <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
                写第一篇文章
              </NButton>
            </template>
          </NEmpty>
        </div>

        <div v-else :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }">
          <div
            v-for="article in articles"
            :key="article.id"
            @click="router.push(`/article/${article.id}`)"
          >
            <ArticleCard :article="article" />
          </div>
        </div>
      </NSpin>

      <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 40px;">
        <NPagination
          :page="page"
          :page-size="pageSize"
          :item-count="total"
          @update:page="onPageChange"
        />
      </div>
    </div>
</template>

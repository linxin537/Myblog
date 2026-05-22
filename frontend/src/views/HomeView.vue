<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NInput, NSelect, NPagination, NButton, NSpin, NEmpty, NSpace, NTag, NText } from 'naive-ui'
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
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
    <!-- 搜索和筛选栏 -->
    <div class="glass" style="padding: 16px 20px; margin-bottom: 24px;">
      <NSpace vertical :size="12" style="width: 100%;">
        <NInput
          v-model:value="searchKeyword"
          placeholder="搜索文章..."
          clearable
          round
          size="large"
        >
          <template #prefix>
            <NIcon :component="Search" />
          </template>
        </NInput>
        <NSpace>
          <NSelect
            v-model:value="selectedCategory"
            :options="categories.map(c => ({ label: c.name, value: c.id }))"
            placeholder="分类筛选"
            clearable
            style="width: 160px;"
          />
          <NSelect
            v-model:value="selectedTag"
            :options="tags.map(t => ({ label: t.name, value: t.id }))"
            placeholder="标签筛选"
            clearable
            style="width: 160px;"
          />
          <NButton text @click="clearFilters">清除筛选</NButton>
          <div style="flex: 1;" />
          <NButton v-if="auth.isAuthor" type="primary" @click="router.push('/editor')">
            写文章
          </NButton>
        </NSpace>
      </NSpace>
    </div>

    <!-- 文章列表 -->
    <template v-if="initialLoading">
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <ArticleCardSkeleton v-for="i in 3" :key="i" />
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

      <div v-else style="display: flex; flex-direction: column; gap: 16px;">
        <div
          v-for="article in articles"
          :key="article.id"
          @click="router.push(`/article/${article.id}`)"
        >
          <ArticleCard :article="article" />
        </div>
      </div>
    </NSpin>

    <!-- 分页 -->
    <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 32px;">
      <NPagination
        :page="page"
        :page-size="pageSize"
        :item-count="total"
        @update:page="onPageChange"
      />
    </div>
  </div>
</template>

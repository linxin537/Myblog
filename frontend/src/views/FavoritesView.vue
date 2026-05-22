<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NPagination, NEmpty, NSpin, NText } from 'naive-ui'
import { getFavorites } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import type { ArticleInfo } from '../types/api'

const articles = ref<ArticleInfo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 10

async function load() {
  loading.value = true
  try {
    const { data } = await getFavorites({ page: page.value, page_size: pageSize })
    if (data.code === 0) {
      articles.value = (data.data || []) as ArticleInfo[]
      total.value = data.pagination?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function onPageChange(p: number) {
  page.value = p
  load()
}

onMounted(load)
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
    <NText tag="h2" style="font-size: 24px; font-weight: 700; margin-bottom: 24px;">
      我的收藏
    </NText>

    <NSpin :show="loading">
      <template v-if="!loading && articles.length === 0">
        <NEmpty description="还没有收藏任何文章" />
      </template>
      <div v-else>
        <ArticleCard
          v-for="article in articles"
          :key="article.id"
          :article="article"
          style="margin-bottom: 16px;"
        />
        <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 24px;">
          <NPagination
            :page="page"
            :page-size="pageSize"
            :item-count="total"
            @update:page="onPageChange"
          />
        </div>
      </div>
    </NSpin>
  </div>
</template>

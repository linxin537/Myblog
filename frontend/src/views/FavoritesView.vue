<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NPagination, NEmpty, NSpin, NText } from 'naive-ui'
import { getFavorites } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import type { ArticleInfo } from '../types/api'

const router = useRouter()

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
  <div :style="{ maxWidth: '820px', margin: '0 auto', paddingTop: '24px' }">
    <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700, marginBottom: '24px', display: 'block' }">
      我的收藏
    </NText>

    <NSpin :show="loading">
      <template v-if="!loading && articles.length === 0">
        <NEmpty description="还没有收藏任何文章" />
      </template>
      <div
        v-else
        :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }"
      >
        <div
          v-for="article in articles"
          :key="article.id"
          @click="router.push(`/article/${article.id}`)"
        >
          <ArticleCard :article="article" />
        </div>
      </div>
      <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 32px;">
        <NPagination
          :page="page"
          :page-size="pageSize"
          :item-count="total"
          @update:page="onPageChange"
        />
      </div>
    </NSpin>
  </div>
</template>

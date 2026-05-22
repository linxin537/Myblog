<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NText, NSpin, NEmpty, NPopconfirm, useMessage } from 'naive-ui'
import { getArticles, deleteArticle } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import type { ArticleInfo } from '../types/api'

const router = useRouter()
const message = useMessage()
const articles = ref<ArticleInfo[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await getArticles({ is_draft: true, page_size: 50 })
    if (data.code === 0) {
      articles.value = (data.data || []) as ArticleInfo[]
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  const { data } = await deleteArticle(id)
  if (data.code === 0) {
    message.success('草稿已删除')
    load()
  } else {
    message.error(data.message)
  }
}

onMounted(load)
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding-top: 24px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
      <NText tag="h2" style="font-size: 24px; font-weight: 700;">草稿管理</NText>
      <NButton type="primary" @click="router.push('/editor')">新建文章</NButton>
    </div>

    <NSpin :show="loading">
      <NEmpty v-if="!loading && articles.length === 0" description="暂无草稿">
        <template #extra>
          <NButton type="primary" @click="router.push('/editor')">开始写作</NButton>
        </template>
      </NEmpty>
      <div v-else>
        <div v-for="article in articles" :key="article.id" style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
          <div style="flex: 1;">
            <ArticleCard :article="article" />
          </div>
          <div style="display: flex; flex-direction: column; gap: 6px; flex-shrink: 0;">
            <NButton size="small" @click="router.push(`/editor/${article.id}`)">编辑</NButton>
            <NPopconfirm @positive-click="() => handleDelete(article.id)">
              <template #trigger>
                <NButton size="small" type="error" secondary>删除</NButton>
              </template>
              确定删除这个草稿？
            </NPopconfirm>
          </div>
        </div>
      </div>
    </NSpin>
  </div>
</template>

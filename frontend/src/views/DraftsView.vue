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
  <div :style="{ maxWidth: '820px', margin: '0 auto', paddingTop: '24px' }">
    <div :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }">
      <NText tag="h2" :style="{ fontSize: '24px', fontWeight: 700 }">草稿管理</NText>
      <NButton type="primary" @click="router.push('/editor')">新建文章</NButton>
    </div>

    <NSpin :show="loading">
      <NEmpty v-if="!loading && articles.length === 0" description="暂无草稿">
        <template #extra>
          <NButton type="primary" @click="router.push('/editor')">开始写作</NButton>
        </template>
      </NEmpty>
      <div
        v-else
        :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }"
      >
        <div
          v-for="article in articles"
          :key="article.id"
          :style="{
            position: 'relative',
            border: '1px solid var(--color-hairline-soft)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
          }"
        >
          <div @click="router.push(`/editor/${article.id}`)">
            <ArticleCard :article="article" />
          </div>
          <!-- Draft action overlay -->
          <div
            :style="{
              position: 'absolute',
              top: '8px',
              right: '8px',
              display: 'flex',
              gap: '6px',
            }"
          >
            <NButton
              size="tiny"
              :style="{ '--n-border-radius': '6px' }"
              @click="router.push(`/editor/${article.id}`)"
            >
              编辑
            </NButton>
            <NPopconfirm @positive-click="() => handleDelete(article.id)">
              <template #trigger>
                <NButton
                  size="tiny"
                  type="error"
                  secondary
                  :style="{ '--n-border-radius': '6px' }"
                >
                  删除
                </NButton>
              </template>
              确定删除这个草稿？
            </NPopconfirm>
          </div>
        </div>
      </div>
    </NSpin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NInput, NText, NSpace, NPagination, NEmpty, useMessage } from 'naive-ui'
import { getComments, createComment } from '../api/comments'
import { useAuthStore } from '../stores/auth'
import CommentItem from './CommentItem.vue'
import type { CommentInfo } from '../types/api'

const props = defineProps<{ articleId: number }>()

const message = useMessage()
const auth = useAuthStore()

const comments = ref<CommentInfo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 10

const newContent = ref('')
const replyTo = ref<CommentInfo | null>(null)

async function loadComments() {
  loading.value = true
  try {
    const { data } = await getComments(props.articleId, { page: page.value, page_size: pageSize })
    if (data.code === 0) {
      comments.value = (data.data || []) as CommentInfo[]
      total.value = data.pagination?.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  const content = newContent.value.trim()
  if (!content) {
    message.warning('请输入评论内容')
    return
  }
  const { data } = await createComment(props.articleId, {
    content,
    parent_id: replyTo.value?.id || null,
  })
  if (data.code === 0) {
    message.success(replyTo.value ? '回复成功' : '评论成功')
    newContent.value = ''
    replyTo.value = null
    loadComments()
  } else {
    message.error(data.message)
  }
}

function handleReply(comment: CommentInfo) {
  replyTo.value = comment
  newContent.value = ''
}

function cancelReply() {
  replyTo.value = null
  newContent.value = ''
}

function onPageChange(p: number) {
  page.value = p
  loadComments()
}

onMounted(loadComments)
</script>

<template>
  <div>
    <NText tag="h3" style="font-size: 20px; font-weight: 700; margin-bottom: 20px;">
      评论 ({{ total }})
    </NText>

    <!-- 评论输入框 -->
    <div v-if="auth.isLoggedIn" style="margin-bottom: 24px;">
      <div v-if="replyTo" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        <NText depth="3" style="font-size: 13px;">回复 @{{ replyTo.user?.username }}：</NText>
        <NButton size="tiny" text @click="cancelReply">取消</NButton>
      </div>
      <NInput
        v-model:value="newContent"
        type="textarea"
        :placeholder="replyTo ? '写下你的回复...' : '写下你的评论...'"
        :autosize="{ minRows: 3, maxRows: 8 }"
        :maxlength="1000"
        show-count
        style="margin-bottom: 12px;"
      />
      <NButton type="primary" @click="handleSubmit" :disabled="!newContent.trim()">
        {{ replyTo ? '发表回复' : '发表评论' }}
      </NButton>
    </div>
    <NText v-else depth="3" style="display: block; margin-bottom: 24px;">
      请先登录后发表评论
    </NText>

    <!-- 评论列表 -->
    <div v-if="loading" style="text-align: center; padding: 40px;">
      <NText depth="3">加载中...</NText>
    </div>
    <template v-else>
      <NEmpty v-if="comments.length === 0" description="暂无评论，来抢沙发吧" />
      <div v-else>
        <CommentItem
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :article-id="articleId"
          :on-reply="handleReply"
          :on-refresh="loadComments"
        />
        <div v-if="total > pageSize" style="display: flex; justify-content: center; margin-top: 20px;">
          <NPagination
            :page="page"
            :page-size="pageSize"
            :item-count="total"
            @update:page="onPageChange"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NText, NTag, NSpace, NInput, NPopconfirm, useMessage } from 'naive-ui'
import { updateComment, deleteComment } from '../api/comments'
import { useAuthStore } from '../stores/auth'
import type { CommentInfo } from '../types/api'

const props = defineProps<{
  comment: CommentInfo
  articleId: number
  onReply: (comment: CommentInfo) => void
  onRefresh: () => void
}>()

const message = useMessage()
const auth = useAuthStore()
const isEditing = ref(false)
const editContent = ref('')

function canModify(comment: CommentInfo) {
  if (!auth.user) return false
  return auth.isAdmin || auth.user.id === comment.user_id
}

function formatDate(d: string) {
  const date = new Date(d)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function startEdit() {
  editContent.value = props.comment.content
  isEditing.value = true
}

async function handleUpdate() {
  if (!editContent.value.trim()) return
  const { data } = await updateComment(props.comment.id, { content: editContent.value })
  if (data.code === 0) {
    message.success('已更新')
    isEditing.value = false
    props.onRefresh()
  } else {
    message.error(data.message)
  }
}

async function handleDelete() {
  const { data } = await deleteComment(props.comment.id)
  if (data.code === 0) {
    message.success('已删除')
    props.onRefresh()
  } else {
    message.error(data.message)
  }
}
</script>

<template>
  <div :style="{ marginLeft: comment.parent_id ? '24px' : '0', marginBottom: comment.parent_id ? '12px' : '20px' }">
    <div class="glass" style="padding: 14px 18px; border-radius: 12px;">
      <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
        <NText strong style="font-size: 14px;">{{ comment.user?.username || '匿名' }}</NText>
        <NTag v-if="comment.user?.role === 'admin'" type="error" size="tiny" :bordered="false">管理员</NTag>
        <NText depth="3" style="font-size: 12px;">{{ formatDate(comment.created_at) }}</NText>
      </div>

      <NInput
        v-if="isEditing"
        v-model:value="editContent"
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 6 }"
        style="margin-bottom: 8px;"
      />
      <NText v-else style="font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{{ comment.content }}</NText>

      <div v-if="isEditing" style="display: flex; gap: 8px; margin-top: 8px;">
        <NButton size="tiny" type="primary" @click="handleUpdate">保存</NButton>
        <NButton size="tiny" @click="isEditing = false">取消</NButton>
      </div>
      <div v-else style="display: flex; gap: 8px; margin-top: 8px;">
        <NButton v-if="auth.isLoggedIn" size="tiny" text @click="props.onReply(comment)">回复</NButton>
        <template v-if="canModify(comment)">
          <NButton size="tiny" text @click="startEdit">编辑</NButton>
          <NPopconfirm @positive-click="handleDelete">
            <template #trigger>
              <NButton size="tiny" text type="error">删除</NButton>
            </template>
            确定要删除这条评论吗？
          </NPopconfirm>
        </template>
      </div>
    </div>

    <div v-if="comment.replies && comment.replies.length">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :article-id="articleId"
        :on-reply="props.onReply"
        :on-refresh="props.onRefresh"
      />
    </div>
  </div>
</template>

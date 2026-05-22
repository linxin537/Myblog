<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { Heart, HeartOutline } from '@vicons/ionicons5'
import { likeArticle } from '../api/articles'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  articleId: number
  initialLiked: boolean
  initialCount: number
}>()

const emit = defineEmits<{
  (e: 'update:liked', v: boolean): void
  (e: 'update:count', v: number): void
}>()

const message = useMessage()
const auth = useAuthStore()
const pending = ref(false)

async function toggle() {
  if (!auth.isLoggedIn) {
    message.warning('请先登录')
    return
  }
  if (pending.value) return
  pending.value = true
  try {
    const { data } = await likeArticle(props.articleId)
    if (data.code === 0 && data.data) {
      emit('update:liked', data.data.liked!)
      emit('update:count', data.data.count)
    }
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <NButton
    :type="initialLiked ? 'error' : 'default'"
    secondary
    @click="toggle"
    :disabled="pending"
    style="border-radius: 20px;"
  >
    <template #icon>
      <NIcon :component="initialLiked ? Heart : HeartOutline" />
    </template>
    {{ initialCount || 0 }}
  </NButton>
</template>

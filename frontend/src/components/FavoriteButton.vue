<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { Star, StarOutline } from '@vicons/ionicons5'
import { favoriteArticle } from '../api/articles'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  articleId: number
  initialFavorited: boolean
  initialCount: number
}>()

const emit = defineEmits<{
  (e: 'update:favorited', v: boolean): void
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
    const { data } = await favoriteArticle(props.articleId)
    if (data.code === 0 && data.data) {
      emit('update:favorited', data.data.favorited!)
      emit('update:count', data.data.count)
    }
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <NButton
    :type="initialFavorited ? 'warning' : 'default'"
    secondary
    @click="toggle"
    :disabled="pending"
    style="border-radius: 20px;"
  >
    <template #icon>
      <NIcon :component="initialFavorited ? Star : StarOutline" />
    </template>
    {{ initialCount || 0 }}
  </NButton>
</template>

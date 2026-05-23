<script setup lang="ts">
import { NIcon, NBadge, NPopover, NButton, NList, NListItem, NText, NEmpty, NScrollbar } from 'naive-ui'
import { NotificationsOutline } from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notification'
import { onMounted } from 'vue'

const router = useRouter()
const store = useNotificationStore()

onMounted(async () => {
  await store.fetchItems()
})

function handleOpen() {
  store.fetchItems()
}

async function handleClick(item: { id: number; link: string | null }) {
  await store.readOne(item.id)
  if (item.link) router.push(item.link)
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = Date.now()
  const diff = now - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  return `${days} 天前`
}
</script>

<template>
  <NPopover
    trigger="click"
    placement="bottom-end"
    :style="{ padding: 0, width: '360px' }"
    @update:show="handleOpen"
  >
    <template #trigger>
      <NButton quaternary circle>
        <template #icon>
          <NBadge :value="store.unreadCount" :max="99" :show="store.unreadCount > 0">
            <NIcon :component="NotificationsOutline" :size="22" />
          </NBadge>
        </template>
      </NButton>
    </template>

    <div :style="{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid var(--color-hairline-soft)' }">
      <NText strong :style="{ fontSize: '14px' }">通知</NText>
      <NButton
        v-if="store.unreadCount > 0"
        text
        size="tiny"
        :style="{ fontSize: '12px', color: 'var(--color-primary)' }"
        @click="store.readAll()"
      >
        全部标为已读
      </NButton>
    </div>

    <NScrollbar :style="{ maxHeight: '400px' }">
      <NEmpty v-if="store.items.length === 0" description="暂无通知" :style="{ padding: '32px' }" />
      <NList v-else>
        <NListItem
          v-for="item in store.items"
          :key="item.id"
          :style="{
            padding: '12px 16px',
            cursor: 'pointer',
            background: item.is_read ? 'transparent' : 'var(--color-surface-soft)',
            opacity: item.is_read ? 0.7 : 1,
          }"
          @click="handleClick(item)"
        >
          <div>
            <NText :style="{ fontSize: '14px', fontWeight: item.is_read ? 400 : 600 }">
              {{ item.title }}
            </NText>
            <br>
            <NText :depth="3" :style="{ fontSize: '13px' }">{{ item.content }}</NText>
            <br>
            <NText :depth="3" :style="{ fontSize: '11px' }">{{ formatTime(item.created_at) }}</NText>
          </div>
        </NListItem>
      </NList>
    </NScrollbar>
  </NPopover>
</template>

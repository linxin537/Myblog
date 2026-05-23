import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getNotifications,
  getUnreadCount,
  markRead,
  markAllRead,
  type NotificationItem,
} from '../api/notifications'
import { useAuthStore } from './auth'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)
  const items = ref<NotificationItem[]>([])
  let pollingTimer: ReturnType<typeof setInterval> | null = null

  async function fetchUnreadCount() {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return
    try {
      const res = await getUnreadCount()
      unreadCount.value = res.data.data?.count ?? 0
    } catch {
      // Silently fail
    }
  }

  async function fetchItems(page = 1) {
    try {
      const res = await getNotifications(page)
      items.value = res.data.data?.items ?? []
    } catch {
      // Silently fail
    }
  }

  async function readOne(id: number) {
    try {
      await markRead(id)
      const item = items.value.find((n) => n.id === id)
      if (item) item.is_read = true
      await fetchUnreadCount()
    } catch {
      // Silently fail
    }
  }

  async function readAll() {
    try {
      await markAllRead()
      items.value.forEach((n) => (n.is_read = true))
      unreadCount.value = 0
    } catch {
      // Silently fail
    }
  }

  function startPolling() {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return
    fetchUnreadCount()
    pollingTimer = setInterval(fetchUnreadCount, 60000)
  }

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  return { unreadCount, items, fetchUnreadCount, fetchItems, readOne, readAll, startPolling, stopPolling }
})

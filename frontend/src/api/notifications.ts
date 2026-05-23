import client from './client'
import type { ApiResponse } from '../types/api'

export interface NotificationItem {
  id: number
  type: 'comment' | 'reply' | 'like' | 'system'
  title: string
  content: string
  link: string | null
  is_read: boolean
  created_at: string
}

export interface NotificationListData {
  items: NotificationItem[]
  total: number
  total_pages: number
}

export function getNotifications(page = 1, pageSize = 20) {
  return client.get<ApiResponse<NotificationListData>>('/notifications', {
    params: { page, page_size: pageSize },
  })
}

export function markRead(notificationId: number) {
  return client.put<ApiResponse<NotificationItem>>(`/notifications/${notificationId}/read`)
}

export function markAllRead() {
  return client.put<ApiResponse>('/notifications/read-all')
}

export function getUnreadCount() {
  return client.get<ApiResponse<{ count: number }>>('/notifications/unread-count')
}

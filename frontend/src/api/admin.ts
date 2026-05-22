import client from './client'
import type { ApiResponse, PaginatedResponse } from '../types/api'

export interface UserManageInfo {
  id: number
  username: string
  email: string
  role: string
  avatar: string | null
  bio: string | null
  is_active: boolean
  login_attempts: number
  locked_until: string | null
  created_at: string
  updated_at: string | null
}

export interface AuditLogInfo {
  id: number
  user_id: number | null
  username: string | null
  action: string
  target_type: string | null
  target_id: number | null
  ip_address: string | null
  detail: string | null
  created_at: string
}

export function getUsers(params?: { page?: number; page_size?: number; search?: string; role?: string }) {
  return client.get<PaginatedResponse<UserManageInfo>>('/admin/users', { params })
}

export function updateUserRole(userId: number, role: string) {
  return client.put<ApiResponse<UserManageInfo>>(`/admin/users/${userId}/role`, { role })
}

export function updateUserStatus(userId: number, isActive: boolean) {
  return client.put<ApiResponse<UserManageInfo>>(`/admin/users/${userId}/status`, { is_active: isActive })
}

export function getAuditLogs(params?: { page?: number; page_size?: number; action?: string; user_id?: number }) {
  return client.get<PaginatedResponse<AuditLogInfo>>('/admin/audit-logs', { params })
}

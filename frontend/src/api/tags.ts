import client from './client'
import type { ApiResponse, TagInfo, TagForm } from '../types/api'

export function getTags() {
  return client.get<ApiResponse<TagInfo[]>>('/tags')
}

export function createTag(data: TagForm) {
  return client.post<ApiResponse<TagInfo>>('/tags', data)
}

export function updateTag(id: number, data: TagForm) {
  return client.put<ApiResponse<TagInfo>>(`/tags/${id}`, data)
}

export function deleteTag(id: number) {
  return client.delete<ApiResponse<null>>(`/tags/${id}`)
}

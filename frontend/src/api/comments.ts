import client from './client'
import type { ApiResponse, PaginatedResponse, CommentInfo, CommentForm } from '../types/api'

export function getComments(articleId: number, params?: { page?: number; page_size?: number }) {
  return client.get<PaginatedResponse<CommentInfo>>(`/articles/${articleId}/comments`, { params })
}

export function createComment(articleId: number, data: CommentForm) {
  return client.post<ApiResponse<CommentInfo>>(`/articles/${articleId}/comments`, data)
}

export function updateComment(id: number, data: { content: string }) {
  return client.put<ApiResponse<CommentInfo>>(`/comments/${id}`, data)
}

export function deleteComment(id: number) {
  return client.delete<ApiResponse<null>>(`/comments/${id}`)
}

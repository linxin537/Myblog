import client from './client'
import type { ApiResponse, PaginatedResponse, ArticleInfo, ArticleDetail, ArticleForm, ToggleResponse } from '../types/api'

export function getArticles(params?: {
  page?: number
  page_size?: number
  category_id?: number
  tag_id?: number
  is_draft?: boolean
  search?: string
}) {
  return client.get<PaginatedResponse<ArticleInfo>>('/articles', { params })
}

export function getArticle(id: number) {
  return client.get<ApiResponse<ArticleDetail>>(`/articles/${id}`)
}

export function createArticle(data: ArticleForm) {
  return client.post<ApiResponse<ArticleDetail>>('/articles', data)
}

export function updateArticle(id: number, data: Partial<ArticleForm>) {
  return client.put<ApiResponse<ArticleDetail>>(`/articles/${id}`, data)
}

export function deleteArticle(id: number) {
  return client.delete<ApiResponse<null>>(`/articles/${id}`)
}

export function likeArticle(id: number) {
  return client.post<ApiResponse<ToggleResponse>>(`/articles/${id}/like`)
}

export function favoriteArticle(id: number) {
  return client.post<ApiResponse<ToggleResponse>>(`/articles/${id}/favorite`)
}

export function getFavorites(params?: { page?: number; page_size?: number }) {
  return client.get<PaginatedResponse<ArticleInfo>>('/articles/favorites', { params })
}

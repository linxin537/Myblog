import client from './client'
import type { ApiResponse, CategoryInfo, CategoryForm } from '../types/api'

export function getCategories() {
  return client.get<ApiResponse<CategoryInfo[]>>('/categories')
}

export function createCategory(data: CategoryForm) {
  return client.post<ApiResponse<CategoryInfo>>('/categories', data)
}

export function updateCategory(id: number, data: CategoryForm) {
  return client.put<ApiResponse<CategoryInfo>>(`/categories/${id}`, data)
}

export function deleteCategory(id: number) {
  return client.delete<ApiResponse<null>>(`/categories/${id}`)
}

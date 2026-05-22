import client from './client'
import type { ApiResponse, PaginatedResponse, FileInfo } from '../types/api'

export function uploadFile(file: File, onProgress?: (pct: number) => void) {
  const form = new FormData()
  form.append('file', file)
  return client.post<ApiResponse<FileInfo>>('/files/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}

export function getFiles(params?: { page?: number; page_size?: number }) {
  return client.get<PaginatedResponse<FileInfo>>('/files', { params })
}

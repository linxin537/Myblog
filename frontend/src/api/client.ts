import axios from 'axios'
import type { ApiResponse } from '../types/api'

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  timeout: 10000,
})

let isRefreshing = false
let refreshQueue: Array<(token: string) => void> = []

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(client(originalRequest)))
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })
        refreshQueue.forEach((cb) => cb(''))
        refreshQueue = []
        return client(originalRequest)
      } catch {
        refreshQueue = []
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default client

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiResponse | undefined
    if (data?.message) return data.message
    if (error.message) return error.message
  }
  return '请求失败'
}

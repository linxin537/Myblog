export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T | null
}

export interface PaginationMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PaginatedResponse<T = unknown> extends ApiResponse<T[]> {
  pagination: PaginationMeta | null
}

export interface UserInfo {
  id: number
  username: string
  email: string
  role: 'admin' | 'author' | 'reader'
  avatar: string | null
  bio: string | null
  is_active: boolean
  created_at: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserInfo
}

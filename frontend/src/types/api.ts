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

// 文章
export interface ArticleInfo {
  id: number
  title: string
  summary: string | null
  cover_image: string | null
  author_id: number
  view_count: number
  is_draft: boolean
  is_pinned: boolean
  published_at: string | null
  created_at: string
  author: UserInfo | null
  category: CategoryInfo | null
  tags: TagInfo[]
}

export interface ArticleDetail extends ArticleInfo {
  content: string
  html_content: string | null
  updated_at: string | null
}

export interface ArticleForm {
  title: string
  content: string
  summary?: string | null
  cover_image?: string | null
  category_id?: number | null
  tag_ids?: number[]
  is_draft?: boolean
  is_pinned?: boolean
}

// 分类
export interface CategoryInfo {
  id: number
  name: string
  description: string | null
  sort_order: number
  created_at: string
  updated_at: string | null
}

export interface CategoryForm {
  name: string
  description?: string | null
  sort_order?: number
}

// 标签
export interface TagInfo {
  id: number
  name: string
  created_at: string
  updated_at: string | null
}

export interface TagForm {
  name: string
}

// 文件
export interface FileInfo {
  id: number
  original_name: string
  path: string
  size: number
  mime_type: string
  uploader_id: number
  created_at: string
  thumb_path?: string
  uploader?: UserInfo | null
}

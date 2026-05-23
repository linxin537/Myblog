import client from './client'
import type { ApiResponse, LoginResponse, UserInfo } from '../types/api'

export function register(username: string, email: string, password: string) {
  return client.post<ApiResponse<UserInfo>>('/auth/register', { username, email, password })
}

export function login(username: string, password: string, rememberMe = false) {
  return client.post<ApiResponse<LoginResponse>>('/auth/login', {
    username,
    password,
    remember_me: rememberMe,
  })
}

export function logout() {
  return client.post<ApiResponse>('/auth/logout')
}

export function getMe() {
  return client.get<ApiResponse<UserInfo>>('/users/me')
}

export function updateMe(data: { avatar?: string; bio?: string }) {
  return client.put<ApiResponse<UserInfo>>('/users/me', data)
}

export function forgotPassword(email: string) {
  return client.post<ApiResponse>('/auth/forgot-password', { email })
}

export function resetPassword(token: string, newPassword: string) {
  return client.post<ApiResponse>('/auth/reset-password', { token, new_password: newPassword })
}

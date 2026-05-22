import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '../types/api'
import * as authApi from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isAuthor = computed(() => user.value?.role === 'author' || user.value?.role === 'admin')
  const hasFetched = ref(false)

  async function fetchUser() {
    if (hasFetched.value) return
    hasFetched.value = true
    try {
      const { data } = await authApi.getMe()
      if (data.code === 0 && data.data) {
        user.value = data.data
      }
    } catch {
      user.value = null
    }
  }

  async function login(username: string, password: string, rememberMe = false) {
    const { data } = await authApi.login(username, password, rememberMe)
    if (data.code === 0 && data.data) {
      user.value = data.data.user
      hasFetched.value = true
    }
    return data
  }

  async function register(username: string, email: string, password: string) {
    const { data } = await authApi.register(username, email, password)
    return data
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      hasFetched.value = false
    }
  }

  return { user, isLoggedIn, isAdmin, isAuthor, fetchUser, login, register, logout }
})

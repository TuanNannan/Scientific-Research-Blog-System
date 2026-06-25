import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api'

interface User {
  id: number
  username: string
  email: string
  role: string
  avatar?: string
  bio?: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res: any = await userApi.login({ username, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('access_token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
    return res
  }

  async function register(username: string, email: string, password: string) {
    const res: any = await userApi.register({ username, email, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('access_token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
    return res
  }

  async function fetchUser() {
    try {
      const res: any = await userApi.getMe()
      user.value = res
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    fetchUser,
    logout,
  }
})
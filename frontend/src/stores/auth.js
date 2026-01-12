import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),

  actions: {
    async login(credentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials)
        this.token = response.data.access_token
        this.user = response.data.user
        this.isAuthenticated = true
        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || '登录失败')
      }
    },

    async register(userData) {
      try {
        const response = await axios.post('/api/auth/register', userData)
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || '注册失败')
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    async getProfile() {
      try {
        const response = await axios.get('/api/auth/profile')
        this.user = response.data.user
        return response.data
      } catch (error) {
        this.logout()
        throw new Error('获取用户信息失败')
      }
    },

    init() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})
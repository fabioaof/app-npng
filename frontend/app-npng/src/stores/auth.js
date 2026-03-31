import { defineStore } from 'pinia'
import { api } from 'src/api/client'

const TOKEN_KEY = 'npng_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: typeof localStorage !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null,
    user: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    isProfessional: (s) => s.user?.role === 'professional',
  },
  actions: {
    setToken (token) {
      this.token = token
      if (token) localStorage.setItem(TOKEN_KEY, token)
      else localStorage.removeItem(TOKEN_KEY)
    },
    setUser (user) {
      this.user = user
    },
    async fetchMe () {
      const { data } = await api.get('/auth/me')
      this.user = data
      return data
    },
    async login (email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.setToken(data.access_token)
      await this.fetchMe()
    },
    async register (payload) {
      await api.post('/auth/register', payload)
      await this.login(payload.email, payload.password)
    },
    logout () {
      this.setToken(null)
      this.user = null
    },
  },
})

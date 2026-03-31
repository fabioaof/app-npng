import axios from 'axios'

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('npng_token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // FormData precisa do boundary no Content-Type; o default application/json quebra o upload.
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

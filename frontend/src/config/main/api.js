/**
 * API Service - Django Backend Configuration
 * 
 * This file is for the main branch (Django backend).
 */
import axios from 'axios'
import router from '@/router'

// Django API
const djangoApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add auth token (Django only)
djangoApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor - Handle token refresh (Django only)
djangoApi.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh/`,
          { refresh: refreshToken }
        )

        const { access } = response.data
        localStorage.setItem('access_token', access)

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`
        return djangoApi(originalRequest)
      } catch (refreshError) {
        // Refresh failed - logout user and trigger login modal and redirect to home
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_role')
        // Save intended path so user can be redirected after login
        try {
          sessionStorage.setItem('intended_path', window.location.pathname + window.location.search)
        } catch (e) {
          // ignore sessionStorage errors
        }
        // Trigger the global login modal used by the app
        window.dispatchEvent(new Event('show-login'))
        // Redirect to homepage
        try {
          router.push('/')
        } catch (err) {
          // fallback to full reload if router push fails
          window.location.href = '/'
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Django API methods
const api = {
  get: async (...args) => {
    return djangoApi.get(...args)
  },

  post: async (...args) => {
    return djangoApi.post(...args)
  },

  patch: async (...args) => {
    return djangoApi.patch(...args)
  },

  put: async (...args) => {
    return djangoApi.put(...args)
  },

  delete: async (...args) => {
    return djangoApi.delete(...args)
  }
}

const fetchSubjects = () => api.get('/question_bank/subjects/')

const USE_SUPABASE = false

export { fetchSubjects, USE_SUPABASE }
export default api

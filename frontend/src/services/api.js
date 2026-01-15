import axios from 'axios'
import router from '@/router'

// Check if we should use Supabase
const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'

// Dynamic import for Supabase API
let supabaseApi = null
if (USE_SUPABASE) {
  import('./apiSupabase.js').then(module => {
    supabaseApi = module.default
  })
}

// Django API (fallback)
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

// Create a proxy that routes to appropriate backend
const api = new Proxy({}, {
  get(target, prop) {
    return async (...args) => {
      // Use Supabase if enabled and loaded
      if (USE_SUPABASE && supabaseApi) {
        return supabaseApi[prop](...args)
      }
      // Fallback to Django
      return djangoApi[prop](...args)
    }
  }
})

// For synchronous access (before dynamic import loads)
api.get = async (...args) => {
  if (USE_SUPABASE && supabaseApi) {
    return supabaseApi.get(...args)
  }
  return djangoApi.get(...args)
}

api.post = async (...args) => {
  if (USE_SUPABASE && supabaseApi) {
    return supabaseApi.post(...args)
  }
  return djangoApi.post(...args)
}

api.patch = async (...args) => {
  if (USE_SUPABASE && supabaseApi) {
    return supabaseApi.patch(...args)
  }
  return djangoApi.patch(...args)
}

api.put = async (...args) => {
  if (USE_SUPABASE && supabaseApi) {
    return supabaseApi.put(...args)
  }
  return djangoApi.put(...args)
}

api.delete = async (...args) => {
  if (USE_SUPABASE && supabaseApi) {
    return supabaseApi.delete(...args)
  }
  return djangoApi.delete(...args)
}

const fetchSubjects = () => api.get('/question_bank/subjects/')

export { fetchSubjects, USE_SUPABASE }
export default api


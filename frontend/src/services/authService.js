import api from './api'

const authService = {
  /**
   * 登入
   * @param {Object} credentials - {username, password}
   * @returns {Promise} 登入結果，包含 access 和 refresh token
   */
  async login(credentials) {
    const response = await api.post('/auth/login/', credentials)
    const { access, refresh } = response.data

    // 儲存 tokens
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    // 解析 JWT token 取得使用者資訊
    const userInfo = this.parseJWT(access)
    console.log('JWT Token 內容:', userInfo) // 調試用

    if (userInfo) {
      // 嘗試不同的欄位名稱
      const userId = userInfo.user_id || userInfo.id || userInfo.sub
      const username = userInfo.username || userInfo.name || userInfo.email || credentials.username

      localStorage.setItem('user_id', userId || '')
      localStorage.setItem('username', username || '')

      // 檢查是否為管理員（檢查多種可能的欄位）
      const isAdmin = userInfo.is_staff ||
                     userInfo.is_superuser ||
                     userInfo.isStaff ||
                     userInfo.isSuperuser ||
                     userInfo.role === 'admin' ||
                     userInfo.role === 'staff'

      if (isAdmin) {
        localStorage.setItem('user_role', 'admin')
      } else {
        localStorage.setItem('user_role', 'user')
      }

      console.log('已設定使用者角色:', localStorage.getItem('user_role'))
    }

    return response
  },

  /**
   * 登出
   */
  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('user_role')
  },

  /**
   * 檢查是否已登入
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },

  /**
   * 取得當前使用者資訊
   * @returns {Object|null}
   */
  getCurrentUser() {
    const token = localStorage.getItem('access_token')
    if (!token) return null

    return {
      id: localStorage.getItem('user_id'),
      username: localStorage.getItem('username'),
      role: localStorage.getItem('user_role'),
      isAdmin: localStorage.getItem('user_role') === 'admin'
    }
  },

  /**
   * 解析 JWT token
   * @param {string} token
   * @returns {Object|null}
   */
  parseJWT(token) {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('JWT 解析失敗:', error)
      return null
    }
  },

  /**
   * 刷新 token
   * @returns {Promise}
   */
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await api.post('/auth/refresh/', {
      refresh: refreshToken
    })

    const { access } = response.data
    localStorage.setItem('access_token', access)

    return response
  }
}

export default authService

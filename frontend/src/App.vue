<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import authService from './services/authService'

const router = useRouter()
const route = useRoute()

const tabs = [
  { name: '練習模式', path: '/practice', key: 'practice' },
  { name: '快閃卡', path: '/flashcard', key: 'flashcard' },
  { name: '學習追蹤', path: '/analytics', key: 'analytics' },
  { name: '題庫管理', path: '/admin', key: 'admin' }
]

const activeTab = ref(route.path.split('/')[1] || 'practice')
const showLoginModal = ref(false)

// 使用 ref 來追蹤登入狀態變化
const loginStateVersion = ref(0)

// 檢查是否已登入
const isAuthenticated = computed(() => {
  loginStateVersion.value // 依賴此值來觸發重新計算
  return authService.isAuthenticated()
})

// 取得當前使用者（computed 會自動響應變化）
const currentUser = computed(() => {
  loginStateVersion.value // 依賴此值來觸發重新計算
  return authService.getCurrentUser()
})

const switchTab = (path, key) => {
  activeTab.value = key
  router.push(path)
}

const handleLogin = () => {
  showLoginModal.value = true
}

const handleLogout = () => {
  if (confirm('確定要登出嗎？')) {
    authService.logout()
    loginStateVersion.value++ // 觸發響應式更新
    router.push('/practice')
  }
}

const handleLoginSuccess = () => {
  console.log('處理登入成功事件')

  // 關閉登入彈窗
  showLoginModal.value = false

  // 觸發響應式更新
  loginStateVersion.value++
  console.log('已更新登入狀態，currentUser:', currentUser.value)

  // 如果之前要訪問管理頁面，登入後跳轉過去
  const intendedPath = sessionStorage.getItem('intended_path')
  if (intendedPath) {
    sessionStorage.removeItem('intended_path')
    router.push(intendedPath)
  }
}

// 全域監聽需要登入的事件
const showLogin = () => {
  showLoginModal.value = true
}

// 掛載時註冊全域事件監聽器
onMounted(() => {
  // 註冊全域事件監聽器
  window.addEventListener('show-login', showLogin)
})
</script>

<template>
  <div class="app-container">
    <!-- Header -->
    <header>
      <div class="header-content">
        <div class="header-text">
          <h1>司律考題練習題庫系統</h1>
          <p>整合歷屆司法官／律師考題，提供智慧複習、學習追蹤與快閃卡管理</p>
        </div>
        <div class="user-section">
          <div v-if="isAuthenticated" class="user-info">
            <span class="username">{{ currentUser?.username }}</span>
            <span v-if="currentUser?.isAdmin" class="admin-badge">管理員</span>
            <button class="btn btn-logout" @click="handleLogout">登出</button>
          </div>
          <button v-else class="btn btn-login" @click="handleLogin">登入</button>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav>
      <div class="nav-container">
        <a
          v-for="tab in tabs"
          :key="tab.key"
          href="#"
          :class="{ active: activeTab === tab.key }"
          @click.prevent="switchTab(tab.path, tab.key)"
        >
          {{ tab.name }}
        </a>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <router-view />
    </main>

    <!-- Login Modal -->
    <LoginModal
      :visible="showLoginModal"
      @close="showLoginModal = false"
      @success="handleLoginSuccess"
    />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* Header */
header {
  background: white;
  padding: 24px 0;
  border-bottom: 1px solid #e0e0e0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text {
  flex: 1;
}

header h1 {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 6px;
}

header p {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

/* User Section */
.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f5f5f5;
  border-radius: 24px;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.admin-badge {
  padding: 3px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-login {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-logout {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-logout:hover {
  background: #e0e0e0;
  color: #333;
}

/* Navigation */
nav {
  background: white;
  border-bottom: 2px solid #e0e0e0;
  padding: 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 0;
  padding: 0 24px;
}

nav a {
  padding: 16px 32px;
  text-decoration: none;
  color: #666;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  cursor: pointer;
}

nav a:hover {
  color: #007bff;
}

nav a.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

/* Main */
main {
  padding: 40px 0;
  max-width: 1200px;
  margin: 0 auto;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .header-text {
    width: 100%;
  }

  header h1 {
    font-size: 24px;
  }

  header p {
    font-size: 13px;
  }

  .nav-container {
    flex-wrap: wrap;
  }

  nav a {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>

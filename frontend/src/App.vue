<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import authService from './services/authService'

const router = useRouter()
const route = useRoute()

const tabs = [
  { name: '首頁', path: '/', key: 'landing' },
  { name: '練習模式', path: '/practice', key: 'practice' },
  { name: '快閃卡', path: '/flashcard', key: 'flashcard' },
  { name: 'AI 助手', path: '/ai-chat', key: 'ai-chat' },
  { name: '學習追蹤', path: '/analytics', key: 'analytics' },
  { name: '題庫管理', path: '/admin', key: 'admin' }
]

const activeTab = ref(route.path === '/' ? 'landing' : route.path.split('/')[1] || 'practice')
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
:global(:root) {
  --bg-soft: #f6f7f9;
  --surface: #ffffff;
  --surface-muted: #f0f2f5;
  --primary: #2f5f90;
  --primary-soft: #e6eef7;
  --text-primary: #1f2933;
  --text-secondary: #4b5563;
  --border: #dce1e7;
  --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  --radius: 12px;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f7f9fc 0%, #fdfefe 100%);
  color: var(--text-primary);
  font-family: "Inter", "Noto Sans TC", system-ui, -apple-system, sans-serif;
}

/* Header */
header {
  background: var(--surface);
  padding: 22px 0;
  border-bottom: 1px solid var(--border);
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.04);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
}

.header-text {
  flex: 1;
}

header h1 {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: 0.01em;
}

header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* User Section */
.user-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  background: var(--surface-muted);
  border-radius: 999px;
  border: 1px solid var(--border);
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-badge {
  padding: 4px 10px;
  background: var(--primary-soft);
  color: var(--primary);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-login {
  background: var(--primary);
  color: #f7f9fc;
  box-shadow: var(--shadow);
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(47, 95, 144, 0.18);
}

.btn-logout {
  background: var(--surface);
  color: var(--text-secondary);
  border-color: var(--border);
}

.btn-logout:hover {
  background: var(--surface-muted);
  color: var(--text-primary);
}

/* Navigation */
nav {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: 4px;
  padding: 0 16px;
}

nav a {
  padding: 14px 18px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  border-radius: 10px 10px 0 0;
  transition: all 0.2s ease;
  cursor: pointer;
}

nav a:hover {
  color: var(--primary);
  background: var(--primary-soft);
}

nav a.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
  background: var(--primary-soft);
}

/* Main */
main {
  min-height: calc(100vh - 140px);
  background: linear-gradient(180deg, #f7f8fb 0%, #fdfefe 100%);
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    grid-template-columns: 1fr;
    gap: 14px;
    text-align: center;
  }

  header h1 {
    font-size: 22px;
  }

  header p {
    font-size: 13px;
  }

  .nav-container {
    grid-auto-flow: row;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  nav a {
    padding: 12px 14px;
    font-size: 14px;
  }
}
</style>

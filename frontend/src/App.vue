<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import ThemeToggle from './components/common/ThemeToggle.vue'
import authService from './services/authService'
import { supabase } from './lib/supabase'

const router = useRouter()
const route = useRoute()

// Check if using Supabase
const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'

const tabs = [
  { name: '首頁', path: '/', key: 'landing', icon: 'bi-house-door' },
  { name: '練習模式', path: '/practice', key: 'practice', icon: 'bi-pencil-square' },
  { name: '我的考卷', path: '/user-exam', key: 'user-exam', icon: 'bi-journal-text' },
  { name: '快閃卡', path: '/flashcard', key: 'flashcard', icon: 'bi-card-text' },
  { name: 'AI 申論解析', path: '/essay-analysis', key: 'essay-analysis', icon: 'bi-robot' },
  { name: '學習追蹤', path: '/analytics', key: 'analytics', icon: 'bi-graph-up' },
  { name: '題庫管理', path: '/admin', key: 'admin', adminOnly: true, icon: 'bi-gear' }
]

// We don't need an `activeTab` ref – router-link provides active-class handling
const showLoginModal = ref(false)

// 使用 ref 來追蹤登入狀態變化
const loginStateVersion = ref(0)

// Store for Supabase user
const supabaseUser = ref(null)

// 檢查是否已登入
const isAuthenticated = computed(() => {
  loginStateVersion.value // 依賴此值來觸發重新計算
  if (USE_SUPABASE) {
    return !!supabaseUser.value
  }
  return authService.isAuthenticated()
})

// 取得當前使用者（computed 會自動響應變化）
const currentUser = computed(() => {
  loginStateVersion.value // 依賴此值來觸發重新計算
  
  if (USE_SUPABASE && supabaseUser.value) {
    const user = supabaseUser.value
    return {
      id: user.id,
      username: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
      email: user.email,
      isAdmin: user.user_metadata?.is_admin || false,
      role: user.user_metadata?.is_admin ? 'admin' : 'user'
    }
  }
  
  return authService.getCurrentUser()
})

// 根據使用者角色篩選可見的 tabs
const visibleTabs = computed(() => {
  // 未登入時只顯示「首頁」
  if (!isAuthenticated.value) {
    return tabs.filter(tab => tab.key === 'landing')
  }

  // 已登入時根據權限顯示 tabs
  return tabs.filter(tab => {
    if (tab.adminOnly) {
      return currentUser.value?.isAdmin
    }
    return true
  })
})

// `switchTab` 已移除：改用 router-link 做導航，並由 `route` 自動同步 `activeTab`。

const handleLogin = () => {
  showLoginModal.value = true
}

const handleLogout = async () => {
  if (confirm('確定要登出嗎？')) {
    if (USE_SUPABASE) {
      await supabase.auth.signOut()
    } else {
      authService.logout()
    }
    supabaseUser.value = null
    loginStateVersion.value++ // 觸發響應式更新
    router.push('/')
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
  // show login modal (closable)
  showLoginModal.value = true
}

const handleModalClose = () => {
  showLoginModal.value = false
}

// Auth state subscription
let authSubscription = null

// 掛載時註冊全域事件監聽器
onMounted(async () => {
  // 註冊全域事件監聽器
  window.addEventListener('show-login', showLogin)
  
  // Subscribe to Supabase auth state changes
  if (USE_SUPABASE) {
    // Get initial session
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      supabaseUser.value = session.user
      console.log('Initial Supabase user:', session.user.email, 'isAdmin:', session.user.user_metadata?.is_admin)
    }
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event, session?.user?.email)
      supabaseUser.value = session?.user || null
      loginStateVersion.value++
      
      // Update localStorage for compatibility
      if (session?.user) {
        localStorage.setItem('user_id', session.user.id)
        localStorage.setItem('username', session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'User')
        localStorage.setItem('user_role', session.user.user_metadata?.is_admin ? 'admin' : 'user')
      } else {
        localStorage.removeItem('user_id')
        localStorage.removeItem('username')
        localStorage.removeItem('user_role')
      }
    })
    authSubscription = subscription
  }
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('show-login', showLogin)
  if (authSubscription) {
    authSubscription.unsubscribe()
  }
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
          <ThemeToggle />
          <div v-if="isAuthenticated" class="user-info">
            <span class="username hidden-mobile">{{ currentUser?.username }}</span>
            <span v-if="currentUser?.isAdmin" class="admin-badge hidden-mobile">管理員</span>
            <button class="btn btn-logout icon-only-mobile" @click="handleLogout">
              <span class="hidden-mobile">登出</span>
              <i class="bi bi-box-arrow-right hidden-desktop"></i>
            </button>
          </div>
          <button v-else class="btn btn-login" @click="handleLogin">登入</button>
        </div>
      </div>
    </header>

    <!-- Desktop Navigation -->
    <nav class="desktop-nav hidden-mobile">
      <div class="nav-container">
        <router-link v-for="tab in visibleTabs" :key="tab.key" :to="tab.path" active-class="active"
          exact-active-class="active">
          <i :class="['bi', tab.icon, 'me-1']"></i>
          {{ tab.name }}
        </router-link>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Mobile Bottom Navigation -->
    <nav class="mobile-nav hidden-desktop">
      <router-link v-for="tab in visibleTabs" :key="tab.key" :to="tab.path" active-class="active"
        exact-active-class="active" class="mobile-nav-item">
        <i :class="['bi', tab.icon]"></i>
        <span class="nav-label">{{ tab.name }}</span>
      </router-link>
    </nav>

    <!-- Login Modal -->
    <LoginModal :visible="showLoginModal" @close="handleModalClose" @success="handleLoginSuccess" />
  </div>
</template>

<style scoped>
:global(:root) {
  /* Light Mode - Professional Slate & Steel */
  --bg-page: #F8FAFC;
  --surface: #FFFFFF;
  --surface-muted: #E2E8F0;
  
  /* Primary: Professional Slate Blue */
  --primary: #476996;
  --primary-hover: #35527a;
  --primary-soft: #EEF2FF;
  
  /* Text */
  --text-primary: #1E293B;
  --text-secondary: #64748B;
  
  /* Status Colors */
  --success: #22c55e;
  --success-soft: #dcfce7;
  --warning: #f59e0b;
  --warning-soft: #fef3c7;
  --destructive: #ef4444;
  --destructive-soft: #fee2e2;
  
  /* Borders & Shadows */
  --border: #CBD5E1;
  --shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.1), 0 2px 4px -1px rgba(15, 23, 42, 0.06);
  --shadow-hover: 0 10px 15px -3px rgba(15, 23, 42, 0.1), 0 4px 6px -2px rgba(15, 23, 42, 0.05);
  --shadow-card: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
  --radius: 12px;
  
  /* Gradient tokens */
  --gradient-hero: linear-gradient(135deg, var(--surface) 0%, rgba(71, 105, 150, 0.08) 10%, #EEF2FF 50%, #E2E8F0 100%);
  --gradient-card: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  
  /* Enhanced Shadows */
  --shadow-elegant: 0 4px 20px -2px rgba(15, 23, 42, 0.08), 0 2px 8px -2px rgba(15, 23, 42, 0.04);
  --shadow-glow: 0 0 20px rgba(71, 105, 150, 0.15);
  
  /* Glass Effect */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
  
  /* Icon Color Palettes */
  --icon-blue-bg: #eff6ff;
  --icon-blue-fg: #3b82f6;
  --icon-green-bg: #ecfdf5;
  --icon-green-fg: #10b981;
  --icon-purple-bg: #f5f3ff;
  --icon-purple-fg: #8b5cf6;
  --icon-orange-bg: #fff7ed;
  --icon-orange-fg: #f97316;
  --icon-amber-bg: #fffbeb;
  --icon-amber-fg: #f59e0b;

  /* Mobile-First Breakpoints */
  --bp-phone-plus: 480px;
  --bp-tablet-sm: 640px;
  --bp-tablet: 768px;
  --bp-tablet-lg: 1024px;
  --bp-desktop: 1200px;
}

/* Dark Mode */
:global(.dark) {
  --bg-page: #0f172a;
  --surface: #1e293b;
  --surface-muted: #334155;
  
  --primary: #60a5fa;
  --primary-hover: #3b82f6;
  --primary-soft: #1e3a5f;
  
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  
  --success: #4ade80;
  --success-soft: #14532d;
  --warning: #fbbf24;
  --warning-soft: #713f12;
  --destructive: #f87171;
  --destructive-soft: #7f1d1d;
  
  --border: #334155;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
  --shadow-hover: 0 20px 40px -10px rgba(96, 165, 250, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.3);
  --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
  
  --gradient-hero: linear-gradient(135deg, var(--surface) 0%, rgba(96, 165, 250, 0.1) 10%, #1e293b 50%, #0f172a 100%);
  --gradient-card: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  
  /* Enhanced Shadows (Dark) */
  --shadow-elegant: 0 4px 20px -2px rgba(0, 0, 0, 0.3), 0 2px 8px -2px rgba(0, 0, 0, 0.2);
  --shadow-glow: 0 0 20px rgba(96, 165, 250, 0.2);
  
  /* Glass Effect (Dark) - More transparent for blending */
  --glass-bg: rgba(30, 41, 59, 0.4);
  --glass-border: rgba(255, 255, 255, 0.08);
  
  /* Icon Color Palettes (Dark) */
  --icon-blue-bg: rgba(59, 130, 246, 0.15);
  --icon-blue-fg: #60a5fa;
  --icon-green-bg: rgba(16, 185, 129, 0.15);
  --icon-green-fg: #34d399;
  --icon-purple-bg: rgba(139, 92, 246, 0.15);
  --icon-purple-fg: #a78bfa;
  --icon-orange-bg: rgba(249, 115, 22, 0.15);
  --icon-orange-fg: #fb923c;
  --icon-amber-bg: rgba(245, 158, 11, 0.15);
  --icon-amber-fg: #fbbf24;
}

.app-container {
  min-height: 100vh;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: "Inter", "Noto Sans TC", system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Header */
header {
  background-color: var(--surface); /* Explicit background-color */
  background: var(--surface);
  padding: 18px 0;
  border-bottom: 1px solid var(--border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03); /* Subtle shadow */
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  opacity: 1; /* Explicit opacity */
  position: relative;
  z-index: 50;
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
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.01em;
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
  font-weight: 500;
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
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-hover);
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
  display: block; /* Ensure block-level for background */
  width: 100%;
  background-color: var(--surface); /* Explicit background-color */
  background: var(--surface); /* Fallback */
  border-bottom: 1px solid var(--border);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000; /* High z-index to stay on top */
  opacity: 1; /* Explicit opacity */
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); /* Stronger shadow for stacking context */
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  gap: 4px;
  padding: 0 16px;
  overflow-x: auto; /* Allow horizontal scroll if needed */
  scrollbar-width: none; /* Hide scrollbar for Firefox */
}

.nav-container::-webkit-scrollbar {
  display: none; /* Hide scrollbar for Chrome/Safari */
}

nav a {
  padding: 14px 18px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
  white-space: nowrap; /* Prevent text wrapping */
  flex-shrink: 0; /* Prevent items from shrinking */
}

nav a:hover {
  color: var(--primary);
  background: transparent;
}

nav a.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
  background: transparent;
}

/* Main */
main.main-content {
  min-height: calc(100vh - 140px);
  background: var(--bg-page);
  padding-bottom: 80px; /* Space for mobile nav */
}

@media (min-width: 768px) {
  main.main-content {
    padding-bottom: 0;
  }
}

/* Mobile Navigation (Bottom) */
.mobile-nav {
  position: fixed;
  top: auto; /* Prevent full screen overlay */
  bottom: 0;
  left: 0;
  right: 0;
  height: auto;
  background: var(--surface);
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-around;
  padding: 8px 4px 20px 4px; /* Extra padding for iOS home bar */
  z-index: 1000;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
  min-width: 60px;
}

.mobile-nav-item i {
  font-size: 20px;
  margin-bottom: 2px;
}

.mobile-nav-item.active {
  color: var(--primary);
  background: var(--primary-soft);
}

.mobile-nav-item:active {
  transform: scale(0.95);
}

/* Responsive Overrides */
@media (max-width: 768px) {
  .header-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding: 12px 16px;
  }
  
  .header-text {
    text-align: center;
  }

  header h1 {
    font-size: 20px;
  }

  header p {
    display: none; /* Hide subtitle on mobile */
  }
  
  .user-section {
    justify-content: space-between;
    width: 100%;
  }
  
  .user-info {
    flex: 1;
    justify-content: flex-end;
  }
  
  .btn-logout.icon-only-mobile {
    padding: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
}

/* ============================================
   GLOBAL UTILITY CLASSES
   ============================================ */

/* Glass Effect */
:global(.glass) {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:global(.dark .glass) {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Card Hover Effect */
:global(.card-hover) {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

:global(.card-hover:hover) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

/* Animations */
:global(.animate-fade-up) {
  animation: fadeUp 0.6s ease-out forwards;
}

:global(.animate-fade-in) {
  animation: fadeIn 0.5s ease-out forwards;
}

:global(.animate-slide-in) {
  animation: slideIn 0.4s ease-out forwards;
}

:global(.animate-scale-in) {
  animation: scaleIn 0.3s ease-out forwards;
}

/* Animation Delays */
:global(.delay-100) { animation-delay: 100ms; }
:global(.delay-200) { animation-delay: 200ms; }
:global(.delay-300) { animation-delay: 300ms; }
:global(.delay-400) { animation-delay: 400ms; }

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Custom Scrollbar */
:global(::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:global(::-webkit-scrollbar-track) {
  background: var(--surface-muted);
  border-radius: 4px;
}

:global(::-webkit-scrollbar-thumb) {
  background: var(--text-secondary);
  border-radius: 4px;
  opacity: 0.3;
}

:global(::-webkit-scrollbar-thumb:hover) {
  opacity: 0.5;
}

/* Flashcard 3D Flip Utilities */
:global(.perspective-1000) {
  perspective: 1000px;
}

:global(.transform-style-3d) {
  transform-style: preserve-3d;
}

:global(.backface-hidden) {
  backface-visibility: hidden;
}

:global(.rotate-y-180) {
  transform: rotateY(180deg);
}

/* Status Colors Utilities */
:global(.text-success) { color: var(--success); }
:global(.text-warning) { color: var(--warning); }
:global(.text-destructive) { color: var(--destructive); }
:global(.bg-success-soft) { background: var(--success-soft); }
:global(.bg-warning-soft) { background: var(--warning-soft); }
:global(.bg-destructive-soft) { background: var(--destructive-soft); }

/* ============================================
   RESPONSIVE UTILITIES
   ============================================ */

/* Container System */
:global(.container) {
  width: 100%;
  padding-left: 16px;
  padding-right: 16px;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 640px) {
  :global(.container) {
    padding-left: 24px;
    padding-right: 24px;
    max-width: 640px;
  }
}

@media (min-width: 768px) {
  :global(.container) {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  :global(.container) {
    max-width: 1024px;
  }
}

@media (min-width: 1280px) {
  :global(.container) {
    max-width: 1280px;
  }
}

/* Touch Targets */
:global(.touch-target) {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Visibility Utilities */
:global(.hidden-mobile) {
  display: none !important;
}

@media (min-width: 1280px) {
  :global(.hidden-mobile) {
    display: initial !important; /* Reset to default */
  }
  :global(.hidden-desktop) {
    display: none !important;
  }
}

/* Layout Utilities */
:global(.mobile-stack) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 640px) {
  :global(.mobile-stack) {
    flex-direction: row;
    align-items: center;
  }
}

/* ============================================
   CHECK-CIRCLE PATTERN
   ============================================ */
:global(.check-circle) {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--success-soft);
  color: var(--success);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 12px;
}

:global(.dark .check-circle) {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

/* ============================================
   ICON-BOX COMPONENT
   ============================================ */
:global(.icon-box) {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

:global(.icon-box.blue) {
  background: var(--icon-blue-bg);
  color: var(--icon-blue-fg);
}

:global(.icon-box.green) {
  background: var(--icon-green-bg);
  color: var(--icon-green-fg);
}

:global(.icon-box.purple) {
  background: var(--icon-purple-bg);
  color: var(--icon-purple-fg);
}

:global(.icon-box.orange) {
  background: var(--icon-orange-bg);
  color: var(--icon-orange-fg);
}

:global(.icon-box.amber) {
  background: var(--icon-amber-bg);
  color: var(--icon-amber-fg);
}

/* ============================================
   GLASS-CARD COMPONENT
   ============================================ */
:global(.glass-card) {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-elegant);
}

/* ============================================
   CARD-INTERACTIVE COMPONENT
   ============================================ */
:global(.card-interactive) {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-elegant);
  transition: all 0.3s ease;
}

:global(.card-interactive:hover) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: var(--primary);
}

:global(.card-interactive:hover .icon-box) {
  transform: scale(1.1);
}

/* ============================================
   BADGE-POPULAR COMPONENT
   ============================================ */
:global(.badge-popular) {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.25);
}

/* ============================================
   FLOATING ANIMATION
   ============================================ */
@keyframes floatBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

:global(.animate-float) {
  animation: floatBounce 3s ease-in-out infinite;
}

/* ============================================
   GLOBAL DARK MODE OVERRIDES
   ============================================ */

/* Cards and Surfaces */
:global(.dark) .analytics-card,
:global(.dark) .overview-card,
:global(.dark) .exam-card,
:global(.dark) .mode-card,
:global(.dark) .feature-card,
:global(.dark) .stat-card,
:global(.dark) .chart-card,
:global(.dark) .results-card,
:global(.dark) .wrong-card,
:global(.dark) .trend-card,
:global(.dark) .pricing-card,
:global(.dark) .exam-item,
:global(.dark) .flashcard-item,
:global(.dark) .question-item,
:global(.dark) .card {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

/* Form Inputs */
:global(.dark) input,
:global(.dark) select,
:global(.dark) textarea {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

:global(.dark) input::placeholder,
:global(.dark) textarea::placeholder {
  color: var(--text-secondary) !important;
}

/* Search filters and controls */
:global(.dark) .search-filter,
:global(.dark) .filter-section,
:global(.dark) .search-box,
:global(.dark) .filter-bar {
  background: var(--surface-muted) !important;
  border-color: var(--border) !important;
}

/* Table rows and list items */
:global(.dark) .trend-item,
:global(.dark) .results-table-row,
:global(.dark) .question-row,
:global(.dark) .search-item,
:global(.dark) .list-item,
:global(.dark) .hot-item {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

:global(.dark) .trend-item:hover,
:global(.dark) .results-table-row:hover,
:global(.dark) .question-row:hover,
:global(.dark) .hot-item:hover {
  background: var(--surface-muted) !important;
}

/* Table headers */
:global(.dark) .trend-list-header,
:global(.dark) .results-table-header,
:global(.dark) .table-header {
  background: var(--surface-muted) !important;
  color: var(--text-secondary) !important;
  border-color: var(--border) !important;
}

/* Progress bars */
:global(.dark) .progress-bar,
:global(.dark) .accuracy-bar-container,
:global(.dark) .score-bar-container {
  background: var(--surface-muted) !important;
}

/* Modal/Dialog backgrounds */
:global(.dark) .modal-content,
:global(.dark) .dialog-body,
:global(.dark) .mock-exam-dialog {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

/* Tabs */
:global(.dark) .tabs button,
:global(.dark) .results-tabs button {
  color: var(--text-secondary) !important;
  background: transparent !important;
}

:global(.dark) .tabs button.active,
:global(.dark) .results-tabs button.active {
  color: var(--primary) !important;
  background: var(--primary-soft) !important;
}

/* Badges and Tags */
:global(.dark) .badge,
:global(.dark) .tag,
:global(.dark) .status-tag {
  background: var(--surface-muted) !important;
  color: var(--text-primary) !important;
}

/* Empty states */
:global(.dark) .empty-chart,
:global(.dark) .empty-results,
:global(.dark) .empty-state {
  color: var(--text-secondary) !important;
}

/* Pagination */
:global(.dark) .pagination-controls,
:global(.dark) .pagination-buttons button {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

/* QuestionList specific - white rows issue */
:global(.dark) .question-list-item,
:global(.dark) .search-result-item {
  background: var(--surface) !important;
  border-color: var(--border) !important;
}

/* Landing page - pricing cards */
:global(.dark) .pricing-plan,
:global(.dark) .plan-card {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

:global(.dark) .pricing-plan ul li,
:global(.dark) .plan-features li {
  color: var(--text-secondary) !important;
}

/* Alert box */
:global(.dark) .alert {
  background: var(--surface-muted) !important;
  border-color: var(--border) !important;
}

/* Review header in flashcard */
:global(.dark) .review-header {
  background: var(--surface) !important;
  border-color: var(--border) !important;
}

/* AI Essay Analysis cards */
:global(.dark) .analysis-card,
:global(.dark) .essay-card,
:global(.dark) .chat-card {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}

/* Admin page - override white backgrounds */
:global(.dark) .admin-card,
:global(.dark) .admin-section,
:global(.dark) .data-table,
:global(.dark) .form-group {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}
</style>

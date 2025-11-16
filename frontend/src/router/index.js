import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: () => import('@/views/LandingView.vue')
    },
    {
      path: '/practice',
      name: 'Practice',
      component: () => import('@/views/PracticeView.vue')
    },
    {
      path: '/flashcard',
      name: 'Flashcard',
      component: () => import('@/views/FlashcardView.vue')
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('@/views/AnalyticsView.vue')
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/admin/exams/new',
      name: 'ExamCreate',
      component: () => import('@/views/ExamEditView.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/admin/exams/:id/edit',
      name: 'ExamEdit',
      component: () => import('@/views/ExamEditView.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/ai-chat',
      name: 'AIChat',
      component: () => import('@/views/AIChatView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/subscription',
      name: 'Subscription',
      component: () => import('@/views/SubscriptionView.vue')
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userRole = localStorage.getItem('user_role')

  // 需要認證但未登入
  if (to.meta.requiresAuth && !token) {
    // 儲存原本要前往的路徑
    sessionStorage.setItem('intended_path', to.fullPath)
    // 觸發登入彈窗
    window.dispatchEvent(new Event('show-login'))
    // 停留在當前頁面
    next(false)
  }
  // 需要管理員權限
  else if (to.meta.requiresAdmin) {
    if (!token) {
      // 未登入，觸發登入彈窗
      sessionStorage.setItem('intended_path', to.fullPath)
      window.dispatchEvent(new Event('show-login'))
      next('/practice')
    } else if (userRole === 'admin') {
      // 已登入且是管理員
      next()
    } else {
      // 已登入但不是管理員
      alert('需要管理員權限才能訪問此頁面')
      next('/practice')
    }
  }
  else {
    next()
  }
})

export default router

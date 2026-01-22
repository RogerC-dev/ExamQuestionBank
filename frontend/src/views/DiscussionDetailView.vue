<template>
  <div class="discussion-detail-view">
    <!-- Loading State -->
    <div v-if="store.loading && !discussion" class="loading-state">
      <div class="loading-spinner"></div>
      <p>載入中...</p>
    </div>
    
    <!-- Error State -->
    <div v-else-if="store.error && !discussion" class="error-state">
      <div class="error-icon">⚠️</div>
      <h2>載入失敗</h2>
      <p>{{ store.error }}</p>
      <button class="btn-retry" @click="loadDiscussion">重試</button>
    </div>
    
    <!-- Content -->
    <template v-else-if="discussion">
      <!-- Back Button & Credits -->
      <div class="view-header">
        <button class="btn-back" @click="goBack">
          ← 返回列表
        </button>
        <CreditBalance
          v-if="isLoggedIn"
          :credits="store.creditBalance"
          :can-claim="store.canClaimDaily"
          :loading="claimingCredits"
          @claim="handleClaimCredits"
        />
      </div>
      
      <!-- Discussion Card -->
      <div class="discussion-detail-card">
        <h1 class="discussion-title">{{ discussion.title }}</h1>
        
        <div class="discussion-meta">
          <span class="author">
            <i class="bi bi-person-fill author-icon"></i>
            {{ authorName }}
          </span>
          <span class="time">{{ timeAgo }}</span>
          <span class="views">
            <i class="bi bi-eye-fill"></i> {{ discussion.view_count || 0 }} 瀏覽
          </span>
        </div>
        
        <div class="discussion-body" v-html="formattedBody"></div>
      </div>
      
      <!-- Answers Section -->
      <div class="answers-section">
        <AnswerList
          :answers="answers"
          @unlock="handleUnlock"
          @vote="handleVote"
        />
      </div>
      
      <!-- Answer Form -->
      <div v-if="isLoggedIn" class="answer-form-section">
        <AnswerForm
          :loading="submittingAnswer"
          @submit="handleSubmitAnswer"
        />
      </div>
      
      <div v-else class="login-prompt">
        <p>請登入以提交回答</p>
      </div>
      
      <!-- Error Toast -->
      <div v-if="store.error" class="error-toast">
        <span>{{ store.error }}</span>
        <button @click="store.clearError">✕</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { supabase } from '@/lib/supabase'
import { useDiscussionStore } from '@/stores/discussionStore'
import CreditBalance from '@/components/discussion/CreditBalance.vue'
import AnswerList from '@/components/discussion/AnswerList.vue'
import AnswerForm from '@/components/discussion/AnswerForm.vue'

const route = useRoute()
const router = useRouter()
const store = useDiscussionStore()

const isLoggedIn = ref(false)
const claimingCredits = ref(false)
const submittingAnswer = ref(false)

// Computed properties
const discussion = computed(() => store.currentDiscussion?.discussion)
const answers = computed(() => store.currentDiscussion?.answers || [])

const authorName = computed(() => {
  const email = discussion.value?.user_email
  if (!email) return '匿名用戶'
  return email.split('@')[0]
})

const timeAgo = computed(() => {
  if (!discussion.value?.created_at) return ''
  const date = new Date(discussion.value.created_at)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return '剛剛'
  if (diffMins < 60) return `${diffMins} 分鐘前`
  if (diffHours < 24) return `${diffHours} 小時前`
  if (diffDays < 7) return `${diffDays} 天前`
  return date.toLocaleDateString('zh-TW')
})

const formattedBody = computed(() => {
  if (!discussion.value?.body) return ''
  return discussion.value.body
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
})

// Check auth
async function checkAuth() {
  const { data: { session } } = await supabase.auth.getSession()
  isLoggedIn.value = !!session
}

// Load discussion
async function loadDiscussion() {
  const id = route.params.id
  if (id) {
    await store.fetchDiscussion(id)
  }
}

// Initialize
onMounted(async () => {
  await checkAuth()
  await loadDiscussion()
  if (isLoggedIn.value) {
    await store.fetchCredits()
  }
})

// Navigation
function goBack() {
  router.push({ name: 'Discussions' })
}

// Handle actions
async function handleClaimCredits() {
  claimingCredits.value = true
  try {
    await store.claimDailyCredits()
  } catch (err) {
    // Error handled by store
  } finally {
    claimingCredits.value = false
  }
}

async function handleUnlock(answerId) {
  try {
    await store.unlockAnswer(answerId)
  } catch (err) {
    // Error handled by store
  }
}

async function handleVote(data) {
  try {
    await store.castVote(data.answerId, data.value)
  } catch (err) {
    // Error handled by store
  }
}

async function handleSubmitAnswer(body) {
  submittingAnswer.value = true
  try {
    await store.submitAnswer(discussion.value.id, body)
  } catch (err) {
    // Error handled by store
  } finally {
    submittingAnswer.value = false
  }
}
</script>

<style scoped>
.discussion-detail-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color, #e5e7eb);
  border-top-color: var(--primary-color, #4f46e5);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h2 {
  color: var(--text-primary, #111827);
  margin: 0 0 0.5rem 0;
}

.dark .error-state h2 {
  color: var(--text-primary-dark, #f9fafb);
}

.error-state p {
  color: var(--text-secondary, #6b7280);
  margin: 0 0 1.5rem 0;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color, #4f46e5);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-secondary, #f3f4f6);
  color: var(--text-primary, #111827);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .btn-back {
  background: var(--bg-tertiary, #374151);
  color: var(--text-primary-dark, #f9fafb);
  border-color: var(--border-color-dark, #4b5563);
}

.btn-back:hover {
  background: var(--bg-tertiary, #e5e7eb);
}

.dark .btn-back:hover {
  background: var(--bg-secondary, #4b5563);
}

.discussion-detail-card {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.dark .discussion-detail-card {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border-color-dark, #374151);
}

.discussion-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.dark .discussion-title {
  color: var(--text-primary-dark, #f9fafb);
}

.discussion-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-tertiary, #9ca3af);
  flex-wrap: wrap;
}

.author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--text-secondary, #6b7280);
}

.discussion-body {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--text-primary, #111827);
}

.dark .discussion-body {
  color: var(--text-primary-dark, #f9fafb);
}

.answers-section {
  margin-bottom: 2rem;
}

.answer-form-section {
  margin-top: 1.5rem;
}

.login-prompt {
  text-align: center;
  padding: 2rem;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 12px;
  color: var(--text-secondary, #6b7280);
}

.dark .login-prompt {
  background: var(--bg-tertiary, #374151);
}

.error-toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #ef4444;
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.error-toast button {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

@media (max-width: 640px) {
  .discussion-detail-view {
    padding: 1rem;
  }
  
  .view-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .discussion-title {
    font-size: 1.25rem;
  }
  
  .discussion-detail-card {
    padding: 1rem;
  }
}
</style>

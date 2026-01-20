<template>
  <div class="discussion-view">
    <div class="view-header">
      <h1>討論區</h1>
      <p class="view-description">提問、解答、互相學習</p>
    </div>
    
    <!-- Credit Balance -->
    <CreditBalance
      v-if="isLoggedIn"
      :credits="store.creditBalance"
      :can-claim="store.canClaimDaily"
      :reputation="store.reputation"
      :loading="claimingCredits"
      @claim="handleClaimCredits"
    />
    
    <!-- Action Bar -->
    <div class="action-bar">
      <button 
        v-if="isLoggedIn"
        class="btn-new-discussion"
        @click="showForm = !showForm"
      >
        <span v-if="showForm">✕ 取消</span>
        <span v-else>+ 發起討論</span>
      </button>
    </div>
    
    <!-- Create Discussion Form -->
    <DiscussionForm
      v-if="showForm && isLoggedIn"
      :loading="store.loading"
      @submit="handleCreateDiscussion"
      @cancel="showForm = false"
    />
    
    <!-- Error Message -->
    <div v-if="store.error" class="error-message">
      <span>{{ store.error }}</span>
      <button @click="store.clearError">✕</button>
    </div>
    
    <!-- Discussion List -->
    <DiscussionList
      :discussions="store.discussions"
      :loading="store.loading"
      :has-more="store.pagination.hasMore"
      @select="handleSelectDiscussion"
      @load-more="handleLoadMore"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/lib/supabase'
import { useDiscussionStore } from '@/stores/discussionStore'
import CreditBalance from '@/components/discussion/CreditBalance.vue'
import DiscussionList from '@/components/discussion/DiscussionList.vue'
import DiscussionForm from '@/components/discussion/DiscussionForm.vue'

const router = useRouter()
const store = useDiscussionStore()

const showForm = ref(false)
const claimingCredits = ref(false)
const isLoggedIn = ref(false)

// Check auth status
async function checkAuth() {
  const { data: { session } } = await supabase.auth.getSession()
  isLoggedIn.value = !!session
}

// Load discussions and credits on mount
onMounted(async () => {
  await checkAuth()
  await store.fetchDiscussions(true)
  if (isLoggedIn.value) {
    await store.fetchCredits()
  }
})

// Handle creating a new discussion
async function handleCreateDiscussion(data) {
  try {
    const discussion = await store.createDiscussion(data.title, data.body)
    showForm.value = false
    // Navigate to the new discussion
    router.push({ name: 'DiscussionDetail', params: { id: discussion.id } })
  } catch (err) {
    // Error is already set in store
  }
}

// Handle selecting a discussion
function handleSelectDiscussion(discussion) {
  router.push({ name: 'DiscussionDetail', params: { id: discussion.id } })
}

// Handle loading more discussions
function handleLoadMore() {
  store.fetchDiscussions()
}

// Handle claiming daily credits
async function handleClaimCredits() {
  claimingCredits.value = true
  try {
    await store.claimDailyCredits()
  } catch (err) {
    // Error is already set in store
  } finally {
    claimingCredits.value = false
  }
}
</script>

<style scoped>
.discussion-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.view-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.view-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0 0 0.5rem 0;
}

.dark .view-header h1 {
  color: var(--text-primary-dark, #f9fafb);
}

.view-description {
  color: var(--text-secondary, #6b7280);
  margin: 0;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  margin: 1.5rem 0;
}

.btn-new-discussion {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-new-discussion:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.error-message {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  border-radius: 8px;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-message button {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
}

@media (max-width: 640px) {
  .discussion-view {
    padding: 1rem;
  }
  
  .view-header h1 {
    font-size: 1.5rem;
  }
  
  .action-bar {
    justify-content: stretch;
  }
  
  .btn-new-discussion {
    width: 100%;
  }
}
</style>

<template>
  <div class="answer-card-mvp" :class="{ locked: answer.is_locked }">
    <div class="answer-header">
      <div class="answer-meta">
        <span class="author">
          <i class="bi bi-person-fill author-icon"></i>
          {{ authorName }}
        </span>
        <span class="time">{{ timeAgo }}</span>
      </div>
      <div class="answer-stats">
        <span v-if="!answer.is_locked" class="unlock-count">
          <i class="bi bi-unlock-fill"></i> {{ answer.unlock_count || 0 }} 人已解鎖
        </span>
      </div>
    </div>
    
    <div class="answer-content">
      <template v-if="answer.is_locked">
        <div class="locked-overlay">
          <div class="lock-icon"><i class="bi bi-lock-fill"></i></div>
          <p class="lock-message">此回答已鎖定</p>
          <button 
            class="unlock-btn"
            :disabled="unlocking"
            @click="handleUnlock"
          >
            <span v-if="unlocking" class="loading-spinner"></span>
            <span v-else>解鎖 (20 點數)</span>
          </button>
        </div>
      </template>
      <template v-else>
        <div class="answer-body" v-html="formattedBody"></div>
      </template>
    </div>
    
    <div class="answer-footer">
      <VoteButtons
        :vote-count="answer.vote_count || 0"
        :user-vote="answer.user_vote"
        :disabled="answer.is_locked || voting"
        @vote="handleVote"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import VoteButtons from './VoteButtons.vue'

const props = defineProps({
  answer: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['unlock', 'vote'])

const unlocking = ref(false)
const voting = ref(false)

const authorName = computed(() => {
  // Priority: display_name → email prefix → anonymous
  return props.answer.display_name 
    || (props.answer.user_email?.split('@')[0]) 
    || '匿名用戶'
})

const timeAgo = computed(() => {
  const date = new Date(props.answer.created_at)
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
  if (!props.answer.body) return ''
  // Basic formatting: convert newlines to <br>
  return props.answer.body
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
})

async function handleUnlock() {
  unlocking.value = true
  try {
    await emit('unlock', props.answer.id)
  } finally {
    unlocking.value = false
  }
}

async function handleVote(value) {
  voting.value = true
  try {
    await emit('vote', { answerId: props.answer.id, value })
  } finally {
    voting.value = false
  }
}
</script>

<style scoped>
.answer-card-mvp {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.dark .answer-card-mvp {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border-color-dark, #374151);
}

.answer-card-mvp.locked {
  background: var(--bg-secondary, #f9fafb);
}

.dark .answer-card-mvp.locked {
  background: var(--bg-tertiary, #374151);
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.answer-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--text-tertiary, #9ca3af);
}

.author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--text-secondary, #6b7280);
}

.author-icon {
  font-size: 0.75rem;
}

.answer-stats {
  font-size: 0.75rem;
  color: var(--text-tertiary, #9ca3af);
}

.answer-content {
  margin-bottom: 1rem;
}

.locked-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.05), rgba(139, 92, 246, 0.05));
  border-radius: 8px;
  border: 1px dashed var(--border-color, #d1d5db);
}

.dark .locked-overlay {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(139, 92, 246, 0.1));
  border-color: var(--border-color-dark, #4b5563);
}

.lock-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.lock-message {
  color: var(--text-secondary, #6b7280);
  margin: 0 0 1rem 0;
}

.unlock-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
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

.unlock-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.unlock-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.answer-body {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-primary, #111827);
}

.dark .answer-body {
  color: var(--text-primary-dark, #f9fafb);
}

.answer-footer {
  display: flex;
  justify-content: flex-start;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

.dark .answer-footer {
  border-color: var(--border-color-dark, #374151);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .answer-card-mvp {
    padding: 1rem;
  }
  
  .locked-overlay {
    padding: 1.5rem 1rem;
  }
}
</style>

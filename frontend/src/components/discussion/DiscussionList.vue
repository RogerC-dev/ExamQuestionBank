<template>
  <div class="discussion-list-mvp">
    <div v-if="loading && discussions.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <p>載入中...</p>
    </div>
    
    <div v-else-if="discussions.length === 0" class="empty-state">
      <div class="empty-icon"><i class="bi bi-chat-left-text"></i></div>
      <h3>還沒有討論</h3>
      <p>成為第一個發起討論的人吧！</p>
    </div>
    
    <template v-else>
      <DiscussionCard
        v-for="discussion in discussions"
        :key="discussion.id"
        :discussion="discussion"
        @click="handleCardClick"
      />
      
      <div v-if="hasMore" class="load-more">
        <button 
          class="load-more-btn"
          :disabled="loading"
          @click="loadMore"
        >
          <span v-if="loading" class="loading-spinner small"></span>
          <span v-else>載入更多</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import DiscussionCard from './DiscussionCard.vue'
// No action needed for DiscussionList.vue or AnswerList.vue as user handled them.
const props = defineProps({
  discussions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasMore: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'load-more'])

function handleCardClick(discussion) {
  emit('select', discussion)
}

function loadMore() {
  emit('load-more')
}
</script>

<style scoped>
.discussion-list-mvp {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary, #6b7280);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color, #e5e7eb);
  border-top-color: var(--primary-color, #4f46e5);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

.loading-spinner.small {
  width: 18px;
  height: 18px;
  border-width: 2px;
  margin-bottom: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: var(--text-primary, #111827);
  margin: 0 0 0.5rem 0;
}

.dark .empty-state h3 {
  color: var(--text-primary-dark, #f9fafb);
}

.empty-state p {
  margin: 0;
}

.load-more {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.load-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 120px;
  padding: 0.75rem 1.5rem;
  background: var(--bg-secondary, #f3f4f6);
  color: var(--text-primary, #111827);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .load-more-btn {
  background: var(--bg-tertiary, #374151);
  color: var(--text-primary-dark, #f9fafb);
  border-color: var(--border-color-dark, #4b5563);
}

.load-more-btn:hover:not(:disabled) {
  background: var(--bg-tertiary, #e5e7eb);
}

.dark .load-more-btn:hover:not(:disabled) {
  background: var(--bg-secondary, #4b5563);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

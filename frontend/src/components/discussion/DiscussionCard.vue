<template>
  <div class="discussion-card-mvp" @click="handleClick">
    <div class="card-content">
      <h3 class="card-title">{{ discussion.title }}</h3>
      <p class="card-preview">{{ bodyPreview }}</p>
      
      <div class="card-meta">
        <span class="author">
          <i class="bi bi-person-fill author-icon"></i>
          {{ authorName }}
        </span>
        <span class="time">{{ timeAgo }}</span>
      </div>
      
      <div class="card-stats">
        <span class="stat">
          <i class="bi bi-chat-dots stat-icon"></i>
          {{ discussion.answer_count || 0 }} 回答
        </span>
        <span class="stat">
          <i class="bi bi-eye-fill stat-icon"></i>
          {{ discussion.view_count || 0 }} 瀏覽
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  discussion: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const bodyPreview = computed(() => {
  const body = props.discussion.body || ''
  return body.length > 100 ? body.slice(0, 100) + '...' : body
})

const authorName = computed(() => {
  // Priority: display_name → email prefix → anonymous
  return props.discussion.display_name 
    || (props.discussion.user_email?.split('@')[0]) 
    || '匿名用戶'
})

const timeAgo = computed(() => {
  const date = new Date(props.discussion.created_at)
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

function handleClick() {
  emit('click', props.discussion)
}
</script>

<style scoped>
.discussion-card-mvp {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .discussion-card-mvp {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border-color-dark, #374151);
}

.discussion-card-mvp:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color, #4f46e5);
}

.dark .discussion-card-mvp:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.dark .card-title {
  color: var(--text-primary-dark, #f9fafb);
}

.card-preview {
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: var(--text-tertiary, #9ca3af);
}

.author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.author-icon {
  font-size: 0.75rem;
}

.card-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
}

.stat-icon {
  font-size: 0.875rem;
}

@media (max-width: 480px) {
  .discussion-card-mvp {
    padding: 1rem;
  }
  
  .card-title {
    font-size: 1rem;
  }
  
  .card-stats {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
}
</style>

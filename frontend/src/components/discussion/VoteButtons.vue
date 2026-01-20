<template>
  <div class="vote-buttons-mvp">
    <button 
      class="vote-btn upvote"
      :class="{ active: userVote === 1 }"
      :disabled="disabled"
      @click="handleVote(1)"
      title="讚"
    >
      <i class="bi bi-caret-up-fill"></i>
    </button>
    <span class="vote-count" :class="{ positive: voteCount > 0, negative: voteCount < 0 }">
      {{ voteCount }}
    </span>
    <button 
      class="vote-btn downvote"
      :class="{ active: userVote === -1 }"
      :disabled="disabled"
      @click="handleVote(-1)"
      title="倒讚"
    >
      <i class="bi bi-caret-down-fill"></i>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  voteCount: {
    type: Number,
    default: 0
  },
  userVote: {
    type: Number,
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['vote'])

function handleVote(value) {
  if (props.disabled) return
  emit('vote', value)
}
</script>

<style scoped>
.vote-buttons-mvp {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.vote-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--bg-secondary, #f3f4f6);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .vote-btn {
  background: var(--bg-tertiary, #374151);
  border-color: var(--border-color-dark, #4b5563);
}

.vote-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.vote-btn.upvote:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.1);
  border-color: #10b981;
}

.vote-btn.downvote:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.vote-btn.active.upvote {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.vote-btn.active.downvote {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.vote-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vote-count {
  min-width: 30px;
  text-align: center;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-primary, #111827);
}

.dark .vote-count {
  color: var(--text-primary-dark, #f9fafb);
}

.vote-count.positive {
  color: #10b981;
}

.vote-count.negative {
  color: #ef4444;
}
</style>

<template>
  <div class="review-header" data-testid="review-header">
    <span class="progress-text" data-testid="progress-text">{{ currentIndex + 1 }} / {{ totalCards }}</span>
    <div class="progress-bar" data-testid="progress-bar">
      <div 
        class="progress-fill" 
        data-testid="progress-fill"
        :style="{ width: progressWidth + '%' }"
      ></div>
    </div>
    <button class="btn-exit" data-testid="exit-button" @click="$emit('exit')">
      <i class="bi bi-x-lg me-2"></i>結束
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  currentIndex: number
  totalCards: number
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'exit'): void
}>()

const progressWidth = computed(() => {
  if (props.totalCards === 0) return 0
  return ((props.currentIndex + 1) / props.totalCards) * 100
})
</script>

<style scoped>
/* Review Header Container */
.review-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
  padding: 16px;
  background: var(--surface, #ffffff);
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border, #e2e8f0);
  flex-wrap: wrap;
}

/* Progress Text */
.progress-text {
  white-space: nowrap;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary, #1e293b);
  min-width: 60px;
}

/* Progress Bar */
.progress-bar {
  flex: 1;
  min-width: 200px;
  height: 8px;
  background: var(--border, #e2e8f0);
  border-radius: 4px;
  overflow: hidden;
}

/* Animated Progress Fill */
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary, #3b82f6), var(--primary-hover, #2563eb));
  border-radius: 4px;
  transition: width 0.3s ease-out;
}

/* Exit Button */
.btn-exit {
  padding: 8px 16px;
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  cursor: pointer;
  color: var(--text-primary, #1e293b);
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
}

.btn-exit:hover {
  background: #f0f4f8;
  border-color: var(--primary, #3b82f6);
  color: var(--primary, #3b82f6);
}

.btn-exit:active {
  transform: scale(0.98);
}

/* Responsive Design - Tablet */
@media (max-width: 1024px) {
  .review-header {
    padding: 14px;
    gap: 14px;
  }

  .progress-text {
    font-size: 13px;
  }

  .btn-exit {
    padding: 7px 14px;
    font-size: 13px;
  }
}

/* Responsive Design - Mobile */
@media (max-width: 768px) {
  .review-header {
    padding: 12px;
    gap: 10px;
    font-size: 14px;
  }

  .progress-text {
    font-size: 13px;
    min-width: auto;
  }

  .progress-bar {
    min-width: 100%;
    order: 3;
  }

  .btn-exit {
    padding: 6px 12px;
    font-size: 13px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .review-header {
    padding: 10px;
    gap: 8px;
  }

  .progress-text {
    font-size: 12px;
  }

  .btn-exit {
    padding: 5px 10px;
    font-size: 12px;
  }
}
</style>

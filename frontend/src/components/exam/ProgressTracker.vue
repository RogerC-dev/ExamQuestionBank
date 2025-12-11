<template>
  <div 
    class="progress-tracker"
    role="region"
    aria-label="Exam progress"
  >
    <div class="progress-info">
      <span 
        class="progress-text"
        id="progress-text"
        aria-live="polite"
      >
        進度：{{ answeredCount }} / {{ totalQuestions }} 題
      </span>
      <span 
        class="progress-percentage"
        aria-hidden="true"
      >
        {{ Math.round(progressPercentage) }}%
      </span>
    </div>
    <div 
      class="progress-bar"
      role="progressbar"
      :aria-valuenow="Math.round(progressPercentage)"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Exam progress: ${answeredCount} of ${totalQuestions} questions answered, ${Math.round(progressPercentage)}% complete`"
      aria-describedby="progress-text"
    >
      <div 
        class="progress-fill" 
        :style="{ width: `${progressPercentage}%` }"
        aria-hidden="true"
      ></div>
    </div>
    <span class="sr-only" aria-live="polite">
      {{ answeredCount }} of {{ totalQuestions }} questions answered
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * ProgressTracker Component
 * Visual indicator showing completion status of questions
 */

const props = defineProps({
  answeredQuestions: {
    type: Set,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  }
})

const answeredCount = computed(() => props.answeredQuestions.size)

const progressPercentage = computed(() => {
  if (props.totalQuestions === 0) return 0
  return (answeredCount.value / props.totalQuestions) * 100
})
</script>

<style scoped>
.progress-tracker {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  color: #374151;
  font-weight: 500;
}

.progress-percentage {
  color: #2563eb;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Focus styles for accessibility */
.progress-tracker:focus-within {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .progress-bar {
    border: 2px solid #374151;
  }
  
  .progress-fill {
    background: #2563eb;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .progress-fill {
    transition: none;
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .progress-tracker {
    padding: 12px;
  }
  
  .progress-text {
    font-size: 14px;
  }
}
</style>
<template>
  <header 
    class="exam-header"
    role="banner"
    aria-label="Exam information header"
  >
    <div class="exam-info">
      <h1 class="exam-title" id="exam-title">{{ exam?.name || 'Loading exam...' }}</h1>
      <p 
        class="exam-description" 
        id="exam-description"
        :aria-label="exam?.description ? 'Exam description' : 'No description available'"
      >
        {{ exam?.description || 'No description provided' }}
      </p>
    </div>
    <div class="exam-meta" role="group" aria-label="Exam metadata">
      <span 
        class="question-count" 
        role="status"
        :aria-label="`Total questions: ${exam?.questions?.length || 0}`"
      >
        Questions: {{ exam?.questions?.length || 0 }}
      </span>
      <span 
        v-if="exam?.timeLimit" 
        class="time-limit"
        role="status"
        :aria-label="`Time limit: ${exam.timeLimit} minutes`"
      >
        Time Limit: {{ exam.timeLimit }} minutes
      </span>
      <div class="header-actions" role="group" aria-label="Exam actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </header>
</template>

<script setup>
/**
 * ExamHeader Component
 * Displays exam metadata including title, description, question count, and time limit
 */

defineProps({
  exam: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.exam-header {
  background: white;
  padding: 24px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-title {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.exam-description {
  color: #6b7280;
  margin: 8px 0 0 0;
}

.exam-meta span {
  display: block;
  color: #4b5563;
  margin-bottom: 4px;
}

.header-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

/* Tablet breakpoint */
@media (max-width: 768px) {
  .exam-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
  }
  
  .exam-title {
    font-size: 22px;
  }
  
  .exam-description {
    font-size: 14px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}

/* Mobile breakpoint */
@media (max-width: 480px) {
  .exam-header {
    padding: 16px;
    margin-bottom: 16px;
    border-radius: 8px;
  }
  
  .exam-title {
    font-size: 20px;
    line-height: 1.3;
  }
  
  .exam-description {
    font-size: 13px;
    line-height: 1.5;
  }
  
  .exam-meta span {
    font-size: 14px;
  }
  
  .header-actions {
    gap: 8px;
  }
}

/* Touch-friendly targets for mobile */
@media (max-width: 768px) and (pointer: coarse) {
  .header-actions button,
  .header-actions a {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 16px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .exam-header {
    border: 2px solid #1f2937;
  }
  
  .exam-title {
    color: #000;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .exam-header {
    transition: none;
  }
}

/* Focus styles */
.exam-header:focus-within {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
</style>
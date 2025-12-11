<template>
  <nav 
    class="question-navigator"
    role="navigation"
    aria-label="Question navigation"
  >
    <h3 class="navigator-title" id="navigator-title">題目導航</h3>
    <div 
      class="question-grid"
      role="group"
      aria-labelledby="navigator-title"
      aria-describedby="navigator-status"
    >
      <button
        v-for="(question, index) in questions"
        :key="question.id"
        class="question-button"
        :class="{
          'current': index === currentIndex,
          'answered': answeredQuestions.has(index)
        }"
        @click="$emit('navigate-to', index)"
        :aria-label="getButtonAriaLabel(index)"
        :aria-current="index === currentIndex ? 'step' : undefined"
        :aria-pressed="answeredQuestions.has(index)"
        type="button"
      >
        {{ index + 1 }}
      </button>
    </div>
    <p id="navigator-status" class="sr-only">
      {{ answeredQuestions.size }} of {{ questions.length }} questions answered
    </p>
  </nav>
</template>

<script setup>
/**
 * QuestionNavigator Component
 * Provides visual overview and navigation for exam questions
 * Requirements: 2.2, 2.3, 2.4, 7.3 - Navigation with accessibility support
 */

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  currentIndex: {
    type: Number,
    required: true
  },
  answeredQuestions: {
    type: Set,
    required: true
  }
})

defineEmits(['navigate-to'])

const getButtonAriaLabel = (index) => {
  const questionNum = index + 1
  const isCurrent = index === props.currentIndex
  const isAnswered = props.answeredQuestions.has(index)
  
  let label = `Question ${questionNum}`
  if (isCurrent) label += ', current question'
  if (isAnswered) label += ', answered'
  else label += ', not answered'
  
  return label
}
</script>

<style scoped>
.question-navigator {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-bottom: 16px;
}

.navigator-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #374151;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 8px;
}

.question-button {
  width: 40px;
  height: 40px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.question-button:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.question-button.current {
  border-color: #2563eb;
  background: #2563eb;
  color: white;
}

.question-button.answered {
  border-color: #10b981;
  background: #d1fae5;
  color: #065f46;
}

.question-button.current.answered {
  background: #059669;
  border-color: #059669;
  color: white;
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
.question-button:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
  z-index: 1;
}

.question-button:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .question-button {
    border-width: 3px;
  }
  
  .question-button.current {
    border-color: #000;
    background: #000;
  }
  
  .question-button.answered {
    border-color: #065f46;
    background: #d1fae5;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .question-button {
    transition: none;
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .question-grid {
    grid-template-columns: repeat(auto-fill, minmax(44px, 1fr));
    gap: 6px;
  }
  
  .question-button {
    width: 44px;
    height: 44px;
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
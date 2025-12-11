<template>
  <div 
    class="results-breakdown"
    role="region"
    aria-label="Question-by-question analysis"
  >
    <div class="breakdown-header">
      <h3 class="breakdown-title" id="breakdown-title">Question-by-Question Analysis</h3>
      <div 
        class="breakdown-summary"
        role="group"
        aria-label="Results summary"
      >
        <span 
          class="summary-item correct"
          role="status"
          :aria-label="`${correctCount} questions answered correctly`"
        >
          <span class="summary-icon" aria-hidden="true">✓</span>
          {{ correctCount }} Correct
        </span>
        <span 
          class="summary-item incorrect"
          role="status"
          :aria-label="`${incorrectCount} questions answered incorrectly`"
        >
          <span class="summary-icon" aria-hidden="true">✗</span>
          {{ incorrectCount }} Incorrect
        </span>
        <span 
          class="summary-item unanswered" 
          v-if="unansweredCount > 0"
          role="status"
          :aria-label="`${unansweredCount} questions not answered`"
        >
          <span class="summary-icon" aria-hidden="true">—</span>
          {{ unansweredCount }} Unanswered
        </span>
      </div>
    </div>

    <div 
      class="questions-list"
      role="list"
      aria-labelledby="breakdown-title"
    >
      <article 
        v-for="(detail, index) in results.details" 
        :key="detail.questionId"
        class="question-item"
        :class="getQuestionClass(detail)"
        role="listitem"
        :aria-label="`Question ${index + 1}: ${detail.isCorrect ? 'Correct' : detail.userAnswer ? 'Incorrect' : 'Not answered'}`"
        tabindex="0"
      >
        <div class="question-header">
          <div class="question-number">
            <span class="number" aria-hidden="true">{{ index + 1 }}</span>
            <span 
              class="status-icon" 
              :class="getStatusClass(detail)"
              :aria-label="getStatusAriaLabel(detail)"
              role="img"
            >
              {{ getStatusIcon(detail) }}
            </span>
          </div>
          <div class="question-text">{{ detail.question }}</div>
        </div>

        <div class="answer-section" role="group" aria-label="Answer comparison">
          <div class="user-answer" v-if="detail.userAnswer">
            <span class="answer-label" :id="`user-answer-label-${detail.questionId}`">Your Answer:</span>
            <span 
              class="answer-text" 
              :class="{ 'incorrect': !detail.isCorrect }"
              :aria-labelledby="`user-answer-label-${detail.questionId}`"
            >
              {{ detail.userAnswer }}
            </span>
          </div>
          <div class="user-answer unanswered" v-else>
            <span class="answer-label" :id="`user-answer-label-${detail.questionId}`">Your Answer:</span>
            <span 
              class="answer-text"
              :aria-labelledby="`user-answer-label-${detail.questionId}`"
            >
              Not answered
            </span>
          </div>

          <div class="correct-answer" v-if="!detail.isCorrect">
            <span class="answer-label" :id="`correct-answer-label-${detail.questionId}`">Correct Answer:</span>
            <span 
              class="answer-text correct"
              :aria-labelledby="`correct-answer-label-${detail.questionId}`"
            >
              {{ detail.correctAnswer }}
            </span>
          </div>
        </div>

        <div class="question-explanation" v-if="!detail.isCorrect && showExplanations">
          <div class="explanation-header">
            <span class="explanation-icon">💡</span>
            <span class="explanation-label">Why this answer is correct:</span>
          </div>
          <div class="explanation-text">
            <!-- This would be populated from question data in a real implementation -->
            The correct answer is "{{ detail.correctAnswer }}" based on the question requirements.
          </div>
        </div>
      </article>
    </div>

    <div class="breakdown-footer" v-if="showActions">
      <button 
        class="action-button secondary"
        @click="$emit('toggle-explanations')"
      >
        {{ showExplanations ? 'Hide' : 'Show' }} Explanations
      </button>
      <button 
        class="action-button primary"
        @click="$emit('review-incorrect')"
        v-if="incorrectCount > 0"
      >
        Review Incorrect Questions
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultsBreakdown',
  props: {
    results: {
      type: Object,
      required: true,
      validator(value) {
        return value && 
               Array.isArray(value.details) &&
               typeof value.correctCount === 'number' &&
               typeof value.totalCount === 'number'
      }
    },
    showExplanations: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: true
    }
  },
  emits: ['toggle-explanations', 'review-incorrect'],
  computed: {
    correctCount() {
      return this.results.correctCount
    },
    incorrectCount() {
      return this.results.details.filter(detail => !detail.isCorrect && detail.userAnswer).length
    },
    unansweredCount() {
      return this.results.details.filter(detail => !detail.userAnswer).length
    }
  },
  methods: {
    getQuestionClass(detail) {
      if (!detail.userAnswer) return 'unanswered'
      return detail.isCorrect ? 'correct' : 'incorrect'
    },
    getStatusClass(detail) {
      if (!detail.userAnswer) return 'unanswered'
      return detail.isCorrect ? 'correct' : 'incorrect'
    },
    getStatusIcon(detail) {
      if (!detail.userAnswer) return '—'
      return detail.isCorrect ? '✓' : '✗'
    },
    getStatusAriaLabel(detail) {
      if (!detail.userAnswer) return 'Not answered'
      return detail.isCorrect ? 'Answered correctly' : 'Answered incorrectly'
    }
  }
}
</script>

<style scoped>
.results-breakdown {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.breakdown-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.breakdown-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.breakdown-summary {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.summary-item.correct {
  color: #10b981;
}

.summary-item.incorrect {
  color: #ef4444;
}

.summary-item.unanswered {
  color: #6b7280;
}

.summary-icon {
  font-weight: 700;
  font-size: 1rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.question-item.correct {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
}

.question-item.incorrect {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fef7f7 100%);
}

.question-item.unanswered {
  border-color: #d1d5db;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.question-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.question-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.number {
  background: #f3f4f6;
  color: #374151;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-icon {
  font-weight: 700;
  font-size: 1rem;
}

.status-icon.correct {
  color: #10b981;
}

.status-icon.incorrect {
  color: #ef4444;
}

.status-icon.unanswered {
  color: #6b7280;
}

.question-text {
  font-weight: 500;
  color: #1f2937;
  line-height: 1.5;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-answer,
.correct-answer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.answer-label {
  font-weight: 500;
  color: #6b7280;
  min-width: 100px;
}

.answer-text {
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.answer-text.correct {
  background: #ecfdf5;
  border-color: #10b981;
  color: #065f46;
}

.answer-text.incorrect {
  background: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.user-answer.unanswered .answer-text {
  background: #f3f4f6;
  color: #6b7280;
  font-style: italic;
}

.question-explanation {
  margin-top: 1rem;
  padding: 1rem;
  background: #fffbeb;
  border: 1px solid #fbbf24;
  border-radius: 6px;
}

.explanation-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.explanation-icon {
  font-size: 1rem;
}

.explanation-label {
  font-weight: 600;
  color: #92400e;
}

.explanation-text {
  color: #78350f;
  line-height: 1.5;
}

.breakdown-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-button.primary {
  background: #3b82f6;
  color: white;
}

.action-button.primary:hover {
  background: #2563eb;
}

.action-button.secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.action-button.secondary:hover {
  background: #e5e7eb;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .results-breakdown {
    padding: 1rem;
  }
  
  .breakdown-summary {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .question-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .question-number {
    align-self: flex-start;
  }
  
  .user-answer,
  .correct-answer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .answer-label {
    min-width: auto;
  }
  
  .breakdown-footer {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .question-item.correct {
    border-width: 2px;
    background: #f0fdf4;
  }
  
  .question-item.incorrect {
    border-width: 2px;
    background: #fef2f2;
  }
  
  .question-item.unanswered {
    border-width: 2px;
    background: #f9fafb;
  }
  
  .answer-text.correct {
    background: #dcfce7;
    border-width: 2px;
  }
  
  .answer-text.incorrect {
    background: #fecaca;
    border-width: 2px;
  }
}

/* Focus styles for accessibility */
.action-button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.question-item:focus-within {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.question-item:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
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

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .question-item,
  .action-button {
    transition: none;
  }
}
</style>
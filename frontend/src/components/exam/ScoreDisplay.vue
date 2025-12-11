<template>
  <div 
    class="score-display"
    role="region"
    aria-label="Exam score summary"
    tabindex="0"
  >
    <div class="score-header">
      <h2 class="score-title" id="score-title">Exam Results</h2>
    </div>
    
    <div 
      class="score-main"
      role="group"
      aria-labelledby="score-title"
    >
      <div 
        class="score-circle" 
        :class="scoreClass"
        role="img"
        :aria-label="`Score: ${results.percentage}%, ${getScoreDescription()}`"
      >
        <div class="score-percentage" aria-hidden="true">{{ results.percentage }}%</div>
        <div class="score-label" aria-hidden="true">Score</div>
      </div>
      
      <div class="score-details">
        <div 
          class="score-fraction"
          aria-hidden="true"
        >
          <span class="correct-count">{{ results.correctCount }}</span>
          <span class="separator">/</span>
          <span class="total-count">{{ results.totalCount }}</span>
        </div>
        <div 
          class="score-description"
          role="status"
          aria-live="polite"
        >
          {{ results.correctCount }} out of {{ results.totalCount }} questions correct
        </div>
      </div>
    </div>
    
    <div 
      class="score-metadata" 
      v-if="showMetadata"
      role="group"
      aria-label="Additional exam information"
    >
      <div 
        class="metadata-item" 
        v-if="results.duration > 0"
        role="status"
      >
        <span class="metadata-label" id="time-label">Time Taken:</span>
        <span class="metadata-value" aria-labelledby="time-label">{{ formatDuration(results.duration) }}</span>
      </div>
      <div 
        class="metadata-item" 
        v-if="examName"
        role="status"
      >
        <span class="metadata-label" id="exam-label">Exam:</span>
        <span class="metadata-value" aria-labelledby="exam-label">{{ examName }}</span>
      </div>
    </div>
    
    <span class="sr-only">
      Your score is {{ results.percentage }} percent. 
      You answered {{ results.correctCount }} out of {{ results.totalCount }} questions correctly.
      {{ getScoreDescription() }}
    </span>
  </div>
</template>

<script>
export default {
  name: 'ScoreDisplay',
  props: {
    results: {
      type: Object,
      required: true,
      validator(value) {
        return value && 
               typeof value.correctCount === 'number' &&
               typeof value.totalCount === 'number' &&
               typeof value.percentage === 'number'
      }
    },
    examName: {
      type: String,
      default: ''
    },
    showMetadata: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    scoreClass() {
      const percentage = this.results.percentage
      if (percentage >= 90) return 'excellent'
      if (percentage >= 80) return 'good'
      if (percentage >= 70) return 'average'
      if (percentage >= 60) return 'below-average'
      return 'poor'
    }
  },
  methods: {
    getScoreDescription() {
      const percentage = this.results.percentage
      if (percentage >= 90) return 'Excellent performance!'
      if (percentage >= 80) return 'Good performance!'
      if (percentage >= 70) return 'Average performance'
      if (percentage >= 60) return 'Below average performance'
      return 'Needs improvement'
    },
    formatDuration(seconds) {
      if (seconds <= 0) return '0:00'
      
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      
      if (minutes >= 60) {
        const hours = Math.floor(minutes / 60)
        const remainingMinutes = minutes % 60
        return `${hours}:${remainingMinutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
      }
      
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.score-display {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  margin: 0 auto;
}

.score-header {
  margin-bottom: 2rem;
}

.score-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.score-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 4px solid;
  position: relative;
}

.score-circle.excellent {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
}

.score-circle.good {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #1e40af;
}

.score-circle.average {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  color: #92400e;
}

.score-circle.below-average {
  border-color: #f97316;
  background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
  color: #9a3412;
}

.score-circle.poor {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
  color: #991b1b;
}

.score-percentage {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.25rem;
  opacity: 0.8;
}

.score-details {
  text-align: left;
}

.score-fraction {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.correct-count {
  color: #10b981;
}

.separator {
  color: #6b7280;
  margin: 0 0.25rem;
}

.total-count {
  color: #6b7280;
}

.score-description {
  font-size: 1rem;
  color: #6b7280;
  font-weight: 500;
}

.score-metadata {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.metadata-label {
  font-weight: 500;
  color: #6b7280;
}

.metadata-value {
  font-weight: 600;
  color: #1f2937;
}

/* Tablet breakpoint */
@media (max-width: 768px) {
  .score-display {
    padding: 1.75rem;
    max-width: 100%;
  }
  
  .score-circle {
    width: 110px;
    height: 110px;
  }
  
  .score-percentage {
    font-size: 1.75rem;
  }
  
  .score-fraction {
    font-size: 2rem;
  }
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .score-display {
    padding: 1.5rem;
  }
  
  .score-main {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .score-details {
    text-align: center;
  }
  
  .score-metadata {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metadata-item {
    justify-content: center;
  }
}

/* Small mobile breakpoint */
@media (max-width: 480px) {
  .score-display {
    padding: 1.25rem;
    border-radius: 10px;
  }
  
  .score-header {
    margin-bottom: 1.5rem;
  }
  
  .score-title {
    font-size: 1.25rem;
  }
  
  .score-circle {
    width: 100px;
    height: 100px;
  }
  
  .score-percentage {
    font-size: 1.5rem;
  }
  
  .score-label {
    font-size: 0.75rem;
  }
  
  .score-fraction {
    font-size: 1.75rem;
  }
  
  .score-description {
    font-size: 0.875rem;
  }
  
  .metadata-label,
  .metadata-value {
    font-size: 0.875rem;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .score-circle {
    border-width: 3px;
  }
  
  .score-circle.excellent {
    background: #f0fdf4;
    border-color: #16a34a;
  }
  
  .score-circle.good {
    background: #f0f9ff;
    border-color: #2563eb;
  }
  
  .score-circle.average {
    background: #fffbeb;
    border-color: #d97706;
  }
  
  .score-circle.below-average {
    background: #fff7ed;
    border-color: #ea580c;
  }
  
  .score-circle.poor {
    background: #fef2f2;
    border-color: #dc2626;
  }
}

/* Focus styles for accessibility */
.score-display:focus-within {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.score-display:focus {
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
  .score-circle,
  .score-display {
    transition: none;
  }
}
</style>
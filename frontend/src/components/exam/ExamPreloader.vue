<template>
  <div 
    class="exam-preloader"
    role="region"
    aria-label="Exam loading status"
  >
    <div 
      v-if="isLoading" 
      class="loading-state"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div 
        class="loading-spinner"
        role="img"
        aria-label="Loading indicator"
      ></div>
      <p class="loading-text" aria-live="polite">{{ loadingText }}</p>
    </div>
    
    <div 
      v-else-if="error" 
      class="error-state"
      role="alert"
      aria-live="assertive"
    >
      <div class="error-icon" aria-hidden="true">⚠️</div>
      <h3 class="error-title" id="error-title">Loading Failed</h3>
      <p class="error-message" id="error-message">{{ error }}</p>
      <button 
        v-if="onRetry" 
        class="btn btn-primary" 
        @click="onRetry"
        aria-label="Retry loading exam"
        aria-describedby="error-message"
      >
        Retry
      </button>
    </div>
  </div>
</template>

<script setup>
/**
 * ExamPreloader Component
 * Handles loading states and error display for exam loading
 */

defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  loadingText: {
    type: String,
    default: 'Loading exam questions...'
  },
  onRetry: {
    type: Function,
    default: null
  }
})
</script>

<style scoped>
.exam-preloader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #6b7280;
  margin: 0;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-title {
  color: #dc2626;
  margin: 0 0 8px 0;
}

.error-message {
  color: #6b7280;
  margin: 0 0 16px 0;
}

.btn {
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

/* Focus styles for accessibility */
.btn:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Tablet breakpoint */
@media (max-width: 768px) {
  .exam-preloader {
    min-height: 180px;
  }
  
  .loading-state, .error-state {
    padding: 30px 20px;
  }
  
  .loading-spinner {
    width: 36px;
    height: 36px;
  }
  
  .error-icon {
    font-size: 40px;
  }
}

/* Mobile breakpoint */
@media (max-width: 480px) {
  .exam-preloader {
    min-height: 160px;
  }
  
  .loading-state, .error-state {
    padding: 24px 16px;
  }
  
  .loading-spinner {
    width: 32px;
    height: 32px;
  }
  
  .loading-text {
    font-size: 14px;
  }
  
  .error-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }
  
  .error-title {
    font-size: 18px;
  }
  
  .error-message {
    font-size: 14px;
  }
  
  .btn {
    width: 100%;
    padding: 12px 16px;
    min-height: 44px;
  }
}

/* Touch-friendly targets */
@media (pointer: coarse) {
  .btn {
    min-height: 44px;
    min-width: 44px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .loading-spinner {
    border-width: 5px;
    border-color: #000;
    border-top-color: #2563eb;
  }
  
  .error-state {
    border: 2px solid #dc2626;
    border-radius: 8px;
  }
  
  .btn-primary {
    border: 2px solid #1d4ed8;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
    border-top-color: #2563eb;
    opacity: 0.7;
  }
}
</style>
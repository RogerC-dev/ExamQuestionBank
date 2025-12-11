<template>
  <div class="error-boundary">
    <slot v-if="!hasError"></slot>
    
    <div 
      v-else 
      class="error-container"
      role="alert"
      aria-live="assertive"
    >
      <div class="error-icon" aria-hidden="true">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2"/>
          <path d="M12 8V12M12 16H12.01" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      
      <h2 class="error-title" id="error-boundary-title">{{ title }}</h2>
      <p class="error-message" id="error-boundary-message">{{ userFriendlyMessage }}</p>
      
      <div class="error-actions">
        <button 
          v-if="recoverable"
          class="btn btn-primary"
          @click="handleRetry"
          aria-label="Retry the failed operation"
        >
          重試
        </button>
        <button 
          class="btn btn-secondary"
          @click="handleGoBack"
          aria-label="Go back to previous page"
        >
          返回
        </button>
        <button 
          v-if="showReportButton"
          class="btn btn-outline"
          @click="handleReport"
          aria-label="Report this error"
        >
          回報問題
        </button>
      </div>
      
      <details v-if="showDetails && errorDetails" class="error-details">
        <summary>技術詳情</summary>
        <pre>{{ errorDetails }}</pre>
      </details>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorBoundary',
  props: {
    title: {
      type: String,
      default: '發生錯誤'
    },
    recoverable: {
      type: Boolean,
      default: true
    },
    showDetails: {
      type: Boolean,
      default: false
    },
    showReportButton: {
      type: Boolean,
      default: false
    },
    fallbackMessage: {
      type: String,
      default: '發生未預期的錯誤，請稍後再試。'
    }
  },
  emits: ['retry', 'report', 'error-captured'],
  data() {
    return {
      hasError: false,
      error: null,
      errorInfo: null
    }
  },
  computed: {
    userFriendlyMessage() {
      if (!this.error) return this.fallbackMessage
      
      // Convert technical errors to user-friendly messages
      const errorMessage = this.error.message || ''
      
      // Network errors
      if (this.isNetworkError(errorMessage)) {
        return '無法連接到伺服器，請檢查您的網路連線後再試。'
      }
      
      // Timeout errors
      if (this.isTimeoutError(errorMessage)) {
        return '請求超時，請稍後再試。'
      }
      
      // Permission errors
      if (this.isPermissionError(errorMessage)) {
        return '您沒有權限執行此操作。'
      }
      
      // Not found errors
      if (this.isNotFoundError(errorMessage)) {
        return '找不到請求的資源。'
      }
      
      // Server errors
      if (this.isServerError(errorMessage)) {
        return '伺服器目前發生問題，請稍後再試。'
      }
      
      // Check if message contains technical terms
      if (this.containsTechnicalTerms(errorMessage)) {
        return this.fallbackMessage
      }
      
      return errorMessage || this.fallbackMessage
    },
    errorDetails() {
      if (!this.error) return null
      
      return JSON.stringify({
        message: this.error.message,
        stack: this.error.stack,
        componentInfo: this.errorInfo
      }, null, 2)
    }
  },
  methods: {
    isNetworkError(message) {
      const networkTerms = ['network', 'fetch', 'connection', 'offline', 'ECONNREFUSED']
      return networkTerms.some(term => message.toLowerCase().includes(term.toLowerCase()))
    },
    isTimeoutError(message) {
      const timeoutTerms = ['timeout', 'timed out', 'ETIMEDOUT']
      return timeoutTerms.some(term => message.toLowerCase().includes(term.toLowerCase()))
    },
    isPermissionError(message) {
      const permissionTerms = ['403', 'forbidden', 'unauthorized', '401', 'permission']
      return permissionTerms.some(term => message.toLowerCase().includes(term.toLowerCase()))
    },
    isNotFoundError(message) {
      const notFoundTerms = ['404', 'not found']
      return notFoundTerms.some(term => message.toLowerCase().includes(term.toLowerCase()))
    },
    isServerError(message) {
      const serverTerms = ['500', '502', '503', '504', 'internal server', 'bad gateway']
      return serverTerms.some(term => message.toLowerCase().includes(term.toLowerCase()))
    },
    containsTechnicalTerms(message) {
      const technicalTerms = [
        'TypeError',
        'ReferenceError',
        'SyntaxError',
        'undefined is not',
        'Cannot read property',
        'Cannot read properties',
        'is not a function',
        'stack trace',
        'at Object.',
        'at Function.',
        'at Array.',
        'webpack',
        'node_modules',
        'chunk',
        'module',
        '__webpack',
        'Uncaught',
        'null is not',
        'NaN'
      ]
      
      return technicalTerms.some(term => 
        message.toLowerCase().includes(term.toLowerCase())
      )
    },
    handleRetry() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
      this.$emit('retry')
    },
    handleGoBack() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push('/')
      }
    },
    handleReport() {
      this.$emit('report', {
        error: this.error,
        errorInfo: this.errorInfo,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    },
    captureError(error, errorInfo) {
      this.hasError = true
      this.error = error
      this.errorInfo = errorInfo
      this.$emit('error-captured', { error, errorInfo })
      
      // Log error for debugging (in development)
      if (process.env.NODE_ENV === 'development') {
        console.error('ErrorBoundary caught an error:', error)
        console.error('Error info:', errorInfo)
      }
    },
    reset() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
    }
  },
  errorCaptured(error, instance, info) {
    this.captureError(error, info)
    // Return false to prevent the error from propagating further
    return false
  }
}
</script>

<style scoped>
.error-boundary {
  width: 100%;
  min-height: 200px;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  max-width: 500px;
  margin: 24px auto;
}

.error-icon {
  margin-bottom: 24px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.error-message {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
}

.error-details {
  margin-top: 24px;
  width: 100%;
  text-align: left;
}

.error-details summary {
  cursor: pointer;
  color: #6b7280;
  font-size: 14px;
  padding: 8px;
}

.error-details summary:hover {
  color: #374151;
}

.error-details pre {
  background: #f3f4f6;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
  color: #374151;
  margin-top: 8px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .error-container {
    padding: 32px 16px;
    margin: 16px;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .error-message {
    font-size: 14px;
  }
  
  .error-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .error-container {
    border: 2px solid #1f2937;
  }
  
  .error-icon svg circle,
  .error-icon svg path {
    stroke: #dc2626;
    stroke-width: 3;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .btn {
    transition: none;
  }
}
</style>

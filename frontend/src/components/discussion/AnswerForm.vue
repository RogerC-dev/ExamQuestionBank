<template>
  <div class="answer-form-mvp">
    <h4 class="form-title">撰寫回答</h4>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <textarea
          v-model="body"
          placeholder="分享您的知識和見解（至少 50 個字元）"
          :class="{ error: errors.body }"
          rows="6"
          maxlength="10000"
        ></textarea>
        <span class="char-count" :class="{ warning: body.length < 50 }">
          {{ body.length }}/10000
        </span>
        <span v-if="errors.body" class="error-msg">{{ errors.body }}</span>
      </div>
      
      <div class="form-actions">
        <button 
          type="submit" 
          class="btn-submit"
          :disabled="loading || !isValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>發佈回答</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const body = ref('')
const errors = ref({})

const isValid = computed(() => {
  return body.value.length >= 50
})

function validate() {
  errors.value = {}
  
  if (body.value.length < 50) {
    errors.value.body = '回答至少需要 50 個字元'
  }
  
  return Object.keys(errors.value).length === 0
}

function handleSubmit() {
  if (!validate()) return
  
  emit('submit', body.value.trim())
  body.value = ''
}
</script>

<style scoped>
.answer-form-mvp {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.25rem;
}

.dark .answer-form-mvp {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border-color-dark, #374151);
}

.form-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin: 0 0 1rem 0;
}

.dark .form-title {
  color: var(--text-primary-dark, #f9fafb);
}

.form-group {
  position: relative;
  margin-bottom: 0.5rem;
}

.form-group textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary, #f9fafb);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-primary, #111827);
  transition: all 0.2s ease;
  resize: vertical;
  min-height: 120px;
  box-sizing: border-box;
}

.dark .form-group textarea {
  background: var(--bg-tertiary, #374151);
  border-color: var(--border-color-dark, #4b5563);
  color: var(--text-primary-dark, #f9fafb);
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color, #4f46e5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group textarea.error {
  border-color: #ef4444;
}

.char-count {
  position: absolute;
  right: 0.5rem;
  bottom: -1.25rem;
  font-size: 0.75rem;
  color: var(--text-tertiary, #9ca3af);
}

.char-count.warning {
  color: #f59e0b;
}

.error-msg {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #ef4444;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 120px;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .answer-form-mvp {
    padding: 1rem;
  }
  
  .btn-submit {
    width: 100%;
  }
}
</style>

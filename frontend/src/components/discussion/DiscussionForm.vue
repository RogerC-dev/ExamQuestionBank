<template>
  <div class="discussion-form-mvp">
    <h3 class="form-title">{{ isEditing ? '編輯討論' : '發起新討論' }}</h3>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">標題</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="輸入問題標題（至少 10 個字元）"
          :class="{ error: errors.title }"
          maxlength="200"
        />
        <span class="char-count" :class="{ warning: title.length < 10 }">
          {{ title.length }}/200
        </span>
        <span v-if="errors.title" class="error-msg">{{ errors.title }}</span>
      </div>
      
      <div class="form-group">
        <label for="body">內容</label>
        <textarea
          id="body"
          v-model="body"
          placeholder="詳細描述您的問題或困惑（至少 20 個字元）"
          :class="{ error: errors.body }"
          rows="6"
          maxlength="5000"
        ></textarea>
        <span class="char-count" :class="{ warning: body.length < 20 }">
          {{ body.length }}/5000
        </span>
        <span v-if="errors.body" class="error-msg">{{ errors.body }}</span>
      </div>
      
      <div class="form-actions">
        <button 
          type="button" 
          class="btn-cancel"
          @click="handleCancel"
        >
          取消
        </button>
        <button 
          type="submit" 
          class="btn-submit"
          :disabled="loading || !isValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>{{ isEditing ? '更新' : '發佈' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  initialTitle: {
    type: String,
    default: ''
  },
  initialBody: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const title = ref(props.initialTitle)
const body = ref(props.initialBody)
const errors = ref({})

// Reset form when initial values change
watch(() => props.initialTitle, (val) => { title.value = val })
watch(() => props.initialBody, (val) => { body.value = val })

const isValid = computed(() => {
  return title.value.length >= 10 && body.value.length >= 20
})

function validate() {
  errors.value = {}
  
  if (title.value.length < 10) {
    errors.value.title = '標題至少需要 10 個字元'
  }
  
  if (body.value.length < 20) {
    errors.value.body = '內容至少需要 20 個字元'
  }
  
  return Object.keys(errors.value).length === 0
}

function handleSubmit() {
  if (!validate()) return
  
  emit('submit', {
    title: title.value.trim(),
    body: body.value.trim()
  })
}

function handleCancel() {
  title.value = ''
  body.value = ''
  errors.value = {}
  emit('cancel')
}
</script>

<style scoped>
.discussion-form-mvp {
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.5rem;
}

.dark .discussion-form-mvp {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border-color-dark, #374151);
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin: 0 0 1.5rem 0;
}

.dark .form-title {
  color: var(--text-primary-dark, #f9fafb);
}

.form-group {
  margin-bottom: 1.25rem;
  position: relative;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: var(--text-primary, #111827);
  margin-bottom: 0.5rem;
}

.dark .form-group label {
  color: var(--text-primary-dark, #f9fafb);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary, #f9fafb);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-primary, #111827);
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.dark .form-group input,
.dark .form-group textarea {
  background: var(--bg-tertiary, #374151);
  border-color: var(--border-color-dark, #4b5563);
  color: var(--text-primary-dark, #f9fafb);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color, #4f46e5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group input.error,
.form-group textarea.error {
  border-color: #ef4444;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
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
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: transparent;
  color: var(--text-secondary, #6b7280);
  border: 1px solid var(--border-color, #e5e7eb);
}

.dark .btn-cancel {
  border-color: var(--border-color-dark, #4b5563);
  color: var(--text-secondary-dark, #9ca3af);
}

.btn-cancel:hover {
  background: var(--bg-secondary, #f3f4f6);
}

.dark .btn-cancel:hover {
  background: var(--bg-tertiary, #374151);
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 100px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  border: none;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
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
  .discussion-form-mvp {
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>

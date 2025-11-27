<template>
  <div class="exam-form">
    <h2>{{ isEditMode ? '編輯考卷' : '新增考卷' }}</h2>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">考卷名稱 *</label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          required
          placeholder="請輸入考卷名稱"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="description">考試說明</label>
        <textarea
          id="description"
          v-model="formData.description"
          rows="3"
          placeholder="請輸入考試說明"
          class="form-input"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="time_limit">考試時間限制（分鐘）</label>
        <input
          id="time_limit"
          v-model.number="formData.time_limit"
          type="number"
          min="1"
          placeholder="請輸入時間限制"
          class="form-input"
        />
      </div>

      <div v-if="formError" class="form-error">{{ formError }}</div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="saving">
          {{ saving ? '儲存中...' : '儲存' }}
        </button>
        <button type="button" class="btn btn-secondary" @click="handleCancel">
          取消
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  exam: {
    type: Object,
    default: null
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'cancel'])

const isEditMode = ref(!!props.exam)

const formData = ref({
  name: '',
  description: '',
  time_limit: null
})

const formError = ref('')

// 定義函數（必須在 watch 之前）
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    time_limit: null
  }
}

const handleSubmit = () => {
  const trimmedName = formData.value.name.trim()
  if (!trimmedName) {
    formError.value = '請輸入考卷名稱'
    return
  }
  formError.value = ''

  const cleanedData = {
    name: trimmedName,
    description: formData.value.description?.trim() || '',
    ...(Number.isFinite(formData.value.time_limit) && formData.value.time_limit > 0
      ? { time_limit: formData.value.time_limit }
      : {})
  }
  emit('save', cleanedData)
}

const handleCancel = () => {
  emit('cancel')
}

// 監聽 exam prop 的變化
watch(() => props.exam, (newExam) => {
  if (newExam) {
    isEditMode.value = true
    formData.value = {
      name: newExam.name || '',
      description: newExam.description || '',
      time_limit: newExam.time_limit || null
    }
    formError.value = ''
  } else {
    isEditMode.value = false
    resetForm()
  }
}, { immediate: true })
</script>

<style scoped>
.exam-form {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.exam-form h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
}

textarea.form-input {
  resize: vertical;
  font-family: inherit;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.form-error {
  color: #d93025;
  margin: 8px 0;
  font-size: 13px;
}
</style>

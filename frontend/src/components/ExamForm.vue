<template>
  <div class="card mb-4">
    <div class="card-body">
      <h2 class="card-title mb-4">{{ isEditMode ? '編輯考卷' : '新增考卷' }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label for="name" class="form-label">考卷名稱 *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="請輸入考卷名稱"
            class="form-control"
          />
        </div>

        <div class="mb-3">
          <label for="description" class="form-label">考試說明</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="3"
            placeholder="請輸入考試說明"
            class="form-control"
          ></textarea>
        </div>

        <div class="mb-3">
          <label for="time_limit" class="form-label">考試時間限制（分鐘）</label>
          <input
            id="time_limit"
            v-model.number="formData.time_limit"
            type="number"
            min="1"
            placeholder="請輸入時間限制"
            class="form-control"
          />
        </div>

        <div v-if="formError" class="alert alert-danger mb-3" role="alert">{{ formError }}</div>

        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '儲存中...' : '儲存' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="handleCancel">
            取消
          </button>
        </div>
      </form>
    </div>
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
/* 使用 Bootstrap 樣式，不需要自定義樣式 */
</style>

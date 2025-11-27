<template>
  <div class="mock-exam-view">
    <h1>模擬測驗</h1>

    <section class="form-section">
      <form @submit.prevent="generate">
        <div class="form-grid">
          <label>
            名稱
            <input v-model="form.name" placeholder="未填則自動產生" />
          </label>

          <label>
            科目
            <select v-model.number="form.subject_id" required>
              <option disabled value="">請選擇科目</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </label>

          <label>
            題目數量
            <input v-model.number="form.question_count" type="number" min="5" max="100" required />
          </label>

          <label>
            難度
            <select v-model="form.difficulty">
              <option value="easy">容易</option>
              <option value="medium">中等</option>
              <option value="hard">困難</option>
            </select>
          </label>

          <label>
            指定考年度
            <input v-model.number="form.exam_year" type="number" min="2000" max="2099" placeholder="選填" />
          </label>

          <label>
            時間限制（分鐘）
            <input v-model.number="form.time_limit" type="number" min="5" max="600" placeholder="選填" />
          </label>
        </div>

        <label>
          主題關鍵字
          <input v-model="form.topic" placeholder="例如：民法債編" />
        </label>

        <label class="inline-checkbox">
          <input type="checkbox" v-model="form.reuse_question_bank" />
          優先使用題庫現有題目
        </label>

        <div class="actions">
          <button type="submit" :disabled="loading">
            {{ loading ? '生成中…' : '生成模擬測驗' }}
          </button>
          <span v-if="formError" class="form-error">{{ formError }}</span>
        </div>
      </form>
    </section>

    <section class="history">
      <header>
        <h2>歷史測驗</h2>
        <button @click="loadHistory" :disabled="loadingHistory">重新整理</button>
      </header>

      <div v-if="historyError" class="alert">{{ historyError }}</div>
      <p v-else-if="!mockExams.length" class="empty">尚未建立模擬測驗</p>

      <ul v-else>
        <li v-for="exam in mockExams" :key="exam.id">
          <div class="history-item">
            <div>
              <strong>{{ exam.name }}</strong>
              <span>｜{{ exam.subject_name }}</span>
            </div>
            <div class="meta">
              <span>{{ exam.question_count }} 題</span>
              <span v-if="exam.time_limit">{{ exam.time_limit }} 分鐘</span>
              <span>{{ formatDate(exam.generated_at) }}</span>
              <span>{{ exam.ai_generated ? 'AI 生成' : '題庫抽題' }}</span>
            </div>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { fetchSubjects } from '@/services/api'

const form = ref({
  name: 'AI 模擬測驗',
  subject_id: '',
  question_count: 20,
  difficulty: 'medium',
  exam_year: '',
  time_limit: '',
  topic: '',
  reuse_question_bank: false
})

const subjects = ref([])
const mockExams = ref([])
const loading = ref(false)
const loadingHistory = ref(false)
const formError = ref('')
const historyError = ref('')

const normalizePayload = () => {
  if (!form.value.subject_id) {
    formError.value = '請選擇科目'
    return null
  }
  formError.value = ''

  const payload = {
    ...form.value,
    subject_id: Number(form.value.subject_id),
    question_count: Number(form.value.question_count) || 20,
    difficulty: form.value.difficulty,
    reuse_question_bank: Boolean(form.value.reuse_question_bank)
  }

  if (!payload.name?.trim()) {
    delete payload.name
  } else {
    payload.name = payload.name.trim()
  }

  payload.topic = payload.topic?.trim() || undefined
  payload.exam_year = payload.exam_year || undefined
  payload.time_limit = payload.time_limit || undefined

  return payload
}

const generate = async () => {
  const payload = normalizePayload()
  if (!payload) {
    return
  }

  loading.value = true
  try {
    await api.post('/mock-exams/', payload)
    await loadHistory()
  } catch (error) {
    formError.value = error.response?.data?.detail || '生成失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  historyError.value = ''
  try {
    const { data } = await api.get('/mock-exams/')
    mockExams.value = data
  } catch (error) {
    historyError.value = error.response?.data?.detail || '無法取得歷史測驗'
  } finally {
    loadingHistory.value = false
  }
}

const loadSubjects = async () => {
  try {
    const { data } = await fetchSubjects()
    subjects.value = data
  } catch (error) {
    historyError.value = '無法載入科目列表'
  }
}

const formatDate = (value) => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

onMounted(async () => {
  await Promise.all([loadSubjects(), loadHistory()])
})
</script>

<style scoped>
.mock-exam-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.form-section,
.history {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
}

input,
select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.inline-checkbox {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

button {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-error,
.alert {
  color: #d93025;
  font-size: 13px;
}

.history header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  flex-direction: column;
}

.meta {
  font-size: 13px;
  color: #6b7280;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.empty {
  color: #6b7280;
}
</style>

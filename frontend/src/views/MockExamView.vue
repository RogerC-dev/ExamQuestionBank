<template>
  <div class="mock-exam-view">
    <h1>模擬測驗</h1>
    <form @submit.prevent="generate">
      <label>
        名稱
        <input v-model="form.name" required />
      </label>
      <label>
        題目數量
        <input v-model.number="form.question_count" type="number" min="5" />
      </label>
      <label>
        難度
        <select v-model="form.difficulty">
          <option value="easy">容易</option>
          <option value="medium">中等</option>
          <option value="hard">困難</option>
        </select>
      </label>
      <button type="submit">生成</button>
    </form>
    <section class="history">
      <h2>歷史測驗</h2>
      <ul>
        <li v-for="exam in mockExams" :key="exam.id">
          {{ exam.name }} - {{ exam.question_count }} 題 - {{ exam.created_at }}
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const form = ref({
  name: 'AI 模擬測驗',
  question_count: 20,
  difficulty: 'medium',
  subject: null,
})
const mockExams = ref([])

const generate = async () => {
  const payload = { ...form.value, subject: form.value.subject }
  await api.post('/mock-exams/', payload)
  await loadHistory()
}

const loadHistory = async () => {
  const { data } = await api.get('/mock-exams/')
  mockExams.value = data
}

onMounted(loadHistory)
</script>

<style scoped>
form {
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
}
.history ul {
  list-style: none;
  padding: 0;
}
</style>


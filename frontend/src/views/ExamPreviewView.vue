<template>
  <div class="exam-preview" v-if="exam">
    <header class="exam-header">
      <div>
        <h1>{{ exam.name }}</h1>
        <p class="description">{{ exam.description || '尚未提供說明' }}</p>
      </div>
      <div class="meta">
        <span>題數：{{ exam.exam_questions.length }}</span>
        <span v-if="exam.time_limit">時間限制：{{ exam.time_limit }} 分鐘</span>
      </div>
    </header>

    <div class="question-list">
      <article v-for="question in exam.exam_questions" :key="question.id" class="question-card">
        <header>
          <span class="order">第 {{ question.order }} 題</span>
          <span class="points" v-if="question.points">{{ question.points }} 分</span>
        </header>
        <p class="content">{{ question.question_content }}</p>
        <div class="question-meta">
          <span>{{ question.question_subject || '未分類' }}</span>
          <span>{{ question.question_category || '未分類' }}</span>
        </div>
      </article>
    </div>

    <footer class="actions">
      <button class="btn btn-primary" @click="startExam" :disabled="starting">{{ starting ? '準備中...' : '開始測驗' }}</button>
      <button class="btn" @click="router.back()">返回</button>
    </footer>
  </div>

  <div v-else class="empty-state">
    <p>{{ errorMessage || '載入考卷中...' }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()
const exam = ref(null)
const errorMessage = ref('')
const starting = ref(false)

const loadExam = async () => {
  try {
    const { data } = await examService.getExam(route.params.id)
    exam.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '無法載入考卷'
  }
}

const startExam = async () => {
  if (!exam.value) return
  starting.value = true
  try {
    await examService.startExam(exam.value.id)
    alert('考試開始！(TODO: 導向實際作答頁面)')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '無法開始考試'
  } finally {
    starting.value = false
  }
}

onMounted(loadExam)
</script>

<style scoped>
.exam-preview {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.exam-header {
  background: white;
  padding: 24px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.description {
  color: #6b7280;
  margin-top: 8px;
}

.meta span {
  display: block;
  color: #4b5563;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.question-card header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #4b5563;
}

.question-meta {
  display: flex;
  gap: 12px;
  color: #9ca3af;
  font-size: 13px;
}

.actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #6b7280;
}
</style>


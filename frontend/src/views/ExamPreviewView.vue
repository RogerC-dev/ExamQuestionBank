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
        <div class="header-actions">
          <button class="btn btn-primary" @click="handleStartExam" :disabled="starting || isQuizActive">{{ starting ? '準備中…' : '開始測驗' }}</button>
        </div>
      </div>
    </header>

    <div v-if="quizMessage" class="quiz-message">{{ quizMessage }}</div>

    <section v-if="showResults && examResults" class="results-panel">
      <div class="results-header">
        <h2>測驗成績</h2>
        <div class="score-display">
          <div class="score-value">{{ examResults.score }}</div>
          <div class="score-label">分</div>
        </div>
      </div>
      <div class="results-summary">
        <span>答對：{{ examResults.correct }} / {{ examResults.total }}</span>
        <span>正確率：{{ Math.round((examResults.correct / examResults.total) * 100) }}%</span>
      </div>
      <div class="results-details">
        <h3>答題詳情</h3>
        <div v-for="(result, index) in examResults.details" :key="index" class="result-item">
          <div class="result-header">
            <span class="result-number">第 {{ index + 1 }} 題</span>
            <span class="result-status" :class="{ correct: result.correct, wrong: !result.correct }">
              {{ result.correct ? '✓ 正確' : '✗ 錯誤' }}
            </span>
          </div>
          <p class="result-question">{{ result.question }}</p>
          <div class="result-answers">
            <div><strong>您的答案：</strong>{{ result.userAnswer }}</div>
            <div v-if="!result.correct"><strong>正確答案：</strong>{{ result.correctAnswer }}</div>
          </div>
        </div>
      </div>
      <div class="results-actions">
        <button class="btn btn-primary" @click="router.back()">返回</button>
        <button class="btn btn-secondary" @click="resetQuiz">重新測驗</button>
      </div>
    </section>

    <section v-if="isQuizActive" class="quiz-panel">
      <div class="quiz-header">
        <div>
          <strong>作答模式</strong>
          <span>第 {{ currentQuestionIndex + 1 }} / {{ exam.exam_questions.length }} 題</span>
        </div>
        <div class="timer" :class="{ danger: timeLeft <= 30 }">
          剩餘時間：{{ formattedTime }}
        </div>
      </div>

      <div v-if="currentQuestion" class="quiz-question">
        <p class="quiz-content">{{ currentQuestion.question_content }}</p>

        <div v-if="currentQuestionOptions.length > 0" class="quiz-options">
          <div
            v-for="option in currentQuestionOptions"
            :key="option.id"
            class="option-item"
            :class="{ selected: userAnswers[currentQuestionIndex] === option.id }"
            @click="selectOption(option.id)"
          >
            <span class="option-label">{{ getOptionLabel(option.order) }}.</span>
            <span class="option-content">{{ option.content }}</span>
          </div>
        </div>

        <div class="question-meta">
          <span>{{ currentQuestion.question_subject || '未分類' }}</span>
          <span>{{ currentQuestion.question_category || '未分類' }}</span>
        </div>
      </div>

      <div class="quiz-actions">
        <button class="btn" @click="prevQuestion" :disabled="currentQuestionIndex === 0">上一題</button>
        <button class="btn" @click="nextQuestion" :disabled="currentQuestionIndex === exam.exam_questions.length - 1">下一題</button>
        <button class="btn btn-secondary" @click="submitExam">提交答案</button>
      </div>
    </section>

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
      <button class="btn" @click="router.back()">返回</button>
    </footer>
  </div>

  <div v-else class="empty-state">
    <p>{{ errorMessage || '載入考卷中...' }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'
import questionService from '@/services/questionService'

const route = useRoute()
const router = useRouter()
const exam = ref(null)
const errorMessage = ref('')
const starting = ref(false)
const isQuizActive = ref(false)
const currentQuestionIndex = ref(0)
const timeLeft = ref(0)
const quizMessage = ref('')
const userAnswers = ref({})
const questionDetails = ref({})
const showResults = ref(false)
const examResults = ref(null)
const startTime = ref(null)
let timerHandle = null

const formattedTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
  const seconds = (timeLeft.value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})

const currentQuestion = computed(() => {
  if (!exam.value) return null
  return exam.value.exam_questions[currentQuestionIndex.value] || null
})

const currentQuestionOptions = computed(() => {
  if (!currentQuestion.value) return []
  const qId = currentQuestion.value.question
  return questionDetails.value[qId]?.options || []
})

const loadExam = async () => {
  try {
    const { data } = await examService.getExam(route.params.id)
    exam.value = data
    await loadAllQuestionDetails()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '無法載入考卷'
  }
}

const loadAllQuestionDetails = async () => {
  if (!exam.value) return
  for (const eq of exam.value.exam_questions) {
    if (!eq.question) continue
    try {
      const { data } = await questionService.getQuestion(eq.question)
      questionDetails.value[eq.question] = data
    } catch (error) {
      console.error(`Failed to load question ${eq.question}`, error)
    }
  }
}

const handleStartExam = () => startExam()

const startExam = async () => {
  if (!exam.value || starting.value) return
  starting.value = true
  quizMessage.value = ''
  userAnswers.value = {}
  showResults.value = false
  try {
    await examService.startExam(exam.value.id)
    launchQuiz()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '無法開始考試'
  } finally {
    starting.value = false
  }
}

const launchQuiz = () => {
  isQuizActive.value = true
  currentQuestionIndex.value = 0
  startTime.value = Date.now()
  const baseSeconds = exam.value.time_limit ? exam.value.time_limit * 60 : 30 * 60
  timeLeft.value = baseSeconds
  if (timerHandle) {
    clearInterval(timerHandle)
  }
  timerHandle = setInterval(() => {
    timeLeft.value -= 1
    if (timeLeft.value <= 0) {
      submitExam(true)
    }
  }, 1000)
}

const selectOption = (optionId) => {
  userAnswers.value[currentQuestionIndex.value] = optionId
}

const getOptionLabel = (order) => {
  return String.fromCharCode(64 + order)
}

const nextQuestion = () => {
  if (!exam.value) return
  currentQuestionIndex.value = Math.min(currentQuestionIndex.value + 1, exam.value.exam_questions.length - 1)
}

const prevQuestion = () => {
  currentQuestionIndex.value = Math.max(currentQuestionIndex.value - 1, 0)
}

const submitExam = async (autoSubmit = false) => {
  if (!autoSubmit && !confirm('確定要提交答案嗎？')) {
    return
  }

  if (timerHandle) {
    clearInterval(timerHandle)
    timerHandle = null
  }

  isQuizActive.value = false

  let correct = 0
  let total = exam.value.exam_questions.length
  const results = []

  exam.value.exam_questions.forEach((eq, index) => {
    const qId = eq.question
    const questionData = questionDetails.value[qId]
    if (!questionData) {
      results.push({ question: eq.question_content, correct: false, userAnswer: null, correctAnswer: null })
      return
    }

    const userAnswerId = userAnswers.value[index]
    const correctOption = questionData.options.find(opt => opt.is_correct)
    const userOption = questionData.options.find(opt => opt.id === userAnswerId)

    const isCorrect = correctOption && userAnswerId === correctOption.id
    if (isCorrect) correct++

    results.push({
      question: eq.question_content,
      correct: isCorrect,
      userAnswer: userOption?.content || '未作答',
      correctAnswer: correctOption?.content || '無正確答案'
    })
  })

  const score = Math.round((correct / total) * 100)
  const durationSeconds = startTime.value ? Math.round((Date.now() - startTime.value) / 1000) : null

  examResults.value = {
    correct,
    total,
    score,
    details: results
  }

  // Save result to backend
  try {
    await examService.saveExamResult({
      exam_id: exam.value.id,
      score,
      correct_count: correct,
      total_count: total,
      duration_seconds: durationSeconds
    })
  } catch (error) {
    console.error('Failed to save exam result:', error)
  }

  showResults.value = true
  quizMessage.value = autoSubmit ? '時間到！測驗已自動提交' : '測驗已提交'
}

const resetQuiz = () => {
  showResults.value = false
  examResults.value = null
  userAnswers.value = {}
  quizMessage.value = ''
}

onMounted(loadExam)
onBeforeUnmount(() => {
  if (timerHandle) {
    clearInterval(timerHandle)
    timerHandle = null
  }
})
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

.header-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
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

.quiz-panel {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.timer {
  font-weight: bold;
  color: #2563eb;
}

.timer.danger {
  color: #dc2626;
}

.quiz-question {
  margin-bottom: 16px;
}

.quiz-content {
  font-size: 18px;
  margin-bottom: 12px;
}

.quiz-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.quiz-message {
  margin: 16px 0;
  background: #fef3c7;
  color: #92400e;
  padding: 12px 16px;
  border-radius: 8px;
}

.countdown-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.countdown-box {
  background: #fff;
  padding: 32px 48px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.count {
  font-size: 56px;
  font-weight: bold;
  color: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #6b7280;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.option-item.selected {
  border-color: #2563eb;
  background: #dbeafe;
}

.option-label {
  font-weight: bold;
  color: #1f2937;
  min-width: 24px;
}

.option-content {
  flex: 1;
  color: #374151;
}

.results-panel {
  background: #fff;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.results-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #2563eb;
}

.score-label {
  font-size: 18px;
  color: #6b7280;
}

.results-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.results-summary span {
  color: #374151;
  font-weight: 500;
}

.results-details h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #1f2937;
}

.result-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.result-number {
  font-weight: 600;
  color: #1f2937;
}

.result-status {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 4px;
}

.result-status.correct {
  background: #d1fae5;
  color: #065f46;
}

.result-status.wrong {
  background: #fee2e2;
  color: #991b1b;
}

.result-question {
  color: #374151;
  margin-bottom: 8px;
}

.result-answers {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #6b7280;
  font-size: 14px;
}

.results-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #6b7280;
}
</style>

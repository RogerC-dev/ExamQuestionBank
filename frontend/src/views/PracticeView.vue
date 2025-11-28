<template>
  <div class="practice-view">
    <div class="container">
      <!-- Stats Summary -->
      <div class="stats-section">
        <div class="stat-card"><div class="stat-value">{{ stats.total_bank }}</div><div class="stat-label">題庫數</div></div>
        <div class="stat-card"><div class="stat-value">{{ stats.total_answered }}</div><div class="stat-label">已練習</div></div>
        <div class="stat-card"><div class="stat-value">{{ stats.accuracy }}%</div><div class="stat-label">正確率</div></div>
        <div class="stat-card clickable" @click="activeTab = 'wrong'"><div class="stat-value">{{ stats.wrong_count || 0 }}</div><div class="stat-label">待複習錯題</div></div>
      </div>

      <!-- Practice Modes -->
      <h2 class="section-title">選擇練習模式</h2>
      <div class="practice-modes">
        <div class="mode-card" @click="startPractice('historical')">
          <div class="mode-icon">📚</div>
          <div class="mode-title">歷屆考題</div>
          <div class="mode-desc">按年度練習歷屆考題</div>
        </div>
        <div class="mode-card" @click="activeTab = 'wrong'">
          <div class="mode-icon">❌</div>
          <div class="mode-title">錯題本</div>
          <div class="mode-desc">複習答錯的題目</div>
        </div>
        <div class="mode-card" @click="activeTab = 'bookmarks'">
          <div class="mode-icon">⭐</div>
          <div class="mode-title">收藏題庫</div>
          <div class="mode-desc">複習已收藏的題目</div>
        </div>
        <div class="mode-card" @click="router.push('/flashcards')">
          <div class="mode-icon">🃏</div>
          <div class="mode-title">快閃卡</div>
          <div class="mode-desc">SM-2間隔複習</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'exams' }" @click="activeTab = 'exams'">歷屆考卷</button>
        <button :class="{ active: activeTab === 'wrong' }" @click="activeTab = 'wrong'">錯題本 ({{ wrongQuestions.length }})</button>
        <button :class="{ active: activeTab === 'bookmarks' }" @click="activeTab = 'bookmarks'">收藏題目 ({{ bookmarks.length }})</button>
      </div>

      <!-- Quiz Mode -->
      <div v-if="quizMode" class="quiz-panel">
        <div class="quiz-header">
          <span>第 {{ currentIndex + 1 }} / {{ quizQuestions.length }} 題</span>
          <button class="btn btn-secondary" @click="exitQuiz">結束練習</button>
        </div>
        <div class="quiz-question">
          <p class="question-content">{{ currentQuestion?.content || currentQuestion?.question_content }}</p>
          <div class="quiz-options">
            <div
              v-for="opt in currentOptions"
              :key="opt.id"
              class="option-item"
              :class="{
                selected: selectedAnswer === opt.id,
                correct: showAnswer && opt.is_correct,
                wrong: showAnswer && selectedAnswer === opt.id && !opt.is_correct
              }"
              @click="!showAnswer && selectAnswer(opt.id)"
            >
              <span class="option-label">{{ getLabel(opt.order) }}.</span>
              <span>{{ opt.content }}</span>
            </div>
          </div>
          <div v-if="showAnswer" class="answer-feedback">
            <p v-if="isCorrect" class="correct-msg">✓ 正確！</p>
            <p v-else class="wrong-msg">✗ 錯誤，正確答案是：{{ correctAnswerLabel }}</p>
          </div>
        </div>
        <div class="quiz-actions">
          <button v-if="!showAnswer" class="btn btn-primary" :disabled="!selectedAnswer" @click="checkAnswer">確認答案</button>
          <button v-else class="btn btn-primary" @click="nextQuestion">{{ currentIndex < quizQuestions.length - 1 ? '下一題' : '完成' }}</button>
          <button class="btn" @click="addCurrentToFlashcard">加入快閃卡</button>
        </div>
      </div>

      <!-- Exams Tab -->
      <section v-if="activeTab === 'exams' && !quizMode" class="content-section">
        <div class="section-header">
          <h3>歷屆考卷</h3>
          <button class="btn btn-primary" @click="router.push('/admin/exams')">管理考卷</button>
        </div>
        <div v-if="loadingExams" class="loading">載入中...</div>
        <div v-else-if="!historicalExams.length" class="empty">目前尚無考卷</div>
        <div v-else class="exam-list">
          <div v-for="exam in historicalExams" :key="exam.id" class="exam-item">
            <div class="exam-info">
              <span class="exam-name">{{ exam.name }}</span>
              <span class="exam-meta">{{ exam.question_count }} 題</span>
            </div>
            <button class="btn btn-primary" @click="viewExam(exam.id)">開始測驗</button>
          </div>
        </div>
      </section>

      <!-- Wrong Questions Tab -->
      <section v-if="activeTab === 'wrong' && !quizMode" class="content-section">
        <div class="section-header">
          <h3>錯題本</h3>
          <button v-if="wrongQuestions.length" class="btn btn-primary" @click="startQuiz(wrongQuestions, 'wrong')">全部重測</button>
        </div>
        <div v-if="loadingWrong" class="loading">載入中...</div>
        <div v-else-if="!wrongQuestions.length" class="empty">🎉 太棒了！沒有錯題</div>
        <div v-else class="question-list">
          <div v-for="wq in wrongQuestions" :key="wq.id" class="question-item">
            <div class="question-info">
              <span class="wrong-badge">錯 {{ wq.wrong_count }} 次</span>
              <p class="question-text">{{ wq.question_content }}</p>
              <span class="question-subject">{{ wq.question_subject }}</span>
            </div>
            <div class="question-actions">
              <button class="btn btn-sm" @click="startSingleQuiz(wq)">重測</button>
              <button class="btn btn-sm" @click="addToFlashcard(wq.question)">快閃卡</button>
              <button class="btn btn-sm btn-secondary" @click="markReviewed(wq.id)">已複習</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Bookmarks Tab -->
      <section v-if="activeTab === 'bookmarks' && !quizMode" class="content-section">
        <div class="section-header">
          <h3>收藏題目</h3>
          <button v-if="bookmarks.length" class="btn btn-primary" @click="startQuiz(bookmarks, 'bookmark')">全部練習</button>
        </div>
        <div v-if="loadingBookmarks" class="loading">載入中...</div>
        <div v-else-if="!bookmarks.length" class="empty">尚無收藏題目</div>
        <div v-else class="question-list">
          <div v-for="bm in bookmarks" :key="bm.id" class="question-item">
            <div class="question-info">
              <p class="question-text">{{ bm.question_content }}</p>
              <span class="question-subject">{{ bm.question_subject }}</span>
            </div>
            <div class="question-actions">
              <button class="btn btn-sm" @click="startSingleQuiz(bm)">練習</button>
              <button class="btn btn-sm" @click="addToFlashcard(bm.question)">快閃卡</button>
              <button class="btn btn-sm btn-danger" @click="removeBookmark(bm.question)">移除</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import examService from '@/services/examService'
import questionService from '@/services/questionService'
import flashcardService from '@/services/flashcardService'

const router = useRouter()
const activeTab = ref('exams')
const stats = reactive({ total_bank: 0, total_answered: 0, accuracy: 0, exam_count: 0, wrong_count: 0 })

// Data
const historicalExams = ref([])
const wrongQuestions = ref([])
const bookmarks = ref([])
const loadingExams = ref(false)
const loadingWrong = ref(false)
const loadingBookmarks = ref(false)

// Quiz state
const quizMode = ref(false)
const quizQuestions = ref([])
const currentIndex = ref(0)
const currentOptions = ref([])
const selectedAnswer = ref(null)
const showAnswer = ref(false)
const isCorrect = ref(false)

const currentQuestion = computed(() => quizQuestions.value[currentIndex.value])
const correctAnswerLabel = computed(() => {
  const correct = currentOptions.value.find(o => o.is_correct)
  return correct ? `${getLabel(correct.order)}. ${correct.content}` : ''
})

const getLabel = (order) => String.fromCharCode(64 + (order || 1))

const loadData = async () => {
  loadingExams.value = true
  loadingWrong.value = true
  loadingBookmarks.value = true
  
  try {
    const [statsRes, examsRes, wrongRes, bookmarkRes] = await Promise.all([
      examService.getExamStats().catch(() => ({ data: {} })),
      examService.getExams({ page_size: 10 }).catch(() => ({ data: [] })),
      examService.getWrongQuestions().catch(() => ({ data: [] })),
      examService.getBookmarks().catch(() => ({ data: [] }))
    ])
    Object.assign(stats, statsRes.data || {})
    historicalExams.value = Array.isArray(examsRes.data) ? examsRes.data : examsRes.data?.results || []
    wrongQuestions.value = wrongRes.data || []
    bookmarks.value = bookmarkRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingExams.value = false
    loadingWrong.value = false
    loadingBookmarks.value = false
  }
}

const startPractice = (mode) => {
  if (mode === 'historical' && historicalExams.value.length) {
    viewExam(historicalExams.value[0].id)
  }
}

const viewExam = (examId) => router.push({ name: 'ExamPreview', params: { id: examId } })

const startQuiz = async (questions, type) => {
  quizQuestions.value = questions.map(q => ({
    id: q.question || q.id,
    content: q.question_content || q.content,
    subject: q.question_subject || q.subject
  }))
  currentIndex.value = 0
  selectedAnswer.value = null
  showAnswer.value = false
  await loadQuestionOptions(quizQuestions.value[0].id)
  quizMode.value = true
}

const startSingleQuiz = async (q) => {
  await startQuiz([q], 'single')
}

const loadQuestionOptions = async (questionId) => {
  try {
    const { data } = await questionService.getQuestion(questionId)
    currentOptions.value = data.options || []
  } catch (e) {
    currentOptions.value = []
  }
}

const selectAnswer = (optId) => {
  selectedAnswer.value = optId
}

const checkAnswer = () => {
  const correct = currentOptions.value.find(o => o.is_correct)
  isCorrect.value = correct && selectedAnswer.value === correct.id
  showAnswer.value = true
}

const nextQuestion = async () => {
  if (currentIndex.value < quizQuestions.value.length - 1) {
    currentIndex.value++
    selectedAnswer.value = null
    showAnswer.value = false
    await loadQuestionOptions(quizQuestions.value[currentIndex.value].id)
  } else {
    exitQuiz()
  }
}

const exitQuiz = () => {
  quizMode.value = false
  quizQuestions.value = []
  currentIndex.value = 0
  loadData() // Refresh data
}

const addCurrentToFlashcard = async () => {
  if (!currentQuestion.value) return
  try {
    await flashcardService.createFlashcard({ question: currentQuestion.value.id })
    alert('已加入快閃卡')
  } catch (e) {
    alert(e.message || '加入失敗')
  }
}

const addToFlashcard = async (questionId) => {
  try {
    await flashcardService.createFlashcard({ question: questionId })
    alert('已加入快閃卡')
  } catch (e) {
    alert(e.message || '加入失敗')
  }
}

const markReviewed = async (id) => {
  try {
    await examService.markWrongQuestionReviewed(id)
    wrongQuestions.value = wrongQuestions.value.filter(w => w.id !== id)
    stats.wrong_count = Math.max(0, (stats.wrong_count || 0) - 1)
  } catch (e) {
    console.error(e)
  }
}

const removeBookmark = async (questionId) => {
  try {
    await examService.removeBookmark(questionId)
    bookmarks.value = bookmarks.value.filter(b => b.question !== questionId)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  color: white;
}

.stat-card:nth-child(2) { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card:nth-child(3) { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-card:nth-child(4) { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); cursor: pointer; }

.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { font-size: 14px; opacity: 0.9; }

.section-title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }

.practice-modes {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 30px;
}

.mode-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.2s;
}

.mode-card:hover { transform: translateY(-4px); }
.mode-icon { font-size: 40px; margin-bottom: 12px; }
.mode-title { font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }
.mode-desc { font-size: 13px; color: #7f8c8d; }

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.tabs button.active { background: #2563eb; color: white; }

.content-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 { margin: 0; font-size: 18px; color: #2c3e50; }

.loading, .empty { text-align: center; padding: 40px; color: #666; }

.exam-list, .question-list { display: flex; flex-direction: column; gap: 12px; }

.exam-item, .question-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.exam-info, .question-info { flex: 1; }
.exam-name { font-weight: 600; color: #2c3e50; }
.exam-meta { font-size: 13px; color: #666; margin-left: 12px; }

.question-text { margin: 8px 0; color: #2c3e50; font-size: 15px; }
.question-subject { font-size: 13px; color: #666; }

.wrong-badge {
  display: inline-block;
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.question-actions { display: flex; gap: 8px; }

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  background: #2563eb;
  color: white;
}

.btn:hover { background: #1d4ed8; }
.btn-sm { padding: 6px 12px; font-size: 13px; }
.btn-secondary { background: #6b7280; }
.btn-secondary:hover { background: #4b5563; }
.btn-danger { background: #dc2626; }
.btn-danger:hover { background: #b91c1c; }
.btn-primary { background: #2563eb; }

/* Quiz Panel */
.quiz-panel {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.quiz-question { margin-bottom: 20px; }
.question-content { font-size: 18px; color: #1f2937; margin-bottom: 20px; line-height: 1.6; }

.quiz-options { display: flex; flex-direction: column; gap: 12px; }

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

.option-item:hover { border-color: #3b82f6; background: #eff6ff; }
.option-item.selected { border-color: #2563eb; background: #dbeafe; }
.option-item.correct { border-color: #10b981; background: #d1fae5; }
.option-item.wrong { border-color: #ef4444; background: #fee2e2; }

.option-label { font-weight: bold; min-width: 24px; }

.answer-feedback { margin-top: 16px; padding: 12px; border-radius: 8px; }
.correct-msg { color: #065f46; background: #d1fae5; padding: 12px; border-radius: 8px; margin: 0; }
.wrong-msg { color: #991b1b; background: #fee2e2; padding: 12px; border-radius: 8px; margin: 0; }

.quiz-actions { display: flex; gap: 12px; margin-top: 20px; }

@media (max-width: 768px) {
  .stats-section, .practice-modes { grid-template-columns: repeat(2, 1fr); }
  .exam-item, .question-item { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>

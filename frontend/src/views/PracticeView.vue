<template>
  <div class="split-view-container">
    <!-- Main Content Panel -->
    <div class="main-panel" :style="mainPanelStyle">
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
        <div class="mode-card ask-ai-card" @click="openChat()">
          <div class="mode-icon">🤖</div>
          <div class="mode-title">Ask AI</div>
          <div class="mode-desc">題目解析與追問</div>
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
          <div class="quiz-tools">
            <button class="btn btn-ghost" @click="openChat(composeQuestionPrompt(currentQuestion))">Ask AI</button>
            <button class="btn btn-secondary" @click="exitQuiz">結束練習</button>
          </div>
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
          <div class="section-actions">
            <button v-if="wrongQuestions.length" class="btn btn-primary" @click="startQuiz(wrongQuestions, 'wrong')">全部重測</button>
          </div>
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
              <button class="btn btn-sm btn-outline" @click="openChatFromQuestion(wq)">Ask AI</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Bookmarks Tab -->
      <section v-if="activeTab === 'bookmarks' && !quizMode" class="content-section">
        <div class="section-header">
          <h3>收藏題目</h3>
          <div class="section-actions">
            <button v-if="bookmarks.length" class="btn btn-primary" @click="startQuiz(bookmarks, 'bookmark')">全部練習</button>
          </div>
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
              <button class="btn btn-sm btn-outline" @click="openChatFromQuestion(bm)">Ask AI</button>
            </div>
          </div>
        </div>
      </section>
    </div>
    </div>

    <!-- Draggable Divider -->
    <div
      v-if="isChatOpen"
      class="split-divider"
      @mousedown="startDrag"
      @touchstart="startDrag"
    >
      <div class="divider-handle"></div>
    </div>

    <!-- AI Chat Panel (Split View) -->
    <div v-if="isChatOpen" class="chat-panel-split" :style="chatPanelStyle">
      <div class="chat-panel-header">
        <div class="chat-panel-title">
          <span class="chat-icon">🤖</span>
          <span>Ask AI</span>
        </div>
        <button class="btn-close" @click="closeChat" aria-label="關閉">×</button>
      </div>
      <AIChatInterface :prefill="chatPrefill" class="chat-panel-content" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import examService from '@/services/examService'
import questionService from '@/services/questionService'
import flashcardService from '@/services/flashcardService'
import AIChatInterface from '@/components/AIChatInterface.vue'

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

const loadQuestionOptions = async (questionId) => {
  try {
    const res = await questionService.getQuestionOptions(questionId)
    currentOptions.value = res.data || []
  } catch (e) {
    console.error('Failed to load options:', e)
    currentOptions.value = []
  }
}

const selectAnswer = (optionId) => {
  selectedAnswer.value = optionId
}

const checkAnswer = async () => {
  const selected = currentOptions.value.find(o => o.id === selectedAnswer.value)
  isCorrect.value = selected?.is_correct || false
  showAnswer.value = true

  // Record answer
  try {
    await examService.recordAnswer({
      question: currentQuestion.value.id,
      selected_option: selectedAnswer.value,
      is_correct: isCorrect.value
    })
    // Refresh wrong questions if answer was wrong
    if (!isCorrect.value) {
      const wrongRes = await examService.getWrongQuestions().catch(() => ({ data: [] }))
      wrongQuestions.value = wrongRes.data || []
    }
  } catch (e) {
    console.error('Failed to record answer:', e)
  }
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
  selectedAnswer.value = null
  showAnswer.value = false
  currentOptions.value = []
  loadData() // Refresh stats
}

const startSingleQuiz = async (question) => {
  await startQuiz([question], 'single')
}

const addToFlashcard = async (questionId) => {
  try {
    await flashcardService.addQuestionToFlashcard(questionId)
    alert('已加入快閃卡！')
  } catch (e) {
    console.error('Failed to add to flashcard:', e)
    alert('加入快閃卡失敗')
  }
}

const addCurrentToFlashcard = () => {
  if (currentQuestion.value?.id) {
    addToFlashcard(currentQuestion.value.id)
  }
}

const markReviewed = async (wrongQuestionId) => {
  try {
    await examService.markWrongQuestionReviewed(wrongQuestionId)
    wrongQuestions.value = wrongQuestions.value.filter(wq => wq.id !== wrongQuestionId)
  } catch (e) {
    console.error('Failed to mark as reviewed:', e)
  }
}

const removeBookmark = async (questionId) => {
  try {
    await examService.removeBookmark(questionId)
    bookmarks.value = bookmarks.value.filter(bm => bm.question !== questionId)
  } catch (e) {
    console.error('Failed to remove bookmark:', e)
  }
}

const composeQuestionPrompt = (question) => {
  if (!question) return ''
  const content = question.content || question.question_content || ''
  const options = currentOptions.value.map(o => `${getLabel(o.order)}. ${o.content}`).join('\n')
  const correctOpt = currentOptions.value.find(o => o.is_correct)
  const correctAnswer = correctOpt ? `正確答案：${getLabel(correctOpt.order)}. ${correctOpt.content}` : ''
  return `題目：${content}\n\n選項：\n${options}\n\n${correctAnswer}\n\n請解釋為什麼這個答案是正確的？`
}

const openChatFromQuestion = (question) => {
  const content = question.question_content || question.content || ''
  openChat(`題目：${content}\n\n請幫我解析這道題目`)
}

// Split View State
const isChatOpen = ref(false)
const chatPrefill = ref({ text: '', stamp: Date.now() })
const splitRatio = ref(0.6) // Main panel takes 60% by default
const isDragging = ref(false)
const minPanelWidth = 300 // Minimum width for each panel in pixels

// Computed styles for split view
const mainPanelStyle = computed(() => {
  if (!isChatOpen.value) {
    return { width: '100%' }
  }
  return { width: `calc(${splitRatio.value * 100}% - 4px)` }
})

const chatPanelStyle = computed(() => {
  if (!isChatOpen.value) {
    return { display: 'none' }
  }
  return { width: `calc(${(1 - splitRatio.value) * 100}% - 4px)` }
})

// Drag handlers for the divider
const startDrag = (e) => {
  isDragging.value = true
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag)
  document.addEventListener('touchend', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value) return

  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const containerWidth = window.innerWidth

  let newRatio = clientX / containerWidth

  // Enforce minimum panel widths
  const minRatio = minPanelWidth / containerWidth
  const maxRatio = 1 - minRatio

  newRatio = Math.max(minRatio, Math.min(maxRatio, newRatio))
  splitRatio.value = newRatio
}

const stopDrag = () => {
  isDragging.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''

  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
}

const openChat = (prefillText = '') => {
  chatPrefill.value = { text: prefillText, stamp: Date.now() }
  isChatOpen.value = true
}

const closeChat = () => {
  isChatOpen.value = false
}

const handleResize = () => {
  // Ensure split ratio respects minimum widths on resize
  const containerWidth = window.innerWidth
  const minRatio = minPanelWidth / containerWidth
  const maxRatio = 1 - minRatio

  if (splitRatio.value < minRatio) splitRatio.value = minRatio
  if (splitRatio.value > maxRatio) splitRatio.value = maxRatio
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  // Clean up any lingering drag state
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})
</script>

<style scoped>
/* Split View Container - Browser-like split tab layout */
.split-view-container {
  display: flex;
  width: 100%;
  height: calc(100vh - 140px); /* Account for header and nav */
  overflow: hidden;
  background: #f5f7fa;
}

/* Main Content Panel */
.main-panel {
  height: 100%;
  overflow-y: auto;
  background: #f5f7fa;
  transition: width 0.1s ease;
}

.container {
  max-width: 100%;
  padding: 20px;
}

/* Draggable Divider */
.split-divider {
  width: 8px;
  background: #e5e7eb;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s;
  position: relative;
}

.split-divider:hover,
.split-divider:active {
  background: #d1d5db;
}

.divider-handle {
  width: 4px;
  height: 40px;
  background: #9ca3af;
  border-radius: 2px;
  transition: background 0.2s;
}

.split-divider:hover .divider-handle,
.split-divider:active .divider-handle {
  background: #6b7280;
}

/* AI Chat Split Panel */
.chat-panel-split {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  overflow: hidden;
  transition: width 0.1s ease;
}

.chat-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.chat-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.chat-icon {
  font-size: 20px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  line-height: 1;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.chat-panel-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Stats Section */
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

/* Practice Mode Cards */
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

.ask-ai-card {
  background: #eef9ff;
  border: 2px solid #2563eb;
}

.ask-ai-card .mode-title,
.ask-ai-card .mode-desc {
  color: #2563eb;
}

.ask-ai-card:hover {
  background: #2563eb;
}

.ask-ai-card:hover .mode-title,
.ask-ai-card:hover .mode-desc {
  color: white;
}

/* Tabs */
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

/* Content Section */
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

.question-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* Buttons */
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
.btn-outline { background: transparent; border: 1px solid #2563eb; color: #2563eb; }
.btn-outline:hover { background: #2563eb; color: white; }
.btn-ghost { background: transparent; color: #2563eb; }
.btn-ghost:hover { background: #eff6ff; }

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

.quiz-tools {
  display: flex;
  gap: 8px;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .stats-section, .practice-modes {
    grid-template-columns: repeat(2, 1fr);
  }

  .container {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .split-view-container {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 140px);
  }

  .main-panel {
    width: 100% !important;
    height: auto;
    min-height: 50vh;
  }

  .split-divider {
    width: 100%;
    height: 8px;
    cursor: row-resize;
  }

  .divider-handle {
    width: 40px;
    height: 4px;
  }
  
  .chat-panel-split {
    width: 100% !important;
    height: 50vh;
    border-left: none;
    border-top: 1px solid #e5e7eb;
  }
  
  .stats-section, .practice-modes {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .exam-item, .question-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .container {
    padding: 16px 12px;
  }
  
  .stat-card {
    padding: 16px 12px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 12px;
  }
}

/* Ensure AI Chat Interface fills the panel */
:deep(.ai-chat-interface) {
  height: 100%;
}

:deep(.ai-chat-interface .chat-panel) {
  height: 100%;
}

:deep(.ai-chat-interface .chat-input-container) {
  flex-shrink: 0;
}
</style>

<template>
  <div class="split-view-container">
    <!-- Main Content Panel -->
    <div class="main-panel" :style="mainPanelStyle">
      <div class="container">
      <!-- Practice Modes -->
      <h2 class="section-title">選擇練習模式</h2>
      <div class="practice-modes">
        <div class="mode-card" @click="startPractice('historical')">
          <div class="mode-icon">題</div>
          <div class="mode-title">歷屆考題</div>
          <div class="mode-desc">按年度練習歷屆考題</div>
        </div>
        <div class="mode-card" @click="activeTab = 'wrong'">
          <div class="mode-icon">錯</div>
          <div class="mode-title">錯題本</div>
          <div class="mode-desc">複習答錯的題目</div>
        </div>
        <div class="mode-card" @click="activeTab = 'bookmarks'">
          <div class="mode-icon">藏</div>
          <div class="mode-title">收藏題庫</div>
          <div class="mode-desc">複習已收藏的題目</div>
        </div>
        <div class="mode-card ask-ai-card" @click="openChat()">
          <div class="mode-icon">AI</div>
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
            <button v-if="showAnswer" class="btn btn-ghost" @click="openChat(composeQuestionPrompt(currentQuestion, currentOptions))">Ask AI</button>
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
        <div v-else-if="!wrongQuestions.length" class="empty">太棒了！目前沒有錯題</div>
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
          <span class="chat-icon">AI</span>
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

const composeQuestionPrompt = (question, options = null) => {
  if (!question) return ''
  const content = question.content || question.question_content || ''
  const opts = options || currentOptions.value
  const optionsText = opts.map(o => `${getLabel(o.order)}. ${o.content}`).join('\n')
  const correctOpt = opts.find(o => o.is_correct)
  const correctAnswer = correctOpt ? `正確答案：${getLabel(correctOpt.order)}. ${correctOpt.content}` : ''
  return `題目：${content}\n\n選項：\n${optionsText}\n\n${correctAnswer}\n\n請解釋為什麼這個答案是正確的？`
}

const openChatFromQuestion = async (question) => {
  const content = question.question_content || question.content || ''
  const questionId = question.question || question.id

  try {
    // Load options for this question to provide full context to AI
    const res = await questionService.getQuestionOptions(questionId)
    const options = res.data || []

    if (options.length > 0) {
      // Compose full prompt with question and all options
      const optionsText = options.map(o => `${getLabel(o.order)}. ${o.content}`).join('\n')
      const correctOpt = options.find(o => o.is_correct)
      const correctAnswer = correctOpt ? `\n\n正確答案：${getLabel(correctOpt.order)}. ${correctOpt.content}` : ''
      openChat(`題目：${content}\n\n選項：\n${optionsText}${correctAnswer}\n\n請幫我解析這道題目，解釋為什麼正確答案是對的？`)
    } else {
      // Fallback if no options available
      openChat(`題目：${content}\n\n請幫我解析這道題目`)
    }
  } catch (e) {
    console.error('Failed to load question options for AI:', e)
    openChat(`題目：${content}\n\n請幫我解析這道題目`)
  }
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
.split-view-container {
  display: flex;
  width: 100%;
  height: calc(100vh - 140px);
  overflow: hidden;
  background: var(--bg-soft);
}

/* Main Content Panel */
.main-panel {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-soft);
  transition: width 0.1s ease;
}

.container {
  max-width: 1180px;
  padding: 20px;
  margin: 0 auto;
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
  background: #d3d8df;
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
  background: var(--surface);
  border-left: 1px solid var(--border);
  overflow: hidden;
  transition: width 0.1s ease;
}

.chat-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #f6f8fb;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.chat-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.chat-icon {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 700;
  font-size: 13px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  line-height: 1;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #eef1f5;
  color: var(--text-primary);
}

.chat-panel-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.section-title { font-size: 18px; font-weight: 800; color: var(--text-primary); margin-bottom: 18px; }

/* Practice Mode Cards */
.practice-modes {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 26px;
}

.mode-card {
  background: var(--surface);
  padding: 22px 18px;
  border-radius: 12px;
  text-align: left;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.mode-card:hover { transform: translateY(-3px); border-color: rgba(47,95,144,0.25); box-shadow: 0 14px 30px rgba(15,23,42,0.08); }
.mode-icon { width: 36px; height: 36px; border-radius: 10px; background: var(--primary-soft); color: var(--primary); display: grid; place-items: center; font-weight: 800; font-size: 13px; margin-bottom: 10px; letter-spacing: 0.05em; }
.mode-title { font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.mode-desc { font-size: 13px; color: var(--text-secondary); }

.ask-ai-card {
  background: #f3f7fb;
  border: 1px solid rgba(47, 95, 144, 0.4);
}

.ask-ai-card .mode-title,
.ask-ai-card .mode-desc {
  color: var(--primary);
}

.ask-ai-card .mode-icon { background: rgba(47, 95, 144, 0.1); }

/* Tabs */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.tabs button {
  padding: 10px 18px;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-primary);
  transition: all 0.2s;
}

.tabs button.active { background: var(--primary); color: #f7f9fc; border-color: var(--primary); box-shadow: 0 10px 24px rgba(47, 95, 144, 0.16); }

/* Content Section */
.content-section {
  background: var(--surface);
  padding: 22px;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-header h3 { margin: 0; font-size: 17px; color: var(--text-primary); font-weight: 700; }

.loading, .empty { text-align: center; padding: 36px; color: var(--text-secondary); }

.exam-list, .question-list { display: flex; flex-direction: column; gap: 10px; }

.exam-item, .question-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #f7f9fb;
  border-radius: 10px;
  border: 1px solid var(--border);
}

.exam-info, .question-info { flex: 1; }
.exam-name { font-weight: 700; color: var(--text-primary); }
.exam-meta { font-size: 13px; color: var(--text-secondary); margin-left: 12px; }

.question-text { margin: 6px 0; color: var(--text-primary); font-size: 15px; line-height: 1.5; }
.question-subject { font-size: 13px; color: var(--text-secondary); }

.wrong-badge {
  display: inline-block;
  background: #fdf1f1;
  color: #9a1b1b;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  border: 1px solid #f3d6d6;
}

.question-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* Buttons */
.btn {
  padding: 8px 14px;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  background: var(--primary);
  color: #f7f9fc;
  transition: all 0.2s;
}

.btn:hover { box-shadow: 0 10px 22px rgba(47, 95, 144, 0.18); transform: translateY(-1px); }
.btn-sm { padding: 7px 12px; font-size: 13px; }
.btn-secondary { background: #eef1f5; color: var(--text-primary); border-color: var(--border); }
.btn-secondary:hover { background: #e3e8ef; }
.btn-danger { background: #c0392b; }
.btn-danger:hover { background: #a83226; }
.btn-primary { background: var(--primary); }
.btn-outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
.btn-outline:hover { background: var(--primary); color: #f7f9fc; }
.btn-ghost { background: transparent; color: var(--primary); }
.btn-ghost:hover { background: #eef3f9; }

/* Quiz Panel */
.quiz-panel {
  background: var(--surface);
  padding: 22px;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.quiz-tools {
  display: flex;
  gap: 8px;
}

.quiz-question { margin-bottom: 18px; }
.question-content { font-size: 17px; color: var(--text-primary); margin-bottom: 18px; line-height: 1.6; }

.quiz-options { display: flex; flex-direction: column; gap: 10px; }

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fbfcfd;
}

.option-item:hover { border-color: rgba(47, 95, 144, 0.4); background: #f3f6fa; }
.option-item.selected { border-color: var(--primary); background: #eef3f9; }
.option-item.correct { border-color: #3b8c5a; background: #ecf8f1; }
.option-item.wrong { border-color: #c0392b; background: #fdf3f1; }

.option-label { font-weight: 700; min-width: 24px; color: var(--text-secondary); }

.answer-feedback { margin-top: 14px; padding: 12px; border-radius: 10px; }
.correct-msg { color: #1f6a3b; background: #ecf8f1; padding: 12px; border-radius: 10px; margin: 0; }
.wrong-msg { color: #a83226; background: #fdf1f0; padding: 12px; border-radius: 10px; margin: 0; }

.quiz-actions { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet 平板 */
@media (max-width: 1024px) {
  .stats-section, .practice-modes {
    grid-template-columns: repeat(2, 1fr);
  }

  .container {
    padding: 16px;
  }
  
  .chat-panel-split {
    min-width: 350px;
  }
  
  .mode-card {
    padding: 18px 14px;
  }
  
  .mode-icon {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
  
  .quiz-header {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .quiz-tools {
    width: 100%;
    justify-content: flex-end;
  }
}

/* Mobile 手機 */
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
    min-height: 400px;
    border-left: none;
    border-top: 1px solid var(--border);
  }
  
  .chat-panel-header {
    padding: 12px 14px;
  }
  
  .chat-panel-title {
    font-size: 14px;
  }
  
  .chat-icon {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  
  .btn-close {
    font-size: 18px;
  }
  
  .container {
    padding: 14px 10px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 14px;
  }
  
  .stats-section, .practice-modes {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .mode-card {
    padding: 16px 12px;
  }
  
  .mode-icon {
    width: 28px;
    height: 28px;
    font-size: 11px;
    margin-bottom: 8px;
  }
  
  .mode-title {
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .mode-desc {
    font-size: 11px;
  }
  
  .tabs {
    gap: 6px;
    margin-bottom: 14px;
  }
  
  .tabs button {
    padding: 8px 12px;
    font-size: 13px;
    flex: 1;
  }
  
  .content-section {
    padding: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .section-header h3 {
    font-size: 15px;
  }
  
  .section-actions {
    width: 100%;
  }
  
  .section-actions .btn {
    width: 100%;
  }
  
  .exam-item, .question-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
  }
  
  .question-info {
    width: 100%;
  }
  
  .question-text {
    font-size: 14px;
    margin: 4px 0;
  }
  
  .question-subject {
    font-size: 12px;
  }
  
  .wrong-badge {
    font-size: 11px;
    padding: 2px 6px;
  }
  
  .question-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .question-actions .btn-sm {
    flex: 1;
    font-size: 12px;
    padding: 6px 10px;
  }
  
  /* Quiz Panel */
  .quiz-panel {
    padding: 16px;
  }
  
  .quiz-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    font-size: 14px;
  }
  
  .quiz-tools {
    width: 100%;
    gap: 6px;
  }
  
  .quiz-tools .btn {
    flex: 1;
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .question-content {
    font-size: 15px;
    margin-bottom: 14px;
  }
  
  .quiz-options {
    gap: 8px;
  }
  
  .option-item {
    padding: 12px;
    font-size: 14px;
  }
  
  .option-label {
    min-width: 20px;
  }
  
  .answer-feedback {
    margin-top: 12px;
    padding: 10px;
    font-size: 14px;
  }
  
  .quiz-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .quiz-actions .btn {
    width: 100%;
  }
}

/* Small Mobile 小螢幕手機 */
@media (max-width: 480px) {
  .container {
    padding: 10px 8px;
  }
  
  .section-title {
    font-size: 15px;
  }
  
  .practice-modes {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .mode-card {
    padding: 14px 12px;
  }
  
  .tabs button {
    padding: 7px 10px;
    font-size: 12px;
  }
  
  .content-section {
    padding: 12px;
  }
  
  .exam-item, .question-item {
    padding: 10px;
  }
  
  .question-text {
    font-size: 13px;
  }
  
  .question-actions {
    flex-direction: column;
  }
  
  .question-actions .btn-sm {
    width: 100%;
  }
  
  .quiz-panel {
    padding: 12px;
  }
  
  .question-content {
    font-size: 14px;
  }
  
  .option-item {
    padding: 10px;
    font-size: 13px;
  }
  
  .chat-panel-split {
    height: 60vh;
    min-height: 350px;
  }
  
  .chat-panel-header {
    padding: 10px 12px;
  }
}

/* Landscape Mobile 橫向手機 */
@media (max-width: 768px) and (orientation: landscape) {
  .split-view-container {
    flex-direction: row;
  }
  
  .main-panel {
    width: 50% !important;
    height: 100%;
  }
  
  .split-divider {
    width: 8px;
    height: 100%;
    cursor: col-resize;
  }
  
  .divider-handle {
    width: 4px;
    height: 40px;
  }
  
  .chat-panel-split {
    width: 50% !important;
    height: 100%;
    border-left: 1px solid var(--border);
    border-top: none;
  }
  
  .practice-modes {
    grid-template-columns: repeat(4, 1fr);
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

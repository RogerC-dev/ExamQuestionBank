<template>
  <div class="flashcard-view">
    <div class="container">
      <!-- Review Mode -->
      <div v-if="reviewMode" class="review-mode">
        <div class="review-header">
          <span>{{ currentIndex + 1 }} / {{ reviewCards.length }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: ((currentIndex + 1) / reviewCards.length * 100) + '%' }"></div>
          </div>
          <button class="btn-exit" @click="exitReview">✕ 結束</button>
        </div>

        <div class="card-container">
          <div class="flashcard" :class="{ flipped: isFlipped }" @click="flipCard">
            <!-- Front - Question -->
            <div class="card-face card-front">
              <div class="card-badge">{{ currentCard?.question_subject }}</div>
              <div class="card-content">
                <p class="card-question">{{ currentCard?.question_content }}</p>
              </div>
              <div class="card-hint">點擊卡片查看答案</div>
            </div>
            <!-- Back - Answer -->
            <div class="card-face card-back">
              <div class="card-badge">答案</div>
              <div class="card-content">
                <div v-if="currentOptions.length" class="answer-options">
                  <div v-for="opt in currentOptions" :key="opt.id" class="answer-option" :class="{ correct: opt.is_correct }">
                    <span class="option-marker">{{ opt.is_correct ? '✓' : '' }}</span>
                    <span>{{ getLabel(opt.order) }}. {{ opt.content }}</span>
                  </div>
                </div>
                <p v-else class="no-options">無選項資料</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="isFlipped" class="rating-section">
          <p class="rating-prompt">你記得這題嗎？</p>
          <div class="rating-buttons">
            <button class="rating-btn again" @click="rateCard(1)" :disabled="isRating">
              <span class="rating-icon">😫</span>
              <span class="rating-text">完全忘記</span>
              <span class="rating-interval">1天後</span>
            </button>
            <button class="rating-btn hard" @click="rateCard(2)" :disabled="isRating">
              <span class="rating-icon">😓</span>
              <span class="rating-text">很難想起</span>
              <span class="rating-interval">1天後</span>
            </button>
            <button class="rating-btn good" @click="rateCard(3)" :disabled="isRating">
              <span class="rating-icon">🤔</span>
              <span class="rating-text">想了一下</span>
              <span class="rating-interval">{{ currentCard?.interval || 1 }}天後</span>
            </button>
            <button class="rating-btn easy" @click="rateCard(4)" :disabled="isRating">
              <span class="rating-icon">😊</span>
              <span class="rating-text">還記得</span>
              <span class="rating-interval">{{ Math.round((currentCard?.interval || 1) * 1.5) }}天後</span>
            </button>
            <button class="rating-btn perfect" @click="rateCard(5)" :disabled="isRating">
              <span class="rating-icon">🎯</span>
              <span class="rating-text">非常熟悉</span>
              <span class="rating-interval">{{ Math.round((currentCard?.interval || 1) * 2) }}天後</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Dashboard Mode -->
      <template v-else>
        <header class="page-header">
          <h2>🃏 快閃卡複習</h2>
          <p>SM-2 間隔重複演算法，越熟悉的卡片間隔越長</p>
        </header>

        <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="alert success">{{ successMessage }}</div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card primary">
            <div class="stat-icon">📚</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.due_cards }}</span>
              <span class="stat-label">今日待複習</span>
            </div>
            <button v-if="stats.due_cards > 0" class="btn-start" @click="startReview">
              開始複習 →
            </button>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_cards }}</span>
              <span class="stat-label">總卡片數</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.review_streak }}</span>
              <span class="stat-label">連續天數</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.completion_percent }}%</span>
              <span class="stat-label">完成率</span>
            </div>
          </div>
        </div>

        <!-- Quick Add -->
        <div class="quick-add">
          <h3>新增快閃卡</h3>
          <form @submit.prevent="handleCreate" class="add-form">
            <input v-model="questionIdInput" type="number" placeholder="輸入題目 ID" min="1" />
            <button type="submit" :disabled="isCreating">{{ isCreating ? '新增中...' : '新增' }}</button>
          </form>
        </div>

        <!-- Card List -->
        <div class="card-list-section">
          <div class="list-header">
            <h3>我的快閃卡 ({{ flashcards.length }})</h3>
            <select v-model="statusFilter">
              <option value="all">全部</option>
              <option value="learning">學習中</option>
              <option value="reviewing">複習中</option>
              <option value="mastered">已掌握</option>
            </select>
          </div>
          <div v-if="isListLoading" class="loading">載入中...</div>
          <div v-else-if="flashcards.length === 0" class="empty">
            <p>尚無快閃卡</p>
            <p class="hint">從練習頁面的錯題本或收藏題目加入快閃卡</p>
          </div>
          <div v-else class="card-list">
            <div v-for="card in flashcards" :key="card.id" class="list-card">
              <div class="list-card-content">
                <span class="list-card-subject">{{ card.question_subject }}</span>
                <p class="list-card-question">{{ card.question_content }}</p>
                <div class="list-card-meta">
                  <span :class="'status-' + card.status">{{ statusLabel(card.status) }}</span>
                  <span>下次：{{ formatDate(card.next_review_date) }}</span>
                  <span>複習 {{ card.review_count }} 次</span>
                </div>
              </div>
              <button class="btn-delete" @click="handleDelete(card.id)" :disabled="deletingCardId === card.id">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import flashcardService from '@/services/flashcardService'
import questionService from '@/services/questionService'

// State
const stats = ref({ total_cards: 0, due_cards: 0, completion_percent: 0, review_streak: 0 })
const flashcards = ref([])
const dueFlashcards = ref([])
const statusFilter = ref('all')
const questionIdInput = ref('')
const isListLoading = ref(false)
const isCreating = ref(false)
const deletingCardId = ref(null)
const errorMessage = ref('')
const successMessage = ref('')

// Review mode state
const reviewMode = ref(false)
const reviewCards = ref([])
const currentIndex = ref(0)
const isFlipped = ref(false)
const isRating = ref(false)
const currentOptions = ref([])

const currentCard = computed(() => reviewCards.value[currentIndex.value])
const getLabel = (order) => String.fromCharCode(64 + (order || 1))

const statusLabel = (status) => ({ learning: '學習中', reviewing: '複習中', mastered: '已掌握' }[status] || status)
const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-TW') : '未排定'

const showError = (msg) => { errorMessage.value = msg; setTimeout(() => errorMessage.value = '', 4000) }
const showSuccess = (msg) => { successMessage.value = msg; setTimeout(() => successMessage.value = '', 3000) }

// Load data
const loadStats = async () => {
  try { stats.value = await flashcardService.getStatistics() } catch (e) { showError(e.message) }
}

const loadFlashcards = async () => {
  try {
    isListLoading.value = true
    const params = statusFilter.value !== 'all' ? { status: statusFilter.value } : {}
    flashcards.value = await flashcardService.getFlashcards(params)
  } catch (e) { showError(e.message) }
  finally { isListLoading.value = false }
}

const loadDueFlashcards = async () => {
  try { dueFlashcards.value = await flashcardService.getDueFlashcards() } catch (e) { showError(e.message) }
}

// Review functions
const startReview = async () => {
  await loadDueFlashcards()
  if (dueFlashcards.value.length === 0) {
    showError('沒有待複習的卡片')
    return
  }
  reviewCards.value = [...dueFlashcards.value]
  currentIndex.value = 0
  isFlipped.value = false
  await loadCurrentOptions()
  reviewMode.value = true
}

const loadCurrentOptions = async () => {
  if (!currentCard.value?.question) return
  try {
    const { data } = await questionService.getQuestion(currentCard.value.question)
    currentOptions.value = data.options || []
  } catch (e) {
    currentOptions.value = []
  }
}

const flipCard = () => {
  if (!isFlipped.value) isFlipped.value = true
}

const rateCard = async (rating) => {
  if (!currentCard.value || isRating.value) return
  isRating.value = true
  try {
    await flashcardService.reviewFlashcard(currentCard.value.id, rating)
    // Next card or finish
    if (currentIndex.value < reviewCards.value.length - 1) {
      currentIndex.value++
      isFlipped.value = false
      await loadCurrentOptions()
    } else {
      showSuccess(`🎉 完成！複習了 ${reviewCards.value.length} 張卡片`)
      exitReview()
    }
  } catch (e) {
    showError(e.message)
  } finally {
    isRating.value = false
  }
}

const exitReview = () => {
  reviewMode.value = false
  reviewCards.value = []
  currentIndex.value = 0
  isFlipped.value = false
  loadStats()
  loadFlashcards()
}

// CRUD
const handleCreate = async () => {
  if (!questionIdInput.value) return
  isCreating.value = true
  try {
    await flashcardService.createFlashcard({ question: parseInt(questionIdInput.value) })
    questionIdInput.value = ''
    showSuccess('已新增快閃卡')
    loadStats()
    loadFlashcards()
  } catch (e) { showError(e.message) }
  finally { isCreating.value = false }
}

const handleDelete = async (id) => {
  deletingCardId.value = id
  try {
    await flashcardService.deleteFlashcard(id)
    flashcards.value = flashcards.value.filter(c => c.id !== id)
    loadStats()
  } catch (e) { showError(e.message) }
  finally { deletingCardId.value = null }
}

watch(statusFilter, loadFlashcards)
onMounted(() => { loadStats(); loadFlashcards() })
</script>

<style scoped>
.container { max-width: 900px; margin: 0 auto; padding: 20px; }

/* Page Header */
.page-header { text-align: center; margin-bottom: 30px; }
.page-header h2 { font-size: 28px; margin-bottom: 8px; }
.page-header p { color: #666; }

/* Alerts */
.alert { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; }
.alert.error { background: #fee2e2; color: #991b1b; }
.alert.success { background: #d1fae5; color: #065f46; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }
.stat-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.stat-card.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.stat-icon { font-size: 32px; }
.stat-info { text-align: center; }
.stat-value { display: block; font-size: 28px; font-weight: bold; }
.stat-label { font-size: 13px; opacity: 0.8; }
.btn-start {
  margin-top: 8px;
  padding: 10px 20px;
  background: rgba(255,255,255,0.2);
  border: 2px solid white;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-start:hover { background: white; color: #667eea; }

/* Quick Add */
.quick-add { background: white; padding: 20px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.quick-add h3 { margin-bottom: 12px; font-size: 16px; }
.add-form { display: flex; gap: 12px; }
.add-form input { flex: 1; padding: 12px 16px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 15px; }
.add-form button { padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
.add-form button:disabled { opacity: 0.6; }

/* Card List */
.card-list-section { background: white; padding: 20px; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.list-header h3 { font-size: 16px; }
.list-header select { padding: 8px 12px; border: 2px solid #e5e7eb; border-radius: 8px; }
.loading, .empty { text-align: center; padding: 40px; color: #666; }
.empty .hint { font-size: 13px; margin-top: 8px; }

.card-list { display: flex; flex-direction: column; gap: 12px; }
.list-card { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #f8fafc; border-radius: 12px; }
.list-card-subject { font-size: 12px; color: #2563eb; font-weight: 600; }
.list-card-question { margin: 8px 0; color: #1f2937; font-size: 15px; line-height: 1.5; }
.list-card-meta { display: flex; gap: 16px; font-size: 12px; color: #666; }
.status-learning { color: #f59e0b; }
.status-reviewing { color: #3b82f6; }
.status-mastered { color: #10b981; }
.btn-delete { background: none; border: none; font-size: 18px; cursor: pointer; opacity: 0.5; }
.btn-delete:hover { opacity: 1; }

/* ========== REVIEW MODE ========== */
.review-mode { min-height: 80vh; display: flex; flex-direction: column; }

.review-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
  padding: 16px;
  background: white;
  border-radius: 12px;
}
.progress-bar { flex: 1; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.3s; }
.btn-exit { padding: 8px 16px; background: #f3f4f6; border: none; border-radius: 8px; cursor: pointer; }

/* Flashcard */
.card-container { perspective: 1000px; margin-bottom: 30px; }
.flashcard {
  width: 100%;
  height: 400px;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.flashcard.flipped { transform: rotateY(180deg); }

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 24px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.card-front {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-back {
  background: white;
  transform: rotateY(180deg);
  border: 3px solid #e5e7eb;
}

.card-badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  align-self: flex-start;
}
.card-back .card-badge { background: #f3f4f6; color: #374151; }

.card-content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.card-question { font-size: 22px; line-height: 1.6; text-align: center; }
.card-hint { text-align: center; font-size: 14px; opacity: 0.7; }

/* Answer Options */
.answer-options { display: flex; flex-direction: column; gap: 12px; }
.answer-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
}
.answer-option.correct { background: #d1fae5; border: 2px solid #10b981; }
.option-marker { font-weight: bold; color: #10b981; min-width: 20px; }
.no-options { text-align: center; color: #666; }

/* Rating Section */
.rating-section { text-align: center; }
.rating-prompt { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #374151; }
.rating-buttons { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }

.rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
}
.rating-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.rating-icon { font-size: 28px; }
.rating-text { font-size: 13px; font-weight: 600; }
.rating-interval { font-size: 11px; opacity: 0.7; }

.rating-btn.again { background: #fee2e2; color: #991b1b; }
.rating-btn.hard { background: #fef3c7; color: #92400e; }
.rating-btn.good { background: #e0f2fe; color: #0369a1; }
.rating-btn.easy { background: #d1fae5; color: #065f46; }
.rating-btn.perfect { background: #ede9fe; color: #5b21b6; }

.rating-btn:hover:not(:disabled) { transform: translateY(-4px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .flashcard { height: 350px; }
  .card-question { font-size: 18px; }
  .rating-buttons { gap: 8px; }
  .rating-btn { min-width: 80px; padding: 12px 14px; }
}
</style>

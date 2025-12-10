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
          <button class="btn-exit" @click="exitReview"><i class="bi bi-x-lg me-2"></i>結束</button>
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
              <span class="rating-icon"><i class="bi bi-emoji-frown"></i></span>
              <span class="rating-text">完全忘記</span>
              <span class="rating-interval">1天後</span>
            </button>
            <button class="rating-btn hard" @click="rateCard(2)" :disabled="isRating">
              <span class="rating-icon"><i class="bi bi-emoji-neutral"></i></span>
              <span class="rating-text">很難想起</span>
              <span class="rating-interval">1天後</span>
            </button>
            <button class="rating-btn good" @click="rateCard(3)" :disabled="isRating">
              <span class="rating-icon"><i class="bi bi-emoji-expressionless"></i></span>
              <span class="rating-text">想了一下</span>
              <span class="rating-interval">{{ currentCard?.interval || 1 }}天後</span>
            </button>
            <button class="rating-btn easy" @click="rateCard(4)" :disabled="isRating">
              <span class="rating-icon"><i class="bi bi-emoji-smile"></i></span>
              <span class="rating-text">還記得</span>
              <span class="rating-interval">{{ Math.round((currentCard?.interval || 1) * 1.5) }}天後</span>
            </button>
            <button class="rating-btn perfect" @click="rateCard(5)" :disabled="isRating">
              <span class="rating-icon"><i class="bi bi-emoji-laughing"></i></span>
              <span class="rating-text">非常熟悉</span>
              <span class="rating-interval">{{ Math.round((currentCard?.interval || 1) * 2) }}天後</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Dashboard Mode -->
      <template v-else>
        <header class="page-header">
          <h2><i class="bi bi-collection me-2"></i>快閃卡複習</h2>
        </header>

        <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="alert success">{{ successMessage }}</div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card primary">
            <div class="stat-icon"><i class="bi bi-book"></i></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.due_cards }}</span>
              <span class="stat-label">今日待複習</span>
            </div>
            <button v-if="stats.due_cards > 0" class="btn-start" @click="startReview">
              開始複習 →
            </button>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="bi bi-bullseye"></i></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_cards }}</span>
              <span class="stat-label">總卡片數</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="bi bi-fire"></i></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.review_streak }}</span>
              <span class="stat-label">連續天數</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon"><i class="bi bi-check-circle-fill"></i></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.completion_percent }}%</span>
              <span class="stat-label">完成率</span>
            </div>
          </div>
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
                <i class="bi bi-trash"></i>
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
const isListLoading = ref(false)
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
.page-header h2 { font-size: 28px; font-weight: 800; color: var(--text-primary); margin-bottom: 8px; }
.page-header p { color: var(--text-secondary); font-size: 14px; }

/* Alerts */
.alert { padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; font-size: 14px; }
.alert.error { background: #fdf1f1; color: #9a1b1b; border: 1px solid #f3d6d6; }
.alert.success { background: #ecf8f1; color: #1f6a3b; border: 1px solid #cef3e8; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }
.stat-card {
  background: var(--surface);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15,23,42,0.05);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  color: var(--primary);
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(15,23,42,0.08); }
.stat-card.primary { background: var(--primary); color: white; border: none; }
.stat-card.primary:hover { background: var(--primary-hover); }
.stat-icon { font-size: 32px; display: flex; align-items: center; justify-content: center; }
.stat-info { text-align: center; width: 100%; }
.stat-value { display: block; font-size: 28px; font-weight: 700; color: inherit; }
.stat-label { font-size: 13px; opacity: 0.8; margin-top: 4px; color: inherit; display: block; }
.btn-start {
  margin-top: 8px;
  padding: 10px 20px;
  background: rgba(255,255,255,0.2);
  border: 2px solid white;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s;
  width: 100%;
  max-width: 200px;
}
.btn-start:hover { background: white; color: var(--primary); }


/* Card List */
.card-list-section { background: var(--surface); padding: 20px; border-radius: 12px; box-shadow: 0 12px 28px rgba(15,23,42,0.05); border: 1px solid var(--border); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.list-header h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.list-header select { padding: 8px 12px; border: 1px solid var(--border); border-radius: 10px; background: var(--surface); color: var(--text-primary); font-size: 14px; cursor: pointer; }
.loading, .empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty .hint { font-size: 13px; margin-top: 8px; color: var(--text-secondary); }

.card-list { display: flex; flex-direction: column; gap: 12px; }
.list-card { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #f7f9fb; border-radius: 12px; border: 1px solid var(--border); transition: all 0.2s; gap: 12px; }
.list-card:hover { background: #f0f4f8; }
.list-card-content { flex: 1; min-width: 0; }
.list-card-subject { font-size: 12px; color: var(--primary); font-weight: 600; display: block; }
.list-card-question { margin: 8px 0; color: var(--text-primary); font-size: 15px; line-height: 1.5; word-break: break-word; }
.list-card-meta { display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary); flex-wrap: wrap; }
.status-learning { color: #f59e0b; font-weight: 600; }
.status-reviewing { color: #3b82f6; font-weight: 600; }
.status-mastered { color: #10b981; font-weight: 600; }
.btn-delete { background: none; border: none; font-size: 18px; cursor: pointer; opacity: 0.5; transition: opacity 0.2s; color: var(--text-primary); padding: 8px; flex-shrink: 0; }
.btn-delete:hover { opacity: 1; }

/* ========== REVIEW MODE ========== */
.review-mode { min-height: 80vh; display: flex; flex-direction: column; }

.review-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
  padding: 16px;
  background: var(--surface);
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15,23,42,0.05);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}
.review-header > span { white-space: nowrap; }
.progress-bar { flex: 1; min-width: 200px; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--primary-hover)); transition: width 0.3s; }
.btn-exit { padding: 8px 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; cursor: pointer; color: var(--text-primary); font-weight: 600; font-size: 14px; transition: all 0.2s; white-space: nowrap; }
.btn-exit:hover { background: #f0f4f8; }

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
  border-radius: 12px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  overflow-y: auto;
}

.card-front {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
}

.card-back {
  background: var(--surface);
  transform: rotateY(180deg);
  border: 1px solid var(--border);
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
.card-back .card-badge { background: var(--primary-soft); color: var(--primary); }

.card-content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.card-question { font-size: 22px; line-height: 1.6; text-align: center; word-break: break-word; }
.card-hint { text-align: center; font-size: 14px; opacity: 0.7; }

/* Answer Options */
.answer-options { display: flex; flex-direction: column; gap: 12px; }
.answer-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  background: #f7f9fb;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-word;
}
.answer-option.correct { background: #ecf8f1; border: 2px solid #10b981; }
.option-marker { font-weight: bold; color: #10b981; min-width: 20px; flex-shrink: 0; }
.no-options { text-align: center; color: var(--text-secondary); }

/* Rating Section */
.rating-section { text-align: center; }
.rating-prompt { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: var(--text-primary); }
.rating-buttons { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }

.rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
  font-weight: 600;
}
.rating-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.rating-icon { font-size: 28px; }
.rating-text { font-size: 13px; font-weight: 600; }
.rating-interval { font-size: 11px; opacity: 0.7; }

.rating-btn.again { background: #fdf1f1; color: #9a1b1b; border: 1px solid #f3d6d6; }
.rating-btn.hard { background: #fef9e7; color: #92400e; border: 1px solid #fbe8c3; }
.rating-btn.good { background: #eff5fc; color: #0369a1; border: 1px solid #dce7f4; }
.rating-btn.easy { background: #ecf8f1; color: #1f6a3b; border: 1px solid #cef3e8; }
.rating-btn.perfect { background: #f4f1fb; color: #5b21b6; border: 1px solid #e8dff8; }

.rating-btn:hover:not(:disabled) { transform: translateY(-4px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet 平板 */
@media (max-width: 1024px) {
  .container { padding: 16px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-card { padding: 16px; }
  .stat-icon { font-size: 28px; }
  .stat-value { font-size: 24px; }
  .rating-buttons { gap: 10px; }
  .rating-btn { min-width: 90px; padding: 14px 16px; }
}

/* Mobile 手機 */
@media (max-width: 768px) {
  .container { padding: 12px; }
  
  /* Header */
  .page-header h2 { font-size: 22px; }
  .page-header { margin-bottom: 20px; }
  
  /* Stats Grid - 單欄顯示 */
  .stats-grid { 
    grid-template-columns: 1fr; 
    gap: 12px; 
    margin-bottom: 20px; 
  }
  .stat-card {
    flex-direction: row;
    justify-content: space-between;
    padding: 16px;
  }
  .stat-card.primary {
    flex-direction: column;
  }
  .stat-icon { font-size: 24px; }
  .stat-info { text-align: left; }
  .stat-card.primary .stat-info { text-align: center; }
  .stat-value { font-size: 22px; }
  .stat-label { font-size: 12px; }
  .btn-start { width: 100%; max-width: none; }
  
  /* Card List */
  .card-list-section { padding: 16px; }
  .list-header { flex-direction: column; align-items: stretch; }
  .list-header h3 { font-size: 15px; }
  .list-header select { width: 100%; }
  
  .list-card { 
    flex-direction: column; 
    align-items: flex-start; 
    padding: 14px; 
  }
  .list-card-question { font-size: 14px; }
  .list-card-meta { 
    gap: 12px; 
    font-size: 11px; 
    width: 100%; 
  }
  .btn-delete { 
    position: absolute; 
    top: 10px; 
    right: 10px; 
  }
  .list-card { position: relative; padding-right: 40px; }
  
  /* Review Mode */
  .review-header { 
    padding: 12px; 
    gap: 10px; 
    font-size: 14px; 
  }
  .progress-bar { min-width: 100%; order: 3; }
  .btn-exit { 
    padding: 6px 12px; 
    font-size: 13px; 
  }
  
  /* Flashcard */
  .flashcard { height: 320px; }
  .card-face { padding: 20px; }
  .card-badge { font-size: 11px; padding: 5px 12px; }
  .card-question { font-size: 16px; }
  .card-hint { font-size: 12px; }
  
  /* Answer Options */
  .answer-option { 
    padding: 10px 14px; 
    font-size: 14px; 
    gap: 8px; 
  }
  
  /* Rating Section */
  .rating-prompt { font-size: 16px; margin-bottom: 16px; }
  .rating-buttons { 
    flex-direction: column;
    gap: 8px;
    width: 100%;
  }
  .rating-btn { 
    width: 100%;
    min-width: auto;
    flex-direction: row;
    justify-content: space-between;
    padding: 12px 16px;
  }
  .rating-icon { font-size: 24px; }
  .rating-text { font-size: 14px; }
  .rating-interval { font-size: 12px; }
}

/* Small Mobile 小螢幕手機 */
@media (max-width: 480px) {
  .container { padding: 8px; }
  .page-header h2 { font-size: 20px; }
  .flashcard { height: 280px; }
  .card-face { padding: 16px; }
  .card-question { font-size: 15px; }
  .stat-value { font-size: 20px; }
  .list-card-question { font-size: 13px; }
  .rating-btn { padding: 10px 14px; }
  .card-list-section { padding: 12px; }
}

/* Landscape Mobile 橫向手機 */
@media (max-width: 768px) and (orientation: landscape) {
  .flashcard { height: 250px; }
  .rating-buttons { 
    flex-direction: row;
    flex-wrap: wrap;
  }
  .rating-btn { 
    flex: 1;
    min-width: calc(50% - 4px);
  }
}
</style>

<template>
  <div class="flashcard-view">
    <div class="container">
      <header class="flashcard-header">
        <div>
          <h2>快閃卡複習系統</h2>
          <p>整合 SM-2 間隔重複演算法，提供個人化的複習節奏</p>
        </div>
        <button class="ghost-btn" @click="refreshAll" :disabled="isRefreshing">
          {{ isRefreshing ? '更新中...' : '重新整理' }}
        </button>
      </header>

      <transition name="fade">
        <div v-if="errorMessage" class="alert alert-error">{{ errorMessage }}</div>
      </transition>
      <transition name="fade">
        <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
      </transition>

      <section class="stats-grid">
        <article class="stat-card today">
          <div>
            <p class="label">今日待複習</p>
            <h3>{{ todayDueCount }}</h3>
            <small>完成率 {{ stats.completion_percent }}%</small>
          </div>
          <button class="primary-btn" @click="refreshDue" :disabled="isDueLoading">
            {{ isDueLoading ? '載入中...' : '立即複習' }}
          </button>
        </article>
        <article class="stat-card tomorrow">
          <div>
            <p class="label">明日預定</p>
            <h3>{{ tomorrowCount }}</h3>
          </div>
          <span class="helper-text">提前規劃，維持節奏</span>
        </article>
        <article class="stat-card week">
          <div>
            <p class="label">本週預定</p>
            <h3>{{ weekCount }}</h3>
          </div>
          <span class="helper-text">下次複習 {{ formattedNextReview }}</span>
        </article>
        <article class="stat-card streak" :class="{ active: stats.review_streak > 0 }">
          <div>
            <p class="label">連續複習天數</p>
            <h3>{{ stats.review_streak }}</h3>
          </div>
          <span class="helper-text">堅持就能累積成果</span>
        </article>
      </section>

      <section class="review-section">
        <div class="section-header">
          <div>
            <h3>待複習卡片</h3>
            <p class="section-subtitle">依照記憶強度選擇評分，系統會調整下次複習時間</p>
          </div>
        </div>
        <div v-if="isDueLoading" class="loading-state">載入待複習卡片中...</div>
        <div v-else-if="dueFlashcards.length === 0" class="empty-state">
          今日沒有待複習卡片，太棒了！
        </div>
        <div v-else class="review-list">
          <article v-for="card in dueFlashcards" :key="card.id" class="review-card">
            <div class="review-meta">
              <span class="badge">{{ card.question_subject }}</span>
              <span class="badge outline">{{ statusLabel(card.status) }}</span>
              <span class="badge outline">難度：{{ card.question_difficulty }}</span>
            </div>
            <p class="question" v-text="card.question_content"></p>
            <div class="review-actions">
              <button
                v-for="rating in ratings"
                :key="rating.value"
                class="rating-btn"
                :class="rating.variant"
                :disabled="reviewingCardId === card.id"
                @click="handleReview(card.id, rating.value)"
              >
                {{ rating.label }}
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="management-section">
        <div class="section-header">
          <div>
            <h3>快閃卡管理</h3>
            <p class="section-subtitle">快速建立、篩選並掌握整體進度</p>
          </div>
          <select v-model="statusFilter" class="select">
            <option value="all">全部狀態</option>
            <option value="learning">學習中</option>
            <option value="reviewing">複習中</option>
            <option value="mastered">已掌握</option>
            <option value="due">僅顯示待複習</option>
          </select>
        </div>

        <form class="create-form" @submit.prevent="handleCreate">
          <input
            type="number"
            min="1"
            class="input"
            placeholder="輸入題目 ID 建立快閃卡"
            v-model="questionIdInput"
          />
          <button class="primary-btn" type="submit" :disabled="isCreating">
            {{ isCreating ? '建立中...' : '建立新卡片' }}
          </button>
        </form>

        <div v-if="isListLoading" class="loading-state">載入快閃卡資料中...</div>
        <div v-else-if="flashcards.length === 0" class="empty-state">
          尚未找到符合條件的卡片
        </div>
        <div v-else class="card-list">
          <article v-for="card in flashcards" :key="card.id" class="card-item">
            <div>
              <h4>{{ card.question_subject }}</h4>
              <p class="question-snippet">{{ card.question_content }}</p>
              <div class="card-meta">
                <span>狀態：{{ statusLabel(card.status) }}</span>
                <span>下次複習：{{ formatDate(card.next_review_date) }}</span>
                <span>複習次數：{{ card.review_count }}</span>
              </div>
            </div>
            <button class="ghost-btn danger" @click="handleDelete(card.id)" :disabled="deletingCardId === card.id">
              {{ deletingCardId === card.id ? '刪除中...' : '刪除' }}
            </button>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import flashcardService from '@/services/flashcardService'

const stats = ref({
  total_cards: 0,
  due_cards: 0,
  completion_percent: 0,
  review_streak: 0,
  next_review_date: null
})
const flashcards = ref([])
const dueFlashcards = ref([])
const statusFilter = ref('all')
const questionIdInput = ref('')
const isListLoading = ref(false)
const isDueLoading = ref(false)
const isRefreshing = ref(false)
const isCreating = ref(false)
const deletingCardId = ref(null)
const reviewingCardId = ref(null)
const errorMessage = ref('')
const successMessage = ref('')

const ratings = [
  { value: 5, label: '很好記', variant: 'positive' },
  { value: 4, label: '還可以', variant: 'positive-light' },
  { value: 3, label: '差點忘記', variant: 'neutral' },
  { value: 2, label: '需要加強', variant: 'warning' },
  { value: 1, label: '完全忘記', variant: 'danger' }
]

const todayDueCount = computed(() => dueFlashcards.value.length)

const getDaysUntil = (dateString) => {
  if (!dateString) return Infinity
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(dateString)
  target.setHours(0, 0, 0, 0)
  return Math.round((target - today) / 86400000)
}

const tomorrowCount = computed(() =>
  flashcards.value.filter(card => getDaysUntil(card.next_review_date) === 1).length
)

const weekCount = computed(() =>
  flashcards.value.filter(card => {
    const diff = getDaysUntil(card.next_review_date)
    return diff >= 2 && diff <= 7
  }).length
)

const formattedNextReview = computed(() => stats.value.next_review_date || '尚無記錄')

const statusLabel = (status) => ({
  learning: '學習中',
  reviewing: '複習中',
  mastered: '已掌握'
}[status] || '未知')

const formatDate = (value) => {
  if (!value) return '尚未安排'
  return new Date(value).toLocaleDateString('zh-TW')
}

const showError = (message) => {
  errorMessage.value = message
  setTimeout(() => (errorMessage.value = ''), 5000)
}

const showSuccess = (message) => {
  successMessage.value = message
  setTimeout(() => (successMessage.value = ''), 3000)
}

const loadFlashcards = async () => {
  try {
    isListLoading.value = true
    const params = {}
    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value
    }
    flashcards.value = await flashcardService.getFlashcards(params)
  } catch (error) {
    showError(error.message)
  } finally {
    isListLoading.value = false
  }
}

const loadDueFlashcards = async () => {
  try {
    isDueLoading.value = true
    dueFlashcards.value = await flashcardService.getDueFlashcards()
  } catch (error) {
    showError(error.message)
  } finally {
    isDueLoading.value = false
  }
}

const loadStats = async () => {
  try {
    stats.value = await flashcardService.getStatistics()
  } catch (error) {
    showError(error.message)
  }
}

const refreshAll = async () => {
  try {
    isRefreshing.value = true
    await Promise.all([loadStats(), loadFlashcards(), loadDueFlashcards()])
  } finally {
    isRefreshing.value = false
  }
}

const refreshDue = async () => {
  await Promise.all([loadDueFlashcards(), loadStats()])
}

const handleReview = async (flashcardId, rating) => {
  try {
    reviewingCardId.value = flashcardId
    const updatedCard = await flashcardService.reviewFlashcard(flashcardId, rating)
    flashcards.value = flashcards.value.map(card => (card.id === updatedCard.id ? updatedCard : card))
    dueFlashcards.value = dueFlashcards.value.filter(card => card.id !== flashcardId)
    await loadStats()
    showSuccess('已記錄複習結果')
  } catch (error) {
    showError(error.message)
  } finally {
    reviewingCardId.value = null
  }
}

const handleCreate = async () => {
  if (!questionIdInput.value) {
    showError('請輸入題目 ID')
    return
  }

  try {
    isCreating.value = true
    await flashcardService.createFlashcard({ question: Number(questionIdInput.value) })
    questionIdInput.value = ''
    await Promise.all([loadFlashcards(), loadStats()])
    showSuccess('快閃卡建立成功')
  } catch (error) {
    showError(error.message)
  } finally {
    isCreating.value = false
  }
}

const handleDelete = async (cardId) => {
  if (!confirm('確定要刪除這張快閃卡嗎？')) return

  try {
    deletingCardId.value = cardId
    await flashcardService.deleteFlashcard(cardId)
    flashcards.value = flashcards.value.filter(card => card.id !== cardId)
    dueFlashcards.value = dueFlashcards.value.filter(card => card.id !== cardId)
    await loadStats()
    showSuccess('已刪除快閃卡')
  } catch (error) {
    showError(error.message)
  } finally {
    deletingCardId.value = null
  }
}

watch(statusFilter, loadFlashcards)
onMounted(refreshAll)
</script>

<style scoped>
.flashcard-view {
  background: #f5f6fa;
  min-height: 100vh;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}

.flashcard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.flashcard-header h2 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #1f2d3d;
}

.flashcard-header p {
  color: #65738e;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e5e7f1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.stat-card.today {
  border: 2px solid #ff6b6b;
  background: #fff5f5;
}

.stat-card.tomorrow {
  border: 2px solid #ffd166;
  background: #fff9e8;
}

.stat-card.week {
  border: 2px solid #51cf66;
  background: #f1fff3;
}

.stat-card.streak.active {
  border: 2px solid #2979ff;
  background: #e9f0ff;
}

.label {
  font-size: 14px;
  color: #6b7280;
}

.stat-card h3 {
  font-size: 32px;
  margin: 4px 0;
}

.helper-text,
.stat-card small {
  color: #708097;
}

.review-section,
.management-section {
  background: #fff;
  padding: 28px;
  border-radius: 16px;
  margin-bottom: 28px;
  border: 1px solid #e5e7f1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.section-header h3 {
  font-size: 22px;
  margin-bottom: 4px;
}

.section-subtitle {
  color: #7a869a;
  font-size: 14px;
}

.review-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.review-card {
  border: 1px solid #f0f2f8;
  border-radius: 12px;
  padding: 20px;
  background: #fcfdff;
}

.review-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  background: #edf2ff;
  color: #3d5af1;
}

.badge.outline {
  background: transparent;
  border: 1px solid #cad4f3;
  color: #56627c;
}

.question {
  font-size: 16px;
  color: #1f2d3d;
  margin-bottom: 16px;
  line-height: 1.5;
}

.review-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.rating-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.rating-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.rating-btn.positive {
  background: #d1f7c4;
  color: #216c2a;
}

.rating-btn.positive-light {
  background: #e5fdd1;
  color: #2f6b1f;
}

.rating-btn.neutral {
  background: #f1f5f9;
  color: #475569;
}

.rating-btn.warning {
  background: #fff3cd;
  color: #856404;
}

.rating-btn.danger {
  background: #ffe0e5;
  color: #b42318;
}

.create-form {
  display: flex;
  gap: 12px;
  margin: 16px 0 24px;
}

.card-list {
  display: grid;
  gap: 16px;
}

.card-item {
  border: 1px solid #edf0f7;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.question-snippet {
  color: #4b5563;
  line-height: 1.5;
  margin: 8px 0;
}

.card-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #6b7280;
}

.alert {
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 18px;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
}

.input,
.select {
  flex: 1;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d0d7ec;
  font-size: 14px;
}

.primary-btn,
.ghost-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
}

.primary-btn {
  background: #2563eb;
  color: #fff;
}

.ghost-btn {
  background: transparent;
  border: 1px solid #d4d9e8;
  color: #374151;
}

.ghost-btn.danger {
  border-color: #fca5a5;
  color: #b91c1c;
}

.loading-state,
.empty-state {
  padding: 24px;
  text-align: center;
  color: #6b7280;
  background: #f8fafc;
  border-radius: 12px;
  margin-top: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 970px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .flashcard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .create-form {
    flex-direction: column;
  }
}
</style>

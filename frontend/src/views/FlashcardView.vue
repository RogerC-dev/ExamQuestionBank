<template>
  <div class="flashcard-view">
    <div class="container">
      <!-- Review Mode -->
      <div v-if="reviewMode" class="review-mode">
        <ReviewHeader
          :current-index="currentIndex"
          :total-cards="reviewCards.length"
          @exit="exitReview"
        />

        <!-- Error message in review mode -->
        <div v-if="errorMessage" class="alert error review-alert" data-testid="review-error-alert">
          <span class="alert-message">{{ errorMessage }}</span>
          <div class="alert-actions">
            <button 
              v-if="errorRetryAction" 
              class="btn-retry" 
              @click="retryLastAction"
              data-testid="review-retry-button"
            >
              <i class="bi bi-arrow-clockwise"></i> 重試
            </button>
            <button 
              class="btn-dismiss" 
              @click="dismissError"
              data-testid="review-dismiss-button"
            >
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>

        <FlashcardDisplay
          v-if="currentCard"
          :card="currentCard"
          :options="currentOptions"
          :flipped="isFlipped"
          @flip="flipCard"
        />

        <RatingPanel
          :visible="isFlipped"
          :disabled="isRating"
          :current-interval="currentCard?.interval || 1"
          @rate="rateCard"
        />
      </div>

      <!-- Dashboard Mode -->
      <div v-else class="dashboard-mode">
        <header class="page-header">
          <h2><i class="bi bi-collection me-2"></i>快閃卡複習</h2>
        </header>

        <div v-if="errorMessage" class="alert error" data-testid="error-alert">
          <span class="alert-message">{{ errorMessage }}</span>
          <div class="alert-actions">
            <button 
              v-if="errorRetryAction" 
              class="btn-retry" 
              @click="retryLastAction"
              data-testid="retry-button"
            >
              <i class="bi bi-arrow-clockwise"></i> 重試
            </button>
            <button 
              class="btn-dismiss" 
              @click="dismissError"
              data-testid="dismiss-button"
            >
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>
        <div v-if="successMessage" class="alert success" data-testid="success-alert">{{ successMessage }}</div>

        <StatsGrid
          :stats="stats"
          :loading="isStatsLoading"
          @start-review="startReview"
        />

        <CardList
          ref="cardListRef"
          :cards="flashcards"
          :loading="isListLoading"
          :status-filter="statusFilter"
          @delete="handleDelete"
          @filter-change="handleFilterChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import flashcardService from '@/services/flashcardService'
import questionService from '@/services/questionService'
import { StatsGrid, CardList, FlashcardDisplay, RatingPanel, ReviewHeader } from '@/components/flashcard'

// Component refs
const cardListRef = ref(null)

// State
const stats = ref({ total_cards: 0, due_cards: 0, completion_percent: 0, review_streak: 0 })
const flashcards = ref([])
const dueFlashcards = ref([])
const statusFilter = ref('all')
const isListLoading = ref(false)
const isStatsLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Error handling state
const errorRetryAction = ref(null)
const errorDismissTimer = ref(null)

// Review mode state
const reviewMode = ref(false)
const reviewCards = ref([])
const currentIndex = ref(0)
const isFlipped = ref(false)
const isRating = ref(false)
const currentOptions = ref([])

const currentCard = computed(() => reviewCards.value[currentIndex.value])

const showError = (msg, retryAction = null) => {
  // Clear any existing timer
  if (errorDismissTimer.value) {
    clearTimeout(errorDismissTimer.value)
  }
  
  errorMessage.value = msg
  errorRetryAction.value = retryAction
  
  // Auto-dismiss after 4 seconds
  errorDismissTimer.value = setTimeout(() => {
    dismissError()
  }, 4000)
}

const dismissError = () => {
  errorMessage.value = ''
  errorRetryAction.value = null
  if (errorDismissTimer.value) {
    clearTimeout(errorDismissTimer.value)
    errorDismissTimer.value = null
  }
}

const retryLastAction = async () => {
  if (errorRetryAction.value) {
    const action = errorRetryAction.value
    dismissError()
    await action()
  }
}

const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => successMessage.value = '', 3000)
}

// Load data
const loadStats = async () => {
  try {
    isStatsLoading.value = true
    stats.value = await flashcardService.getStatistics()
  } catch (e) {
    showError(e.message, loadStats)
  } finally {
    isStatsLoading.value = false
  }
}

const loadFlashcards = async () => {
  try {
    isListLoading.value = true
    const params = statusFilter.value !== 'all' ? { status: statusFilter.value } : {}
    flashcards.value = await flashcardService.getFlashcards(params)
  } catch (e) {
    showError(e.message, loadFlashcards)
  } finally {
    isListLoading.value = false
  }
}

const loadDueFlashcards = async () => {
  try {
    dueFlashcards.value = await flashcardService.getDueFlashcards()
  } catch (e) {
    showError(e.message, loadDueFlashcards)
  }
}

// Review functions
const startReview = async () => {
  try {
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
  } catch (e) {
    showError(e.message, startReview)
  }
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
    // Create a retry function that captures the current rating
    const retryRating = () => rateCard(rating)
    showError(e.message, retryRating)
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
  try {
    await flashcardService.deleteFlashcard(id)
    flashcards.value = flashcards.value.filter(c => c.id !== id)
    loadStats()
    showSuccess('快閃卡已刪除')
  } catch (e) {
    // Create a retry function that captures the card id
    const retryDelete = () => handleDelete(id)
    showError(e.message, retryDelete)
  } finally {
    // Reset the deleting state in CardList component
    cardListRef.value?.resetDeletingState()
  }
}

const handleFilterChange = (status) => {
  statusFilter.value = status
}

watch(statusFilter, loadFlashcards)
onMounted(() => {
  loadStats()
  loadFlashcards()
})
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.alert-message {
  flex: 1;
}

.alert-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.alert.error {
  background: #fdf1f1;
  color: #9a1b1b;
  border: 1px solid #f3d6d6;
}

.alert.success {
  background: #ecf8f1;
  color: #1f6a3b;
  border: 1px solid #cef3e8;
}

.btn-retry {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(154, 27, 27, 0.1);
  border: 1px solid #9a1b1b;
  color: #9a1b1b;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-retry:hover {
  background: #9a1b1b;
  color: white;
}

.btn-dismiss {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  color: inherit;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.7;
  transition: all 0.2s;
}

.btn-dismiss:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

/* Review Mode */
.review-mode {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
}

.review-alert {
  margin: 0 0 16px 0;
}

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet */
@media (max-width: 1024px) {
  .container {
    padding: 16px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .container {
    padding: 12px;
  }

  .page-header h2 {
    font-size: 22px;
  }

  .page-header {
    margin-bottom: 20px;
  }

  .alert {
    flex-wrap: wrap;
    gap: 8px;
  }

  .alert-message {
    flex-basis: 100%;
  }

  .alert-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .btn-retry {
    padding: 8px 14px;
    font-size: 12px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .container {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 20px;
  }
}
</style>

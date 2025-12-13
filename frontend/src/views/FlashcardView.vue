<template>
  <div class="flashcard-view">
    <div class="container">
      <!-- Review Mode -->
      <div v-if="reviewMode" class="review-mode">
        <ReviewHeader :current-index="currentIndex" :total-cards="reviewCards.length" @exit="exitReview" />

        <!-- Error message in review mode -->
        <div v-if="errorMessage" class="alert error review-alert" data-testid="review-error-alert">
          <span class="alert-message">{{ errorMessage }}</span>
          <div class="alert-actions">
            <button v-if="errorRetryAction" class="btn-retry" @click="retryLastAction"
              data-testid="review-retry-button">
              <i class="bi bi-arrow-clockwise"></i> 重試
            </button>
            <button class="btn-dismiss" @click="dismissError" data-testid="review-dismiss-button">
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>

        <FlashcardDisplay v-if="currentCard" :card="currentCard" :options="currentOptions" :flipped="isFlipped"
          @flip="flipCard" />

        <RatingPanel :visible="isFlipped" :disabled="isRating" :current-interval="currentCard?.interval || 1"
          @rate="rateCard" />
      </div>

      <!-- Dashboard Mode -->
      <div v-else class="dashboard-mode">
        <header class="page-header">
          <h2><i class="bi bi-collection me-2"></i>快閃卡複習</h2>
        </header>

        <div v-if="errorMessage" class="alert error" data-testid="error-alert">
          <span class="alert-message">{{ errorMessage }}</span>
          <div class="alert-actions">
            <button v-if="errorRetryAction" class="btn-retry" @click="retryLastAction" data-testid="retry-button">
              <i class="bi bi-arrow-clockwise"></i> 重試
            </button>
            <button class="btn-dismiss" @click="dismissError" data-testid="dismiss-button">
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>
        <div v-if="successMessage" class="alert success" data-testid="success-alert">{{ successMessage }}</div>

        <StatsGrid :stats="stats" :loading="isStatsLoading" @start-review="startReview" />

        <CardList ref="cardListRef" :cards="flashcards" :loading="isListLoading" :status-filter="statusFilter"
          :selected-ids="selectedFlashcardIds" @delete="handleDelete" @filter-change="handleFilterChange"
          @selection-change="handleSelectionChange" />

        <!-- Selection Toolbar (Sticky) -->
        <transition name="slide-up">
          <div class="selection-toolbar-wrapper" v-if="selectedFlashcardCount > 0">
            <div class="selection-toolbar">
              <div class="toolbar-content">
                <div class="toolbar-info">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="9 11 12 14 22 4"></polyline>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                  </svg>
                  <span class="toolbar-text">已選取</span>
                  <span class="toolbar-count">{{ selectedFlashcardCount }}</span>
                  <span class="toolbar-text">張快閃卡</span>
                </div>

                <div class="toolbar-divider"></div>

                <div class="toolbar-actions">
                  <button class="toolbar-btn toolbar-btn-secondary" @click="clearSelection" title="清除選取">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                    <span>清除</span>
                  </button>

                  <div class="toolbar-divider"></div>

                  <button class="toolbar-btn toolbar-btn-danger" @click="deleteSelectedFlashcards"
                    :disabled="isDeletingSelected" title="批量刪除">
                    <div v-if="isDeletingSelected" class="toolbar-spinner"></div>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                      fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                    <span>{{ isDeletingSelected ? '刪除中...' : '刪除' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition>
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

// Selection state
const selectedFlashcardIds = ref([])
const isDeletingSelected = ref(false)

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
const selectedFlashcardCount = computed(() => selectedFlashcardIds.value.length)

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

const handleSelectionChange = (selectedIds) => {
  selectedFlashcardIds.value = selectedIds
}

const clearSelection = () => {
  selectedFlashcardIds.value = []
}

const deleteSelectedFlashcards = async () => {
  if (selectedFlashcardIds.value.length === 0) return

  const confirmMessage = `確定要刪除選取的 ${selectedFlashcardIds.value.length} 張快閃卡嗎？此操作無法復原。`
  if (!confirm(confirmMessage)) return

  isDeletingSelected.value = true
  const idsToDelete = [...selectedFlashcardIds.value]
  let successCount = 0
  let failCount = 0

  for (const id of idsToDelete) {
    try {
      await flashcardService.deleteFlashcard(id)
      flashcards.value = flashcards.value.filter(c => c.id !== id)
      successCount++
      // Remove from selection
      const index = selectedFlashcardIds.value.indexOf(id)
      if (index > -1) {
        selectedFlashcardIds.value.splice(index, 1)
      }
    } catch (e) {
      console.error(`Failed to delete flashcard ${id}`, e)
      failCount++
    }
  }

  isDeletingSelected.value = false

  // Show result
  if (failCount === 0) {
    showSuccess(`成功刪除 ${successCount} 張快閃卡`)
  } else {
    showError(`刪除完成：成功 ${successCount} 張，失敗 ${failCount} 張`)
  }

  // Refresh stats
  loadStats()
  // Reset deleting state in CardList component
  cardListRef.value?.resetDeletingState()
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

/* Selection Toolbar */
.selection-toolbar-wrapper {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: calc(100% - 48px);
  max-width: 900px;
}

.selection-toolbar {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border, #CBD5E1);
}

.toolbar-content {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  gap: 16px;
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: var(--primary-soft, #EEF2FF);
  border-radius: 10px;
}

.toolbar-info svg {
  color: var(--primary, #476996);
  flex-shrink: 0;
}

.toolbar-text {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
  font-weight: 500;
}

.toolbar-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 10px;
  background: var(--primary, #476996);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.toolbar-divider {
  width: 1px;
  height: 32px;
  background: #e5e7eb;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.toolbar-btn svg {
  flex-shrink: 0;
}

.toolbar-btn-secondary {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.toolbar-btn-secondary:hover {
  background: #e5e7eb;
  color: var(--text-primary, #1E293B);
  transform: translateY(-1px);
}

.toolbar-btn-danger {
  background: #fef2f2;
  color: #dc2626;
}

.toolbar-btn-danger:hover:not(:disabled) {
  background: #fee2e2;
  color: #b91c1c;
  transform: translateY(-1px);
}

.toolbar-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toolbar-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(220, 38, 38, 0.3);
  border-top-color: #dc2626;
  border-radius: 50%;
  animation: toolbar-spin 0.8s linear infinite;
}

@keyframes toolbar-spin {
  to {
    transform: rotate(360deg);
  }
}

/* Slide up animation */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
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

  .selection-toolbar-wrapper {
    width: calc(100% - 24px);
  }

  .toolbar-content {
    flex-wrap: wrap;
    padding: 12px 16px;
  }

  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .toolbar-btn span {
    display: none;
  }

  .toolbar-btn {
    padding: 8px 12px;
  }

  .toolbar-divider {
    display: none;
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

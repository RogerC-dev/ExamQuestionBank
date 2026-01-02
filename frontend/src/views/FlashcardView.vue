<template>
  <div class="flashcard-view">
    <div class="container">
      <!-- Review Mode -->
      <div v-if="reviewMode" class="review-mode">
        <!-- Simple Review Header -->
        <div class="review-header" data-testid="review-header">
          <div class="progress-info">
            <span class="progress-text" data-testid="progress-text">{{ swiperActiveIndex + 1 }} / {{ reviewCards.length
            }}</span>
            <div class="progress-bar" data-testid="progress-bar">
              <div class="progress-fill" data-testid="progress-fill" :style="{ width: progressWidth + '%' }"></div>
            </div>
          </div>
          <button class="btn-exit" data-testid="exit-button" @click="exitReview">
            <i class="bi bi-x-lg"></i>
            <span>結束</span>
          </button>
        </div>

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

        <!-- Swiper with Cards Effect for all flashcards -->
        <div class="flashcard-swiper-container">
          <Swiper v-if="reviewCards.length > 0" :modules="swiperModules" :effect="'cards'" :grabCursor="isPracticeMode"
            :cardsEffect="{
              perSlideOffset: 8,
              perSlideRotate: 2,
              rotate: true,
              slideShadows: false,
            }" :allowTouchMove="isPracticeMode" :virtual="{
              enabled: true,
              addSlidesAfter: 2,
              addSlidesBefore: 2,
            }" :preloadImages="false" class="flashcard-swiper" @swiper="onSwiperInit" @slideChange="onSlideChange">
            <SwiperSlide v-for="(card, index) in reviewCards" :key="card.id" :virtualIndex="index">
              <FlashcardDisplay :ref="el => setCardRef(el, index)" :card="card" :options="cardOptions[card.id] || []"
                @flip="handleCardFlip(index)" />
            </SwiperSlide>
          </Swiper>
        </div>

        <RatingPanel :visible="isCardFlipped && swiperActiveIndex < reviewCards.length" :disabled="isRating"
          :current-interval="currentCard?.interval || 1" :practice-mode="isPracticeMode" @rate="rateCard" />
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

        <CardList ref="cardListRef" :cards="paginatedFlashcards" :loading="isListLoading" :status-filter="statusFilter"
          :selected-ids="selectedFlashcardIds" @delete="handleDelete" @filter-change="handleFilterChange"
          @selection-change="handleSelectionChange" />

        <!-- Selection Toolbar (Sticky) -->
        <SelectionToolbar :selected-count="selectedFlashcardCount" item-unit="張快閃卡" @clear="clearSelection">
          <div class="toolbar-divider"></div>

          <button class="toolbar-btn toolbar-btn-info" @click="startPracticeSelected" title="練習選取項目">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
            </svg>
            <span>練習選取</span>
          </button>

          <button class="toolbar-btn toolbar-btn-danger" @click="deleteSelectedFlashcards"
            :disabled="isDeletingSelected" title="批量刪除">
            <div v-if="isDeletingSelected" class="toolbar-spinner"></div>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            <span>{{ isDeletingSelected ? '刪除中...' : '刪除' }}</span>
          </button>
        </SelectionToolbar>

        <!-- Pagination -->
        <PaginationControl v-if="!isListLoading && allFlashcards.length > 0" :pagination-state="paginationState"
          :current-page="currentPage" :page-size="pageSize" :is-loading="isListLoading" @page-change="handlePageChange"
          @size-change="handleSizeChange" class="mt-4" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { EffectCards, Virtual } from 'swiper/modules'
import flashcardService from '@/services/flashcardService'
import questionService from '@/services/questionService'
import { StatsGrid, CardList, FlashcardDisplay, RatingPanel } from '@/components/flashcard'
import SelectionToolbar from '@/components/common/SelectionToolbar.vue'
import PaginationControl from '@/components/common/PaginationControl.vue'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/effect-cards'

// Component refs
const cardListRef = ref(null)
const cardRefs = ref([])
const swiperInstance = ref(null)

// Swiper modules
const swiperModules = [EffectCards, Virtual]

// State
const stats = ref({ total_cards: 0, due_cards: 0, completion_percent: 0, review_streak: 0 })
const dueFlashcards = ref([])
const statusFilter = ref('all')
const isListLoading = ref(false)

// Pagination state (client-side)
const currentPage = ref(1)
const pageSize = ref(20)
const allFlashcards = ref([])

// Computed: paginated flashcards for display
const paginatedFlashcards = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allFlashcards.value.slice(start, end)
})

// Computed: pagination state for the control
const paginationState = computed(() => {
  const total = allFlashcards.value.length
  return {
    hasNext: currentPage.value * pageSize.value < total,
    hasPrev: currentPage.value > 1,
    totalPages: Math.ceil(total / pageSize.value) || 1,
    totalCount: total
  }
})

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
const swiperActiveIndex = ref(0)
const isCardFlipped = ref(false)
const isRating = ref(false)
const isPracticeMode = ref(false)
const cardOptions = ref({}) // Store options for each card by card.id

const currentCard = computed(() => reviewCards.value[swiperActiveIndex.value])
const selectedFlashcardCount = computed(() => selectedFlashcardIds.value.length)
const progressWidth = computed(() => {
  if (reviewCards.value.length === 0) return 0
  return ((swiperActiveIndex.value + 1) / reviewCards.value.length) * 100
})

// Set card ref
const setCardRef = (el, index) => {
  if (el) {
    cardRefs.value[index] = el
  }
}

// Load state tracking
const fetchedCardIds = ref(new Set())

// Swiper event handlers
const onSwiperInit = (swiper) => {
  swiperInstance.value = swiper
  loadSurroundingOptions(swiper.activeIndex)
}

const onSlideChange = () => {
  if (swiperInstance.value) {
    swiperActiveIndex.value = swiperInstance.value.activeIndex
    isCardFlipped.value = false
    loadSurroundingOptions(swiperActiveIndex.value)
  }
}

// Handle card flip
const handleCardFlip = (index) => {
  if (index === swiperActiveIndex.value) {
    isCardFlipped.value = true
  }
}

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
    allFlashcards.value = await flashcardService.getFlashcards(params)
    currentPage.value = 1 // Reset to first page on reload
  } catch (e) {
    showError(e.message, loadFlashcards)
  } finally {
    isListLoading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const loadDueFlashcards = async () => {
  try {
    dueFlashcards.value = await flashcardService.getDueFlashcards()
  } catch (e) {
    showError(e.message, loadDueFlashcards)
  }
}

const loadSurroundingOptions = async (currentIndex) => {
  // Load current card and next 2 cards
  for (let i = 0; i < 3; i++) {
    const targetIndex = currentIndex + i
    if (targetIndex >= reviewCards.value.length) continue

    const card = reviewCards.value[targetIndex]

    // Skip if already fetched or currently fetching (we can use the set)
    if (fetchedCardIds.value.has(card.id)) continue

    // Mark as fetched/fetching to prevent duplicate requests
    fetchedCardIds.value.add(card.id)

    try {
      // Non-blocking fetch (don't await loop iteration)
      questionService.getQuestion(card.question).then(({ data }) => {
        cardOptions.value = {
          ...cardOptions.value,
          [card.id]: data.options || []
        }
      }).catch(() => {
        cardOptions.value = {
          ...cardOptions.value,
          [card.id]: []
        }
      })
    } catch (e) {
      console.error(e)
    }
  }
}

// Review functions
const startReview = async (isPractice = false) => {
  try {
    isPracticeMode.value = isPractice

    if (isPractice) {
      if (allFlashcards.value.length === 0) {
        showError('沒有可供複習的卡片')
        return
      }
      reviewCards.value = [...allFlashcards.value]
    } else {
      await loadDueFlashcards()
      if (dueFlashcards.value.length === 0) {
        showError('沒有待複習的卡片')
        return
      }
      reviewCards.value = [...dueFlashcards.value]
    }

    swiperActiveIndex.value = 0
    isCardFlipped.value = false
    cardRefs.value = []
    fetchedCardIds.value.clear()
    cardOptions.value = {}

    reviewMode.value = true
  } catch (e) {
    showError(e.message, () => startReview(isPractice))
  }
}

const startPracticeSelected = async () => {
  if (selectedFlashcardIds.value.length === 0) return

  try {
    isPracticeMode.value = true

    // Filter currently loaded flashcards by selection
    const selectedCards = allFlashcards.value.filter(card =>
      selectedFlashcardIds.value.includes(card.id)
    )

    if (selectedCards.length === 0) {
      showError('無法載入選取的卡片')
      return
    }

    reviewCards.value = selectedCards
    swiperActiveIndex.value = 0
    isCardFlipped.value = false
    cardRefs.value = []
    fetchedCardIds.value.clear()
    cardOptions.value = {}

    reviewMode.value = true
  } catch (e) {
    showError(e.message, startPracticeSelected)
  }
}



const rateCard = async (rating) => {
  if (!currentCard.value || isRating.value) return
  isRating.value = true

  try {
    // Only call API if not in practice mode and rating > 0
    if (!isPracticeMode.value && rating > 0) {
      await flashcardService.reviewFlashcard(currentCard.value.id, rating)
    }

    // Check if there are more cards
    if (swiperActiveIndex.value < reviewCards.value.length - 1) {
      // Move to next card
      isCardFlipped.value = false
      if (swiperInstance.value) {
        swiperInstance.value.slideNext()
      }
    } else {
      // Finished all cards
      showSuccess(isPracticeMode.value
        ? `🎉 完成！練習了 ${reviewCards.value.length} 張卡片`
        : `🎉 完成！複習了 ${reviewCards.value.length} 張卡片`
      )
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
  swiperActiveIndex.value = 0
  isCardFlipped.value = false
  cardOptions.value = {}
  cardRefs.value = []
  swiperInstance.value = null
  loadStats()
  loadFlashcards()
}

// CRUD
const handleDelete = async (id) => {
  try {
    await flashcardService.deleteFlashcard(id)
    allFlashcards.value = allFlashcards.value.filter(c => c.id !== id)
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
      allFlashcards.value = allFlashcards.value.filter(c => c.id !== id)
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
  max-width: 1200px;
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

/* Review Header */
.review-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

.progress-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-text {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  min-width: 70px;
  white-space: nowrap;
}

.progress-bar {
  flex: 1;
  height: 10px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #476996 0%, #35527a 100%);
  border-radius: 10px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(71, 105, 150, 0.4);
}

.btn-exit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  color: #64748b;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-exit:hover {
  background: #EEF2FF;
  border-color: #476996;
  color: #476996;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.2);
}

.btn-exit:active {
  transform: translateY(0);
}

.review-alert {
  margin: 0 0 16px 0;
}

.flashcard-swiper {
  width: 100%;
  height: 600px;
  padding: 60px 30px;
}

.selection-toolbar-wrapper {
  bottom: 100px;
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

  .review-header {
    flex-wrap: wrap;
    padding: 16px;
    gap: 12px;
  }

  .progress-info {
    width: 100%;
    order: 2;
  }

  .btn-exit {
    padding: 8px 16px;
    font-size: 14px;
  }

  .btn-exit span {
    display: none;
  }

  .flashcard-swiper-container {
    padding: 20px;
    max-width: 100%;
  }

  .flashcard-swiper {
    height: 500px;
    padding: 40px 20px;
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

/* Toolbar Info Button */
.toolbar-btn-info {
  background: #e0f2fe;
  color: #0369a1;
}

.toolbar-btn-info:hover {
  background: #bae6fd;
  color: #0284c7;
  transform: translateY(-1px);
}

/* Dark Mode Overrides */
:global(.dark) .stat-card,
:global(.dark) .stats-section,
:global(.dark) .exam-info,
:global(.dark) .review-header {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

:global(.dark) .toolbar-btn-info {
    background: var(--primary-soft) !important;
    color: var(--primary) !important;
}

:global(.dark) .flashcard-swiper-container {
    background: var(--bg-page) !important;
}

:global(.dark) .rating-btn {
    background: var(--surface-muted) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

:global(.dark) .rating-btn:hover {
    background: var(--primary-soft) !important;
    border-color: var(--primary) !important;
}
</style>

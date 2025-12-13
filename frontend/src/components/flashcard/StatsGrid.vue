<template>
  <div class="stats-grid" data-testid="stats-grid">
    <!-- Primary card: Due cards with start review button -->
    <div class="stat-card primary" data-testid="stat-card-due">
      <div class="stat-icon"><i class="bi bi-book"></i></div>
      <div class="stat-info">
        <span v-if="loading" class="stat-value loading-indicator" data-testid="loading-indicator">
          <span class="loading-spinner"></span>
        </span>
        <span v-else class="stat-value" data-testid="due-cards-value">{{ stats.due_cards }}</span>
        <span class="stat-label">今日待複習</span>
      </div>
      <button v-if="stats.due_cards > 0" class="btn-start" data-testid="start-review-button"
        @click="$emit('start-review', false)" :disabled="loading">
        開始複習 →
      </button>
    </div>

    <!-- Total cards -->
    <div class="stat-card" data-testid="stat-card-total">
      <div class="stat-icon"><i class="bi bi-bullseye"></i></div>
      <div class="stat-info">
        <span v-if="loading" class="stat-value loading-indicator" data-testid="loading-indicator">
          <span class="loading-spinner"></span>
        </span>
        <span v-else class="stat-value" data-testid="total-cards-value">{{ stats.total_cards }}</span>
        <span class="stat-label">總卡片數</span>
      </div>
      <button v-if="stats.total_cards > 0" class="btn-secondary-action" data-testid="practice-all-button"
        @click="$emit('start-review', true)" :disabled="loading">
        <i class="bi bi-play-circle me-1"></i>練習全部
      </button>
    </div>

    <!-- Review streak -->
    <div class="stat-card" data-testid="stat-card-streak">
      <div class="stat-icon"><i class="bi bi-fire"></i></div>
      <div class="stat-info">
        <span v-if="loading" class="stat-value loading-indicator" data-testid="loading-indicator">
          <span class="loading-spinner"></span>
        </span>
        <span v-else class="stat-value" data-testid="review-streak-value">{{ stats.review_streak }}</span>
        <span class="stat-label">連續天數</span>
      </div>
    </div>

    <!-- Completion percentage -->
    <div class="stat-card" data-testid="stat-card-completion">
      <div class="stat-icon"><i class="bi bi-check-circle-fill"></i></div>
      <div class="stat-info">
        <span v-if="loading" class="stat-value loading-indicator" data-testid="loading-indicator">
          <span class="loading-spinner"></span>
        </span>
        <span v-else class="stat-value" data-testid="completion-percent-value">{{ stats.completion_percent }}%</span>
        <span class="stat-label">完成率</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FlashcardStats } from '@/types/flashcard'

interface Props {
  stats: FlashcardStats
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false
})

defineEmits<{
  (e: 'start-review', isPracticeMode: boolean): void
}>()
</script>

<style scoped>
/* Stats Grid Layout */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 30px;
}

/* Stat Card Base Styles */
.stat-card {
  background: var(--surface, #ffffff);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border, #e2e8f0);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  color: var(--primary, #3b82f6);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

/* Primary Card (Due Cards) */
.stat-card.primary {
  background: var(--primary, #3b82f6);
  color: white;
  border: none;
}

.stat-card.primary:hover {
  background: var(--primary-hover, #2563eb);
}

/* Icon Styles */
.stat-icon {
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Info Section */
.stat-info {
  text-align: center;
  width: 100%;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: inherit;
  min-height: 34px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
  color: inherit;
  display: block;
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  opacity: 0.6;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Start Review Button */
.btn-start {
  margin-top: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
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

.btn-start:hover:not(:disabled) {
  background: white;
  color: var(--primary, #3b82f6);
}

.btn-start:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-start:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary-action {
  margin-top: 8px;
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--primary, #3b82f6);
  color: var(--primary, #3b82f6);
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.btn-secondary-action:hover:not(:disabled) {
  background: var(--primary-soft, #EEF2FF);
  transform: translateY(-1px);
}

.btn-secondary-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive Design - Tablet */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    font-size: 28px;
  }

  .stat-value {
    font-size: 24px;
  }
}

/* Responsive Design - Mobile */
@media (max-width: 768px) {
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

  .stat-icon {
    font-size: 24px;
  }

  .stat-info {
    text-align: left;
  }

  .stat-card.primary .stat-info {
    text-align: center;
  }

  .stat-value {
    font-size: 22px;
    min-height: 27px;
  }

  .stat-label {
    font-size: 12px;
  }

  .btn-start {
    width: 100%;
    max-width: none;
  }

  .loading-spinner {
    width: 20px;
    height: 20px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .stat-value {
    font-size: 20px;
    min-height: 25px;
  }
}
</style>

<template>
  <div class="card-list-section">
    <div class="list-header">
      <div class="list-header-left">
        <input v-if="cards.length > 0" type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
          class="select-all-checkbox" aria-label="選取全部" />
        <h3>我的快閃卡 ({{ cards.length }})</h3>
      </div>
      <select :value="statusFilter" @change="$emit('filter-change', ($event.target as HTMLSelectElement).value)">
        <option value="all">全部</option>
        <option value="learning">學習中</option>
        <option value="reviewing">複習中</option>
        <option value="mastered">已掌握</option>
      </select>
    </div>
    <div v-if="loading" class="loading">載入中...</div>
    <div v-else-if="cards.length === 0" class="empty">
      <p>尚無快閃卡</p>
      <p class="hint">從練習頁面的錯題本或收藏題目加入快閃卡</p>
    </div>
    <div v-else class="card-list">
      <div v-for="card in cards" :key="card.id" class="list-card">
        <input type="checkbox" :checked="isCardSelected(card.id)"
          @change="toggleCardSelection(card.id, ($event.target as HTMLInputElement).checked)" class="card-checkbox"
          :disabled="deletingId === card.id" aria-label="選取快閃卡" />
        <div class="list-card-content">
          <span class="list-card-subject">{{ card.question_subject }}</span>
          <p class="list-card-question">{{ card.question_content }}</p>
          <div class="list-card-meta">
            <span :class="'status-' + card.status">{{ statusLabel(card.status) }}</span>
            <span>下次：{{ formatDate(card.next_review_date) }}</span>
            <span>複習 {{ card.review_count }} 次</span>
          </div>
        </div>
        <button class="btn-delete" @click="confirmDelete(card)" :disabled="deletingId === card.id">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="delete-modal-overlay" @click.self="cancelDelete">
      <div class="delete-modal">
        <h4>確認刪除</h4>
        <p>確定要刪除這張快閃卡嗎？</p>
        <p class="delete-card-preview" v-if="cardToDelete">{{ cardToDelete.question_content }}</p>
        <div class="delete-modal-actions">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-confirm-delete" @click="executeDelete" :disabled="deletingId !== null">
            {{ deletingId !== null ? '刪除中...' : '確認刪除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Flashcard, StatusFilter } from '@/types/flashcard'

interface Props {
  cards: Flashcard[]
  loading?: boolean
  statusFilter?: StatusFilter
  selectedIds?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  statusFilter: 'all',
  selectedIds: () => []
})

const emit = defineEmits<{
  (e: 'delete', cardId: number): void
  (e: 'filter-change', status: string): void
  (e: 'selection-change', selectedIds: number[]): void
}>()

const deletingId = ref<number | null>(null)
const showDeleteConfirm = ref(false)
const cardToDelete = ref<Flashcard | null>(null)

const statusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    learning: '學習中',
    reviewing: '複習中',
    mastered: '已掌握'
  }
  return labels[status] || status
}

const formatDate = (date: string | null): string => {
  return date ? new Date(date).toLocaleDateString('zh-TW') : '未排定'
}

const confirmDelete = (card: Flashcard) => {
  cardToDelete.value = card
  showDeleteConfirm.value = true
}

const cancelDelete = () => {
  showDeleteConfirm.value = false
  cardToDelete.value = null
}

const executeDelete = () => {
  if (cardToDelete.value) {
    deletingId.value = cardToDelete.value.id
    emit('delete', cardToDelete.value.id)
    showDeleteConfirm.value = false
    cardToDelete.value = null
  }
}

// Selection management
const isCardSelected = (cardId: number): boolean => {
  return props.selectedIds.includes(cardId)
}

const toggleCardSelection = (cardId: number, checked: boolean) => {
  let newSelection: number[]
  if (checked) {
    newSelection = [...props.selectedIds, cardId]
  } else {
    newSelection = props.selectedIds.filter(id => id !== cardId)
  }
  emit('selection-change', newSelection)
}

const isAllSelected = computed(() => {
  if (props.cards.length === 0) return false
  return props.cards.every(card => props.selectedIds.includes(card.id))
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    // Deselect all
    emit('selection-change', [])
  } else {
    // Select all on current page
    const allIds = props.cards.map(card => card.id)
    emit('selection-change', allIds)
  }
}

// Expose method to reset deleting state (called by parent after delete completes)
defineExpose({
  resetDeletingState: () => {
    deletingId.value = null
  }
})
</script>

<style scoped>
.card-list-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.list-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.select-all-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #1976d2;
}

.list-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.list-header select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty .hint {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.5rem;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.list-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.2s;
  gap: 0.75rem;
}

.card-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
  accent-color: #1976d2;
}

.card-checkbox:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.list-card:hover {
  background: #f0f0f0;
}

.list-card-content {
  flex: 1;
  min-width: 0;
}

.list-card-subject {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.list-card-question {
  margin: 0 0 0.5rem 0;
  font-size: 0.95rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-card-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #666;
}

.list-card-meta .status-learning {
  color: #f57c00;
}

.list-card-meta .status-reviewing {
  color: #1976d2;
}

.list-card-meta .status-mastered {
  color: #388e3c;
}

.btn-delete {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-delete:hover:not(:disabled) {
  background: #ffebee;
  color: #d32f2f;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Delete Confirmation Modal */
.delete-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.delete-modal {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.delete-modal h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.delete-modal p {
  margin: 0 0 0.5rem 0;
  color: #666;
}

.delete-card-preview {
  background: #f5f5f5;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  margin: 1rem 0 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm-delete {
  padding: 0.6rem 1.2rem;
  background: #d32f2f;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: white;
  transition: background 0.2s;
}

.btn-confirm-delete:hover:not(:disabled) {
  background: #b71c1c;
}

.btn-confirm-delete:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet */
@media (max-width: 1024px) {
  .card-list-section {
    padding: 1.25rem;
  }

  .list-header h3 {
    font-size: 1rem;
  }

  .list-card {
    padding: 0.875rem;
  }

  .list-card-meta {
    gap: 0.75rem;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .card-list-section {
    padding: 1rem;
    border-radius: 10px;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .list-header h3 {
    font-size: 1rem;
    text-align: center;
  }

  .list-header select {
    width: 100%;
    padding: 0.6rem 1rem;
  }

  .list-card {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    padding: 0.875rem;
  }

  .list-card-content {
    width: 100%;
  }

  .list-card-question {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .list-card-meta {
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.75rem;
  }

  .btn-delete {
    align-self: flex-end;
    padding: 0.6rem 1rem;
    background: #ffebee;
    color: #d32f2f;
    border-radius: 6px;
  }

  /* Delete Modal Mobile */
  .delete-modal {
    padding: 1.25rem;
    width: 95%;
  }

  .delete-modal h4 {
    font-size: 1rem;
  }

  .delete-modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }

  .btn-cancel,
  .btn-confirm-delete {
    width: 100%;
    padding: 0.75rem;
    text-align: center;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .card-list-section {
    padding: 0.75rem;
  }

  .list-card {
    padding: 0.75rem;
  }

  .list-card-subject {
    font-size: 0.7rem;
  }

  .list-card-question {
    font-size: 0.9rem;
  }

  .list-card-meta {
    font-size: 0.7rem;
  }
}
</style>

<template>
  <div class="question-list">
    <div class="list-header">
      <div class="header-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
        </svg>
      </div>
      <div class="header-content">
        <h3 class="list-title">題目列表</h3>
        <p class="list-subtitle">管理目前考卷的所有題目與配分</p>
      </div>

      <div class="header-actions">
        <button class="action-btn action-btn-secondary" @click="$emit('add-existing-question')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          從題庫加入
        </button>
        <button class="action-btn action-btn-primary" @click="$emit('add-question')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          新增題目
        </button>
      </div>
    </div>

    <div class="search-bar">
      <div class="search-control">
        <input
          type="checkbox"
          :checked="isAllSelected"
          :indeterminate.prop="isPartialSelected"
          @change="toggleSelectAll"
          class="select-all-checkbox"
          title="全選/取消全選"
        />
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋題目內容、科目、分類..."
          class="search-input"
        />
        <span v-if="selectedIds.length > 0" class="selection-badge">
          已選 {{ selectedIds.length }} 題
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>載入中...</p>
    </div>

    <div v-else-if="filteredQuestions.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="empty-icon">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
        <line x1="12" y1="17" x2="12.01" y2="17"></line>
      </svg>
      <p class="empty-text">{{ searchQuery ? '沒有符合的題目' : '尚未加入任何題目' }}</p>
      <p v-if="!searchQuery" class="empty-hint">點擊上方按鈕開始新增題目</p>
    </div>

    <div v-else class="questions">
      <QuestionItem
        v-for="item in filteredQuestions"
        :key="item.id"
        :item="item"
        :is-active="selectedQuestionId === item.question"
        :has-pending-edit="Boolean(pendingEdits[item.id])"
        :is-checked="selectedIds.includes(item.id)"
        :show-checkbox="true"
        @select="selectQuestion"
        @remove="(id) => $emit('remove-question', id)"
        @toggle-check="toggleCheck"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import QuestionItem from './QuestionItem.vue'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  selectedQuestionId: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  totalPoints: {
    type: Number,
    default: 100
  },
  autoDistributeLoading: {
    type: Boolean,
    default: false
  },
  showAutoDistribute: {
    type: Boolean,
    default: true
  },
  pendingEdits: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits([
  'select-question',
  'add-question',
  'add-existing-question',
  'remove-question',
  'auto-distribute',
  'update:total-points',
  'update:selected-ids'
])

const searchQuery = ref('')
const selectedIds = ref([])

const filteredQuestions = computed(() => {
  let questions = props.questions
  questions = [...questions].sort((a, b) => (a.order || 0) - (b.order || 0))
  if (!searchQuery.value) return questions

  const query = searchQuery.value.toLowerCase()
  return questions.filter(item => {
    return (
      item.question_content?.toLowerCase().includes(query) ||
      item.question_subject?.toLowerCase().includes(query) ||
      item.question_category?.toLowerCase().includes(query)
    )
  })
})

const isAllSelected = computed(() => {
  return filteredQuestions.value.length > 0 && 
    filteredQuestions.value.every(q => selectedIds.value.includes(q.id))
})

const isPartialSelected = computed(() => {
  const selected = filteredQuestions.value.filter(q => selectedIds.value.includes(q.id))
  return selected.length > 0 && selected.length < filteredQuestions.value.length
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredQuestions.value.map(q => q.id)
  }
  emit('update:selected-ids', selectedIds.value)
}

const toggleCheck = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(idx, 1)
  }
  emit('update:selected-ids', selectedIds.value)
}

const selectQuestion = (item) => {
  emit('select-question', item)
}

watch(() => props.questions, () => {
  // 清除已不存在的選取項
  selectedIds.value = selectedIds.value.filter(id => 
    props.questions.some(q => q.id === id)
  )
})

defineExpose({ selectedIds })
</script>

<style scoped>
.question-list {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border, #CBD5E1);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.list-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 2px solid var(--border, #CBD5E1);
  background: var(--bg-page, #F8FAFC);
}

.header-icon {
  width: 44px;
  height: 44px;
  background: var(--primary, #476996);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.header-content {
  flex: 1;
}

.list-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  letter-spacing: -0.01em;
}

.list-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-secondary, #64748B);
  line-height: 1.5;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-btn-primary {
  background: var(--primary, #476996);
  color: white;
}

.action-btn-primary:hover {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(71, 105, 150, 0.25);
}

.action-btn-secondary {
  background: white;
  color: var(--text-primary, #1E293B);
  border: 2px solid var(--border, #CBD5E1);
}

.action-btn-secondary:hover {
  border-color: var(--primary, #476996);
  background: var(--primary-soft, #EEF2FF);
  color: var(--primary, #476996);
}

/* Search Bar */
.search-bar {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border, #CBD5E1);
  background: white;
}

.search-control {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-page, #F8FAFC);
  border: 2px solid var(--border, #CBD5E1);
  border-radius: 12px;
  padding: 10px 14px;
  transition: all 0.2s ease;
}

.search-control:focus-within {
  border-color: var(--primary, #476996);
  background: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.select-all-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin: 0;
  flex-shrink: 0;
}

.search-icon {
  color: var(--text-secondary, #64748B);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary, #1E293B);
  outline: none;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--text-secondary, #64748B);
}

.selection-badge {
  padding: 6px 12px;
  background: var(--primary, #476996);
  color: white;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Questions List */
.questions {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--bg-page, #F8FAFC);
}

/* Loading State */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  color: var(--text-secondary, #64748B);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border, #CBD5E1);
  border-top-color: var(--primary, #476996);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  text-align: center;
}

.empty-icon {
  color: var(--border, #CBD5E1);
  margin-bottom: 20px;
}

.empty-text {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #1E293B);
}

.empty-hint {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

/* Scrollbar Styling */
.questions::-webkit-scrollbar {
  width: 8px;
}

.questions::-webkit-scrollbar-track {
  background: var(--surface-muted, #E2E8F0);
  border-radius: 4px;
}

.questions::-webkit-scrollbar-thumb {
  background: var(--border, #CBD5E1);
  border-radius: 4px;
}

.questions::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary, #64748B);
}

/* Responsive Design */
@media (max-width: 768px) {
  .list-header {
    flex-wrap: wrap;
    padding: 16px;
    gap: 12px;
  }

  .header-icon {
    width: 40px;
    height: 40px;
  }

  .list-title {
    font-size: 16px;
  }

  .list-subtitle {
    font-size: 12px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .search-bar {
    padding: 12px 16px;
  }

  .search-control {
    padding: 8px 12px;
  }

  .questions {
    padding: 12px;
  }
}
</style>

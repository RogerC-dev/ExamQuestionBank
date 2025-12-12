<template>
  <div class="question-list">
    <div class="list-header">
      <div>
        <h3>題目列表</h3>
        <p class="subtitle">管理目前考卷的所有題目與配分</p>
      </div>

      <div class="header-actions">
        <button class="btn btn-sm btn-outline-secondary me-1" @click="$emit('add-existing-question')">
          + 從題庫加入
        </button>
        <button class="btn btn-sm btn-primary" @click="$emit('add-question')">
          + 新增題目
        </button>
      </div>
    </div>

    <div class="search-box d-flex align-items-center gap-2">
      <input
        type="checkbox"
        :checked="isAllSelected"
        :indeterminate.prop="isPartialSelected"
        @change="toggleSelectAll"
        class="form-check-input m-0"
        title="全選/取消全選"
      />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋題目內容、科目..."
        class="search-input flex-grow-1"
      />
      <span v-if="selectedIds.length > 0" class="text-muted small text-nowrap">
        已選 {{ selectedIds.length }} 題
      </span>
    </div>

    <div v-if="loading" class="loading">載入中...</div>

    <div v-else-if="filteredQuestions.length === 0" class="empty-state">
      <p>{{ searchQuery ? '沒有符合的題目' : '尚未加入任何題目' }}</p>
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
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: #6b7280;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-box {
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.questions {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.loading,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-outline-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline-secondary:hover {
  background: #f3f4f6;
}
</style>

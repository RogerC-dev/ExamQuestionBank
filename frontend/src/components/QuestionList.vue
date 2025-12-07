<template>
  <div class="question-list">
    <div class="list-header">
      <div>
        <h3>題目列表</h3>
        <p class="subtitle">管理目前考卷的所有題目與配分</p>
      </div>

      <div class="header-actions">
        <button class="btn btn-sm btn-primary" @click="$emit('add-question')">
          + 新增題目
        </button>
      </div>
    </div>

    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋題目內容、科目..."
        class="search-input"
      />
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
        @select="selectQuestion"
        @remove="(id) => $emit('remove-question', id)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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
  'remove-question',
  'auto-distribute',
  'update:total-points'
])

const searchQuery = ref('')

const filteredQuestions = computed(() => {
  let questions = props.questions

  // 先按 order 排序
  questions = [...questions].sort((a, b) => (a.order || 0) - (b.order || 0))

  // 如果有搜尋條件，進行過濾
  if (!searchQuery.value) {
    return questions
  }

  const query = searchQuery.value.toLowerCase()
  return questions.filter(item => {
    return (
      item.question_content?.toLowerCase().includes(query) ||
      item.question_subject?.toLowerCase().includes(query) ||
      item.question_category?.toLowerCase().includes(query)
    )
  })
})

const selectQuestion = (item) => {
  emit('select-question', item)
}

const autoDistributeDisabled = computed(() => {
  return props.autoDistributeLoading || props.questions.length === 0
})
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
  gap: 12px;
}

.total-points-control {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4b5563;
}

.total-points-control input {
  width: 80px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
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

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary:not(:disabled):hover {
  background: #e5e7eb;
}
</style>

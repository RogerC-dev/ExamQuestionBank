<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-content">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              <line x1="12" y1="8" x2="12" y2="14"></line>
              <line x1="9" y1="11" x2="15" y2="11"></line>
            </svg>
          </div>
          <div>
            <h3 class="modal-title">從題庫加入題目</h3>
            <p class="modal-subtitle">搜尋並選擇要加入考卷的題目</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- 已排除提示 -->
        <div v-if="excludedCount > 0" class="excluded-hint">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>已排除 <strong>{{ excludedCount }}</strong> 題（這些題目已在考卷中）</span>
        </div>

        <!-- 篩選區 -->
        <div class="filters-section">
          <!-- 選擇控制列 -->
          <div class="selection-row">
            <div class="selection-control">
              <input type="checkbox" :checked="isAllSelected" :indeterminate.prop="isPartialSelected"
                @change="toggleSelectAll" class="select-all-checkbox" title="全選/取消全選" />
              <span class="selection-label">全選此頁</span>
              <span v-if="selectedQuestions.length > 0" class="selection-badge">
                已選 {{ selectedQuestions.length }} 題
              </span>
            </div>
          </div>

          <!-- 篩選面板 -->
          <QuestionFilterPanel v-model="filters" :tags="tagOptions" :loading="loading" :total-count="totalCount"
            :show-title="false" :show-result-count="false" @search="handleFilterChange" @reset="resetFilters" />
        </div>

        <!-- 題目列表 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>載入中...</p>
        </div>

        <div v-else-if="allQuestions.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" class="empty-icon">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <p class="empty-text">{{ hasActiveFilters ? '沒有找到符合的題目' : '目前沒有可用的題目' }}</p>
          <button v-if="hasActiveFilters" class="empty-reset-btn" @click="resetFilters">清除篩選條件</button>
        </div>

        <div v-else-if="filteredQuestions.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" class="empty-icon">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          <p class="empty-text">此頁的題目皆已加入考卷</p>
          <div class="empty-actions">
            <button v-if="currentPage > 1" class="empty-action-btn" @click="goToPage(currentPage - 1)">
              查看上一頁
            </button>
            <button v-if="currentPage < totalPages" class="empty-action-btn" @click="goToPage(currentPage + 1)">
              查看下一頁
            </button>
          </div>
        </div>

        <div v-else class="questions-list">
          <div v-for="question in filteredQuestions" :key="question.id" class="question-item"
            :class="{ selected: selectedQuestions.some(q => q.id === question.id) }" @click="toggleQuestion(question)">
            <input type="checkbox" :checked="selectedQuestions.some(q => q.id === question.id)"
              class="question-checkbox" @click.stop @change="toggleQuestion(question)" />
            <div class="question-info">
              <div class="question-badges">
                <span class="badge badge-subject">{{ question.subject }}</span>
                <span class="badge badge-category">{{ question.category }}</span>
                <span v-for="tag in (question.tags || []).slice(0, 2)" :key="tag.id" class="badge badge-tag">
                  {{ tag.name }}
                </span>
                <span v-if="(question.tags || []).length > 2" class="badge badge-more">
                  +{{ question.tags.length - 2 }}
                </span>
              </div>
              <div class="question-content">{{ question.content }}</div>
            </div>
          </div>
        </div>

        <!-- 分頁 -->
        <div v-if="totalPages > 1" class="pagination-section">
          <div class="pagination-info">
            顯示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalCount) }} / {{ totalCount
            }} 題
          </div>
          <div class="pagination-controls">
            <button class="pagination-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
              上一頁
            </button>
            <span class="pagination-page">{{ currentPage }} / {{ totalPages }}</span>
            <button class="pagination-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
              下一頁
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>

        <!-- 設定區 -->
        <div v-if="selectedQuestions.length > 0" class="settings-section">
          <div class="settings-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path
                d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">
              </path>
            </svg>
            <span>配分設定</span>
          </div>
          <div class="points-input-group">
            <label for="points">每題配分</label>
            <div class="points-input-wrapper">
              <input id="points" v-model.number="points" type="number" step="0.01" min="0" class="points-input" />
              <span class="points-unit">分</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <div class="footer-info" v-if="selectedQuestions.length > 0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>將加入 <strong>{{ selectedQuestions.length }}</strong> 題，每題 <strong>{{ points }}</strong> 分</span>
        </div>
        <div class="footer-actions">
          <button class="footer-btn footer-btn-secondary" @click="$emit('close')">
            取消
          </button>
          <button class="footer-btn footer-btn-primary" :disabled="selectedQuestions.length === 0" @click="handleAdd">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            確認新增
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import questionService from '../services/questionService'
import tagService from '../services/tagService'
import QuestionFilterPanel from '@/components/common/QuestionFilterPanel.vue'

const props = defineProps({
  existingQuestionIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'add'])

const allQuestions = ref([])
const loading = ref(false)
const selectedQuestions = ref([])
const points = ref(1)

// 篩選相關
const filters = ref({
  subject: '',
  difficulty: '',
  search: '',
  tags: [],
  tag_mode: 'or'
})
const tagOptions = ref([])

// 分頁相關
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// 過濾掉已存在的題目
const filteredQuestions = computed(() => {
  return allQuestions.value.filter(q => !props.existingQuestionIds.includes(q.id))
})

// 計算被排除的題目數量
const excludedCount = computed(() => {
  return allQuestions.value.length - filteredQuestions.value.length
})

// 總頁數
const totalPages = computed(() => {
  return Math.ceil(totalCount.value / pageSize.value)
})

const isAllSelected = computed(() => {
  return filteredQuestions.value.length > 0 &&
    filteredQuestions.value.every(q => selectedQuestions.value.some(sq => sq.id === q.id))
})

const isPartialSelected = computed(() => {
  const selected = filteredQuestions.value.filter(q => selectedQuestions.value.some(sq => sq.id === q.id))
  return selected.length > 0 && selected.length < filteredQuestions.value.length
})

const hasActiveFilters = computed(() => {
  return filters.value.search || filters.value.subject || filters.value.difficulty || filters.value.tags.length > 0
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    // 只移除當前頁面的選取
    const currentIds = filteredQuestions.value.map(q => q.id)
    selectedQuestions.value = selectedQuestions.value.filter(q => !currentIds.includes(q.id))
  } else {
    // 添加當前頁面的所有題目（排除已選取的）
    const currentIds = selectedQuestions.value.map(q => q.id)
    const newSelections = filteredQuestions.value.filter(q => !currentIds.includes(q.id))
    selectedQuestions.value = [...selectedQuestions.value, ...newSelections]
  }
}

const toggleQuestion = (question) => {
  const idx = selectedQuestions.value.findIndex(q => q.id === question.id)
  if (idx === -1) {
    selectedQuestions.value.push(question)
  } else {
    selectedQuestions.value.splice(idx, 1)
  }
}

const loadQuestions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.subject) params.subject = filters.value.subject
    if (filters.value.difficulty) params.difficulty = filters.value.difficulty
    if (filters.value.tags && filters.value.tags.length > 0) {
      params.tags = filters.value.tags.map(t => t.id).join(',')
      params.tag_mode = filters.value.tag_mode
    }

    const response = await questionService.getQuestions(params)
    const data = response.data

    if (data.results) {
      allQuestions.value = data.results
      totalCount.value = data.count || data.results.length
    } else {
      allQuestions.value = data
      totalCount.value = data.length
    }
  } catch (error) {
    console.error('載入題目失敗:', error)
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  try {
    const res = await tagService.getTags()
    let items = res.data?.results || res.data
    if (!Array.isArray(items)) items = []
    tagOptions.value = items.filter(t => t != null)
  } catch (err) {
    console.error('載入標籤失敗:', err)
  }
}



const handleFilterChange = () => {
  currentPage.value = 1
  loadQuestions()
}

const resetFilters = () => {
  filters.value = {
    subject: '',
    difficulty: '',
    search: '',
    tags: [],
    tag_mode: 'or'
  }
  currentPage.value = 1
  loadQuestions()
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadQuestions()
}

const handleAdd = () => {
  if (selectedQuestions.value.length === 0) return
  emit('add', selectedQuestions.value.map(q => q.id), points.value)
}

onMounted(() => {
  loadQuestions()
  loadTags()
})
</script>

<style scoped>
/* Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 2147483647;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

/* Container */
.modal-container {
  width: 90%;
  max-width: 900px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  height: auto;
  max-height: 90vh;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Header */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 20px;
  border-bottom: 1px solid var(--border, #CBD5E1);
}

.header-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex: 1;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary, #476996);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  margin: 0 0 4px 0;
}

.modal-subtitle {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

/* Body */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Excluded Hint */
.excluded-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #FEF3C7;
  border: 1px solid #FCD34D;
  border-radius: 10px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #92400E;
}

.excluded-hint svg {
  flex-shrink: 0;
  color: #D97706;
}

.excluded-hint strong {
  font-weight: 600;
}

/* Filters Section */
.filters-section {
  margin-bottom: 20px;
}

/* Selection Row */
.selection-row {
  margin-bottom: 16px;
}

.selection-control {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-page, #F8FAFC);
  border: 2px solid var(--border, #CBD5E1);
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.select-all-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin: 0;
  flex-shrink: 0;
  accent-color: var(--primary, #476996);
}

.selection-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1E293B);
  flex-shrink: 0;
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
  margin-left: auto;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
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
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  color: var(--border, #CBD5E1);
  margin-bottom: 16px;
}

.empty-text {
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary, #64748B);
}

.empty-reset-btn {
  padding: 10px 20px;
  border: 2px solid var(--primary, #476996);
  border-radius: 10px;
  background: white;
  color: var(--primary, #476996);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-reset-btn:hover {
  background: var(--primary-soft, #EEF2FF);
}

.empty-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.empty-action-btn {
  padding: 10px 20px;
  border: 2px solid var(--primary, #476996);
  border-radius: 10px;
  background: white;
  color: var(--primary, #476996);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-action-btn:hover {
  background: var(--primary-soft, #EEF2FF);
}

/* Questions List */
.questions-list {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid var(--border, #CBD5E1);
  border-radius: 12px;
  background: white;
}

.question-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #E2E8F0);
  cursor: pointer;
  transition: all 0.2s ease;
}

.question-item:last-child {
  border-bottom: none;
}

.question-item:hover {
  background: var(--bg-page, #F8FAFC);
}

.question-item.selected {
  background: var(--primary-soft, #EEF2FF);
  border-color: rgba(71, 105, 150, 0.2);
}

.question-checkbox {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  cursor: pointer;
  accent-color: var(--primary, #476996);
  flex-shrink: 0;
}

.question-info {
  flex: 1;
  min-width: 0;
}

.question-badges {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}

.badge-subject {
  background: var(--primary-soft, #EEF2FF);
  color: var(--primary, #476996);
}

.badge-category {
  background: #FEF3C7;
  color: #92400E;
}

.badge-tag {
  background: #E0E7FF;
  color: #4338CA;
}

.badge-more {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.question-content {
  font-size: 14px;
  color: var(--text-primary, #1E293B);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Scrollbar */
.questions-list::-webkit-scrollbar {
  width: 8px;
}

.questions-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.questions-list::-webkit-scrollbar-thumb {
  background: var(--border, #CBD5E1);
  border-radius: 4px;
}

.questions-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary, #64748B);
}

/* Pagination */
.pagination-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--bg-page, #F8FAFC);
  border-radius: 10px;
  border: 1px solid var(--border, #E2E8F0);
}

.pagination-info {
  font-size: 13px;
  color: var(--text-secondary, #64748B);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 2px solid var(--border, #CBD5E1);
  border-radius: 8px;
  background: white;
  color: var(--text-primary, #1E293B);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--primary, #476996);
  color: var(--primary, #476996);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-page {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  min-width: 60px;
  text-align: center;
}

/* Settings Section */
.settings-section {
  margin-top: 20px;
  padding: 20px;
  background: var(--bg-page, #F8FAFC);
  border-radius: 12px;
  border: 1px solid var(--border, #E2E8F0);
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  margin-bottom: 16px;
}

.settings-header svg {
  color: var(--primary, #476996);
}

.points-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.points-input-group label {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

.points-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.points-input {
  width: 100px;
  padding: 10px 12px;
  border: 2px solid var(--border, #CBD5E1);
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  transition: all 0.2s ease;
}

.points-input:focus {
  outline: none;
  border-color: var(--primary, #476996);
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.points-unit {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-top: 1px solid var(--border, #CBD5E1);
  background: var(--bg-page, #F8FAFC);
  border-radius: 0 0 16px 16px;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary, #64748B);
}

.footer-info svg {
  color: var(--primary, #476996);
  flex-shrink: 0;
}

.footer-info strong {
  color: var(--primary, #476996);
  font-weight: 600;
}

.footer-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.footer-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.footer-btn-secondary {
  background: white;
  color: var(--text-secondary, #64748B);
  border: 2px solid var(--border, #CBD5E1);
}

.footer-btn-secondary:hover {
  background: #f9fafb;
  color: var(--text-primary, #1E293B);
  border-color: #94a3b8;
}

.footer-btn-primary {
  background: var(--primary, #476996);
  color: white;
  box-shadow: 0 2px 4px rgba(71, 105, 150, 0.2);
}

.footer-btn-primary:hover:not(:disabled) {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(71, 105, 150, 0.3);
}

.footer-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    max-height: 95vh;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-title {
    font-size: 18px;
  }

  .modal-body {
    padding: 16px;
  }

  .filter-row {
    flex-direction: column;
  }

  .filter-group,
  .filter-tags {
    width: 100%;
  }

  .filter-select {
    width: 100%;
  }

  .pagination-section {
    flex-direction: column;
    gap: 12px;
  }

  .modal-footer {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
  }

  .footer-info {
    justify-content: center;
    margin-bottom: 8px;
  }

  .footer-actions {
    width: 100%;
    flex-direction: column;
    margin-left: 0;
  }

  .footer-btn {
    width: 100%;
  }

  .questions-list {
    max-height: 200px;
  }
}
</style>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>新增題目到考卷</h3>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <!-- 搜尋區 -->
        <div class="search-section">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜尋題目內容..."
            class="search-input"
            @input="handleSearch"
          />
        </div>

        <!-- 題目列表 -->
        <div v-if="loading" class="loading">載入中...</div>

        <div v-else-if="questions.length === 0" class="empty">
          {{ searchKeyword ? '沒有找到符合的題目' : '目前沒有可用的題目' }}
        </div>

        <div v-else class="questions-list">
          <div
            v-for="question in questions"
            :key="question.id"
            class="question-item"
            :class="{ selected: selectedQuestionId === question.id }"
            @click="selectQuestion(question)"
          >
            <div class="question-info">
              <div class="question-badges">
                <span class="badge">{{ question.subject }}</span>
                <span class="badge">{{ question.category }}</span>
              </div>
              <div class="question-content">{{ question.content }}</div>
            </div>
          </div>
        </div>

        <!-- 設定區 -->
        <div v-if="selectedQuestionId" class="settings-section">
          <h4>題目設定</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="order">順序</label>
              <input
                id="order"
                v-model.number="order"
                type="number"
                min="1"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="points">配分</label>
              <input
                id="points"
                v-model.number="points"
                type="number"
                step="0.01"
                min="0"
                class="form-input"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">
          取消
        </button>
        <button
          class="btn btn-primary"
          :disabled="!selectedQuestionId"
          @click="handleAdd"
        >
          確認新增
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import questionService from '../services/questionService'

const emit = defineEmits(['close', 'add'])

const questions = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedQuestionId = ref(null)
const order = ref(1)
const points = ref(0)

let searchTimeout = null

const loadQuestions = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }

    const response = await questionService.getQuestions(params)
    questions.value = response.data.results || response.data
  } catch (error) {
    console.error('載入題目失敗:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadQuestions()
  }, 500)
}

const selectQuestion = (question) => {
  selectedQuestionId.value = question.id
}

const handleAdd = () => {
  if (!selectedQuestionId.value) return
  emit('add', selectedQuestionId.value, order.value, points.value)
}

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.search-section {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.loading,
.empty {
  padding: 40px;
  text-align: center;
  color: #999;
}

.questions-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.question-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: #4CAF50;
  background: #f9f9f9;
}

.question-item.selected {
  border-color: #4CAF50;
  background: #e8f5e9;
}

.question-badges {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.question-content {
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.settings-section {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.settings-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}
</style>

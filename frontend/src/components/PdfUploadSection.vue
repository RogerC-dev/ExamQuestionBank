<template>
  <div class="pdf-upload-section">
    <h3>匯入試卷 PDF</h3>
    <div class="upload-buttons">
      <!-- 匯入考卷 PDF -->
      <div class="upload-item">
        <label class="upload-label">
          <input
            type="file"
            accept=".pdf"
            @change="handleQuestionPdfUpload"
            ref="questionFileInput"
            style="display: none"
          />
          <button
            type="button"
            class="btn btn-primary"
            @click="$refs.questionFileInput.click()"
            :disabled="uploadingQuestions"
          >
            {{ uploadingQuestions ? '匯入中...' : '📄 匯入考卷 PDF' }}
          </button>
        </label>
        <span v-if="questionFileName" class="file-name">{{ questionFileName }}</span>
      </div>

      <!-- 匯入答案 PDF -->
      <div class="upload-item">
        <label class="upload-label">
          <input
            type="file"
            accept=".pdf"
            @change="handleAnswerPdfUpload"
            ref="answerFileInput"
            style="display: none"
          />
          <button
            type="button"
            class="btn btn-secondary"
            @click="$refs.answerFileInput.click()"
            :disabled="uploadingAnswers"
          >
            {{ uploadingAnswers ? '匯入中...' : '✓ 匯入答案 PDF' }}
          </button>
        </label>
        <span v-if="answerFileName" class="file-name">{{ answerFileName }}</span>
      </div>
    </div>

    <!-- 匯入結果顯示 -->
    <div v-if="importResult" class="import-result">
      <div class="result-header">
        <h4>匯入結果</h4>
        <button class="btn btn-sm btn-close" @click="clearResult">×</button>
      </div>

      <div class="result-info">
        <div class="info-item">
          <span class="label">科目：</span>
          <span class="value">{{ importResult.subject || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">分類：</span>
          <span class="value">{{ importResult.category || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">難度：</span>
          <span class="value">{{ importResult.level || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">時間限制：</span>
          <span class="value">{{ importResult.time_length ? `${importResult.time_length} 分鐘` : '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">題目數量：</span>
          <span class="value">{{ importResult.count || 0 }} 題</span>
        </div>
        <div v-if="answersData" class="info-item">
          <span class="label">答案狀態：</span>
          <span class="value success">✓ 已匯入 ({{ answersData.count || 0 }} 個答案)</span>
        </div>
      </div>

      <!-- 答案修改提醒 -->
      <div v-if="answersData && answersData.notes" class="notes-alert">
        <div class="alert-header">
          <span class="alert-icon">⚠️</span>
          <strong>答案修改提醒</strong>
        </div>
        <div class="alert-content">
          {{ answersData.notes }}
        </div>
        <div v-if="hasModifiedAnswers" class="modified-answers-list">
          <p><strong>有答案修改的題目：</strong></p>
          <div class="modified-items">
            <span
              v-for="(answer, index) in answersData.answers"
              :key="index"
              v-show="answer === '*'"
              class="modified-badge"
            >
              第 {{ index + 1 }} 題
            </span>
          </div>
        </div>
      </div>

      <div class="result-actions">
        <button
          class="btn btn-success"
          @click="handleImportConfirm"
        >
          確認使用此資料
        </button>
        <button class="btn btn-secondary" @click="clearResult">
          取消
        </button>
      </div>
    </div>

    <!-- 錯誤訊息 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../services/api'

const emit = defineEmits(['import-success'])

const questionFileInput = ref(null)
const answerFileInput = ref(null)
const questionFileName = ref('')
const answerFileName = ref('')

const uploadingQuestions = ref(false)
const uploadingAnswers = ref(false)
const importing = ref(false)

const importResult = ref(null)
const answersData = ref(null)
const errorMessage = ref('')

// 檢查是否有修改的答案 (答案為 *)
const hasModifiedAnswers = computed(() => {
  if (!answersData.value || !answersData.value.answers) return false
  return answersData.value.answers.some(answer => answer === '*')
})

// 處理考卷 PDF 上傳
const handleQuestionPdfUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  questionFileName.value = file.name
  uploadingQuestions.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/question_bank/extract-questions-pdf/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    importResult.value = response.data
    console.log('考卷 PDF 解析成功:', response.data)
  } catch (error) {
    console.error('考卷 PDF 上傳失敗:', error)
    errorMessage.value = error.response?.data?.error || '考卷 PDF 上傳失敗'
  } finally {
    uploadingQuestions.value = false
    // 清空 input，讓使用者可以重新上傳同一個檔案
    event.target.value = ''
  }
}

// expose a method to open file picker programmatically
const openQuestionPicker = () => {
  questionFileInput.value?.click()
}
defineExpose({ openQuestionPicker })

// 處理答案 PDF 上傳
const handleAnswerPdfUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  answerFileName.value = file.name
  uploadingAnswers.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/question_bank/extract-answers-pdf/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    answersData.value = response.data
    console.log('答案 PDF 解析成功:', response.data)

    // 如果已經有考卷資料，合併答案
    if (importResult.value && importResult.value.questions) {
      mergeAnswers()
    }
  } catch (error) {
    console.error('答案 PDF 上傳失敗:', error)
    errorMessage.value = error.response?.data?.error || '答案 PDF 上傳失敗'
  } finally {
    uploadingAnswers.value = false
    event.target.value = ''
  }
}

// 合併答案到題目
const mergeAnswers = () => {
  if (!importResult.value || !answersData.value) return

  const questions = importResult.value.questions
  const answers = answersData.value.answers

  // 將答案與題目合併
  questions.forEach((question, index) => {
    if (answers[index]) {
      question.correct_answer = answers[index]
      question.has_modified_answer = answers[index] === '*'
    }
  })

  console.log('已合併答案:', questions)
  console.log('答案修改提醒:', answersData.value.notes)
}

// 確認匯入
const handleImportConfirm = () => {
  if (!importResult.value) return

  // 觸發父組件的匯入事件
  emit('import-success', {
    examData: {
      name: `${importResult.value.subject || ''} ${importResult.value.category || ''}`.trim(),
      description: importResult.value.level ? `難度：${importResult.value.level}` : '',
      subject: importResult.value.subject,
      category: importResult.value.category,
      level: importResult.value.level,
      time_limit: importResult.value.time_length
    },
    questions: importResult.value.questions,
    answers: answersData.value
  })

  // 清除結果（讓使用者可以繼續匯入其他 PDF）
  clearResult()
}

// 清除結果
const clearResult = () => {
  importResult.value = null
  answersData.value = null
  questionFileName.value = ''
  answerFileName.value = ''
  errorMessage.value = ''
}
</script>

<style scoped>
.pdf-upload-section {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.pdf-upload-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.upload-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.upload-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-label {
  display: inline-block;
}

.file-name {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
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
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-success {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.btn-sm {
  padding: 4px 8px;
  font-size: 18px;
}

.btn-close {
  background: transparent;
  color: #999;
  border: none;
  line-height: 1;
}

.btn-close:hover {
  color: #333;
}

.import-result {
  margin-top: 20px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.result-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  gap: 8px;
}

.info-item .label {
  font-weight: 500;
  color: #666;
}

.info-item .value {
  color: #333;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.value.success {
  color: #4CAF50;
  font-weight: 600;
}

.notes-alert {
  margin-top: 16px;
  padding: 16px;
  background: #fff3e0;
  border-radius: 8px;
  border-left: 4px solid #ff9800;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.alert-icon {
  font-size: 18px;
}

.alert-header strong {
  color: #e65100;
  font-size: 15px;
}

.alert-content {
  color: #e65100;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.modified-answers-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ffe0b2;
}

.modified-answers-list p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #e65100;
}

.modified-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.modified-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #ff9800;
  color: white;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.error-message {
  margin-top: 12px;
  padding: 12px 16px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c62828;
}
</style>

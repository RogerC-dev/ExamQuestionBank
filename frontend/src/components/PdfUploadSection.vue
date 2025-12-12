<template>
  <div class="pdf-upload-container">
    <!-- 標題區 -->
    <div class="upload-header">
      <div class="header-content">
        <div class="icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <div>
          <h5 class="title">PDF 匯入</h5>
          <p class="subtitle">支援考卷與答案檔分別上傳，自動識別題目與答案</p>
        </div>
      </div>
    </div>

    <!-- 上傳區域 -->
    <div class="upload-areas">
      <!-- 考卷上傳區 -->
      <div class="upload-card question-card">
        <div class="card-header-custom">
          <div class="card-icon question-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <h6>考卷檔案</h6>
        </div>

        <div 
          class="dropzone"
          :class="{ 'dragging': isDraggingQuestion, 'uploaded': questionFileName, 'uploading': uploadingQuestions }"
          @drop.prevent="handleQuestionDrop"
          @dragover.prevent="isDraggingQuestion = true"
          @dragleave.prevent="isDraggingQuestion = false"
          @click="!uploadingQuestions && $refs.questionFileInput.click()"
        >
          <input
            type="file"
            accept=".pdf"
            @change="handleQuestionPdfUpload"
            ref="questionFileInput"
            style="display: none"
          />

          <div v-if="uploadingQuestions" class="upload-state">
            <div class="spinner-wrapper">
              <div class="spinner"></div>
            </div>
            <p class="state-text">正在解析考卷...</p>
            <small class="state-subtext">請稍候</small>
          </div>

          <div v-else-if="questionFileName" class="upload-state success">
            <div class="success-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="state-text">{{ questionFileName }}</p>
            <small class="state-subtext">點擊重新上傳</small>
          </div>

          <div v-else class="upload-state">
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </div>
            <p class="state-text">拖放 PDF 檔案到這裡</p>
            <small class="state-subtext">或點擊選擇檔案</small>
          </div>
        </div>
      </div>

      <!-- 答案上傳區 -->
      <div class="upload-card answer-card">
        <div class="card-header-custom">
          <div class="card-icon answer-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <h6>答案檔案</h6>
        </div>

        <div 
          class="dropzone"
          :class="{ 'dragging': isDraggingAnswer, 'uploaded': answerFileName, 'uploading': uploadingAnswers }"
          @drop.prevent="handleAnswerDrop"
          @dragover.prevent="isDraggingAnswer = true"
          @dragleave.prevent="isDraggingAnswer = false"
          @click="!uploadingAnswers && $refs.answerFileInput.click()"
        >
          <input
            type="file"
            accept=".pdf"
            @change="handleAnswerPdfUpload"
            ref="answerFileInput"
            style="display: none"
          />

          <div v-if="uploadingAnswers" class="upload-state">
            <div class="spinner-wrapper">
              <div class="spinner"></div>
            </div>
            <p class="state-text">正在解析答案...</p>
            <small class="state-subtext">請稍候</small>
          </div>

          <div v-else-if="answerFileName" class="upload-state success">
            <div class="success-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="state-text">{{ answerFileName }}</p>
            <small class="state-subtext">點擊重新上傳</small>
          </div>

          <div v-else class="upload-state">
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </div>
            <p class="state-text">拖放 PDF 檔案到這裡</p>
            <small class="state-subtext">或點擊選擇檔案（選填）</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 匯入結果 -->
    <transition name="result-fade">
      <div v-if="importResult" class="result-container">
        <div class="result-header">
          <div class="result-title">
            <div class="result-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <span>解析完成</span>
          </div>
          <button type="button" class="close-btn" @click="clearResult">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="result-body">
          <!-- 試卷資訊卡片 -->
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">科目</div>
              <div class="info-value">{{ importResult.subject || '-' }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">分類</div>
              <div class="info-value">{{ importResult.category || '-' }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">難度</div>
              <div class="info-value">{{ importResult.level || '-' }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">時間限制</div>
              <div class="info-value">{{ importResult.time_length ? `${importResult.time_length} 分鐘` : '-' }}</div>
            </div>
            <div class="info-item highlight">
              <div class="info-label">題目數量</div>
              <div class="info-value">{{ importResult.count || 0 }} 題</div>
            </div>
            <div v-if="answersData" class="info-item highlight success">
              <div class="info-label">答案狀態</div>
              <div class="info-value">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                {{ answersData.count || 0 }} 個答案
              </div>
            </div>
          </div>

          <!-- 答案修改警告 -->
          <div v-if="answersData && answersData.notes" class="warning-box">
            <div class="warning-header">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <strong>答案修改提醒</strong>
            </div>
            <p class="warning-text">{{ answersData.notes }}</p>
            <div v-if="hasModifiedAnswers" class="modified-list">
              <small class="modified-label">有答案修改的題目：</small>
              <div class="badge-group">
                <span
                  v-for="(answer, index) in answersData.answers"
                  :key="index"
                  v-show="answer === '*'"
                  class="question-badge"
                >
                  第 {{ index + 1 }} 題
                </span>
              </div>
            </div>
          </div>

          <!-- 題目預覽 -->
          <div v-if="importResult.questions && importResult.questions.length > 0" class="preview-section">
            <div class="preview-header" @click="showPreview = !showPreview">
              <span class="preview-title">題目預覽 ({{ importResult.questions.length }} 題)</span>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="18" 
                height="18" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2" 
                stroke-linecap="round" 
                stroke-linejoin="round"
                :class="{ 'rotated': showPreview }"
                class="chevron"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <transition name="preview-slide">
              <div v-if="showPreview" class="preview-list">
                <div 
                  v-for="(question, index) in previewQuestions" 
                  :key="index"
                  class="preview-item"
                >
                  <div class="question-number">{{ index + 1 }}</div>
                  <div class="question-content">
                    <div class="question-text">{{ question.question }}</div>
                    <div v-if="question.options && question.options.length" class="options-preview">
                      <span v-for="(opt, i) in question.options.slice(0, 4)" :key="i" class="option-tag">
                        {{ String.fromCharCode(65 + i) }}. {{ opt.substring(0, 20) }}{{ opt.length > 20 ? '...' : '' }}
                      </span>
                    </div>
                    <div v-if="question.correct_answer" class="answer-preview">
                      <span class="answer-badge">答案: {{ question.correct_answer }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="importResult.questions.length > 5" class="preview-more">
                  還有 {{ importResult.questions.length - 5 }} 題...
                </div>
              </div>
            </transition>
          </div>

          <!-- 操作按鈕 -->
          <div class="action-buttons">
            <button class="btn-confirm" @click="handleImportConfirm">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              確認使用此資料
            </button>
            <button class="btn-cancel" @click="clearResult">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              取消
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 錯誤訊息 -->
    <transition name="error-fade">
      <div v-if="errorMessage" class="error-toast">
        <div class="error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <span>{{ errorMessage }}</span>
        <button class="error-close" @click="errorMessage = ''">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </transition>
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

const isDraggingQuestion = ref(false)
const isDraggingAnswer = ref(false)
const showPreview = ref(false)

// 檢查是否有修改的答案 (答案為 *)
const hasModifiedAnswers = computed(() => {
  if (!answersData.value || !answersData.value.answers) return false
  return answersData.value.answers.some(answer => answer === '*')
})

// 預覽題目（最多顯示 5 題）
const previewQuestions = computed(() => {
  if (!importResult.value || !importResult.value.questions) return []
  return importResult.value.questions.slice(0, 5)
})

// 處理考卷 PDF 上傳
const handleQuestionPdfUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  await uploadQuestionFile(file)
  event.target.value = ''
}

// 處理考卷拖放
const handleQuestionDrop = async (event) => {
  isDraggingQuestion.value = false
  const file = event.dataTransfer.files[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    errorMessage.value = '請上傳 PDF 檔案'
    return
  }
  await uploadQuestionFile(file)
}

// 上傳考卷檔案
const uploadQuestionFile = async (file) => {
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
    showPreview.value = true // 自動展開預覽
    console.log('考卷 PDF 解析成功:', response.data)
  } catch (error) {
    console.error('考卷 PDF 上傳失敗:', error)
    errorMessage.value = error.response?.data?.error || '考卷 PDF 上傳失敗'
    questionFileName.value = ''
  } finally {
    uploadingQuestions.value = false
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

  await uploadAnswerFile(file)
  event.target.value = ''
}

// 處理答案拖放
const handleAnswerDrop = async (event) => {
  isDraggingAnswer.value = false
  const file = event.dataTransfer.files[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    errorMessage.value = '請上傳 PDF 檔案'
    return
  }
  await uploadAnswerFile(file)
}

// 上傳答案檔案
const uploadAnswerFile = async (file) => {
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
    answerFileName.value = ''
  } finally {
    uploadingAnswers.value = false
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
  showPreview.value = false
}
</script>

<style scoped>
.pdf-upload-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border, #CBD5E1);
  overflow: hidden;
  margin: 0 0 1.5rem;
}

/* 標題區 */
.upload-header {
  background: linear-gradient(to bottom, #f9fafb, #f3f4f6);
  padding: 1.25rem 1.5rem;
  border-bottom: 2px solid var(--border, #CBD5E1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrapper {
  width: 44px;
  height: 44px;
  background: var(--primary-soft, #EEF2FF);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary, #476996);
  flex-shrink: 0;
}

.title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary, #1E293B);
}

.subtitle {
  font-size: 0.8125rem;
  margin: 0.25rem 0 0;
  color: var(--text-secondary, #64748B);
}

/* 上傳區域 */
.upload-areas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  padding: 1.5rem;
}

.upload-card {
  background: #f9fafb;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.2s ease;
}

.upload-card:hover {
  border-color: var(--primary, #476996);
  box-shadow: 0 2px 8px rgba(71, 105, 150, 0.12);
}

.card-header-custom {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.card-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.question-icon {
  background: var(--primary, #476996);
}

.answer-icon {
  background: #10b981;
}

.card-header-custom h6 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

/* 拖放區 */
.dropzone {
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
  position: relative;
}

.dropzone:hover:not(.uploading) {
  background: #f9fafb;
}

.dropzone.dragging {
  background: var(--primary-soft, #EEF2FF);
  border-color: var(--primary, #476996);
}

.dropzone.uploading {
  cursor: not-allowed;
  opacity: 0.7;
  background: #f9fafb;
}

.dropzone.uploaded {
  background: #f0fdf4;
}

.upload-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon {
  color: var(--text-secondary, #64748B);
  opacity: 0.5;
  transition: all 0.2s ease;
}

.dropzone:hover .upload-icon {
  color: var(--primary, #476996);
  opacity: 1;
  transform: translateY(-4px);
}

.success-icon {
  width: 48px;
  height: 48px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  animation: successPop 0.4s ease;
}

@keyframes successPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

.spinner-wrapper {
  width: 48px;
  height: 48px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e5e7eb;
  border-top-color: var(--primary, #476996);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary, #1E293B);
  margin: 0;
}

.state-subtext {
  font-size: 0.75rem;
  color: var(--text-secondary, #64748B);
}

/* 匯入結果 */
.result-container {
  margin: 0 1.5rem 1.5rem;
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: linear-gradient(to bottom, #f0fdf4, #ecfdf5);
  border-bottom: 2px solid #d1fae5;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: #065f46;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.result-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-secondary, #64748B);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #f3f4f6;
  color: var(--text-primary, #1E293B);
}

.result-body {
  padding: 1.5rem;
}

/* 資訊網格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}

.info-item {
  padding: 0.875rem 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  transition: all 0.2s ease;
}

.info-item:hover {
  border-color: #cbd5e1;
  background: #f3f4f6;
}

.info-item.highlight {
  background: #fef3c7;
  border-color: #fcd34d;
}

.info-item.success {
  background: #d1fae5;
  border-color: #6ee7b7;
}

.info-label {
  font-size: 0.6875rem;
  color: var(--text-secondary, #64748B);
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.95rem;
  color: var(--text-primary, #1E293B);
  font-weight: 600;
}

/* 警告框 */
.warning-box {
  background: #fef3c7;
  border: 2px solid #fcd34d;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #92400e;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.warning-text {
  color: #78350f;
  font-size: 0.8125rem;
  margin: 0.5rem 0;
  line-height: 1.5;
}

.modified-list {
  margin-top: 0.75rem;
}

.modified-label {
  display: block;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.question-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  background: #fff;
  color: #92400e;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #fcd34d;
}

/* 題目預覽 */
.preview-section {
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: #fff;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.preview-header:hover {
  background: #f9fafb;
}

.preview-title {
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.chevron {
  transition: transform 0.25s ease;
  color: var(--text-secondary, #64748B);
  flex-shrink: 0;
}

.chevron.rotated {
  transform: rotate(180deg);
}

.preview-list {
  padding: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.preview-item {
  display: flex;
  gap: 0.875rem;
  padding: 0.875rem 1rem;
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  transition: all 0.2s ease;
}

.preview-item:hover {
  border-color: var(--primary, #476996);
  box-shadow: 0 2px 8px rgba(71, 105, 150, 0.12);
}

.preview-item:last-child {
  margin-bottom: 0;
}

.question-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: var(--primary, #476996);
  color: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-text {
  font-size: 0.875rem;
  color: var(--text-primary, #1E293B);
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.options-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.option-tag {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  background: #f9fafb;
  color: var(--text-secondary, #64748B);
  border-radius: 5px;
  font-size: 0.75rem;
  border: 1px solid #e5e7eb;
  font-weight: 500;
}

.answer-preview {
  margin-top: 0.5rem;
}

.answer-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #6ee7b7;
}

.preview-more {
  text-align: center;
  padding: 0.75rem;
  color: var(--text-secondary, #64748B);
  font-size: 0.8125rem;
  font-style: italic;
}

/* 操作按鈕 */
.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-confirm,
.btn-cancel {
  flex: 1;
  min-width: 140px;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-confirm {
  background: var(--primary, #476996);
  color: #fff;
}

.btn-confirm:hover {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
}

.btn-cancel {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.btn-cancel:hover {
  background: #e5e7eb;
  color: var(--text-primary, #1E293B);
}

/* 錯誤提示 */
.error-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #fef2f2;
  border: 2px solid #fecaca;
  color: #991b1b;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: 400px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.error-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  color: #dc2626;
}

.error-close {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  color: #991b1b;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.error-close:hover {
  background: #fee2e2;
}

/* 動畫 */
.result-fade-enter-active,
.result-fade-leave-active {
  transition: all 0.25s ease;
}

.result-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.result-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.preview-slide-enter-active,
.preview-slide-leave-active {
  transition: all 0.25s ease;
  max-height: 500px;
}

.preview-slide-enter-from,
.preview-slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.error-fade-enter-active {
  animation: slideIn 0.3s ease;
}

.error-fade-leave-active {
  animation: slideOut 0.25s ease;
}

@keyframes slideOut {
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .upload-areas {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn-confirm,
  .btn-cancel {
    width: 100%;
  }

  .error-toast {
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
}

/* 滾動條樣式 */
.preview-list::-webkit-scrollbar {
  width: 6px;
}

.preview-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.preview-list::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.preview-list::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>

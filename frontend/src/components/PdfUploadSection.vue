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
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="state-text">{{ questionFileName }}</p>
            <small class="state-subtext">點擊重新上傳</small>
          </div>

          <div v-else class="upload-state">
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="state-text">{{ answerFileName }}</p>
            <small class="state-subtext">點擊重新上傳</small>
          </div>

          <div v-else class="upload-state">
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <span>解析完成</span>
          </div>
          <button type="button" class="close-btn" @click="clearResult">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
            <div class="info-item highlight">
              <div class="info-label">題目數量</div>
              <div class="info-value">{{ importResult.count || 0 }} 題</div>
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
                  </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- 操作按鈕 -->
          <div class="action-buttons">
            <button class="btn-confirm" @click="handleImportConfirm">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              確認使用此資料
            </button>
            <button class="btn-cancel" @click="clearResult">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <span>{{ errorMessage }}</span>
        <button class="error-close" @click="errorMessage = ''">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
import { supabase } from '@/lib/supabase'

const emit = defineEmits(['import-success'])

const questionFileInput = ref(null)
const answerFileInput = ref(null)
const questionFileName = ref('')
const answerFileName = ref('')

const uploadingQuestions = ref(false)
const uploadingAnswers = ref(false)

const importResult = ref(null)
const answersData = ref(null)
const errorMessage = ref('')

const isDraggingQuestion = ref(false)
const isDraggingAnswer = ref(false)
const showPreview = ref(false)

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

// 上傳考卷檔案 - 使用 Edge Function
const uploadQuestionFile = async (file) => {
  questionFileName.value = file.name
  uploadingQuestions.value = true
  errorMessage.value = ''

  try {
    // Read file as base64
    const base64 = await readFileAsBase64(file)
    
    // Call Edge Function for PDF parsing (pdfplumber)
    const { data, error } = await supabase.functions.invoke('extract-pdf', {
      body: {
        file_data: base64,
        file_name: file.name,
        type: 'questions'
      }
    })

    if (error) throw new Error(error.message)

    importResult.value = data
    showPreview.value = true
    console.log('考卷 PDF 解析成功:', data)
  } catch (error) {
    console.error('考卷 PDF 上傳失敗:', error)
    errorMessage.value = error.message || '考卷 PDF 上傳失敗'
    questionFileName.value = ''
  } finally {
    uploadingQuestions.value = false
  }
}

// Helper: Read file as base64
const readFileAsBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
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

// 上傳答案檔案 - 使用 Edge Function
const uploadAnswerFile = async (file) => {
  answerFileName.value = file.name
  uploadingAnswers.value = true
  errorMessage.value = ''

  try {
    const base64 = await readFileAsBase64(file)
    
    const { data, error } = await supabase.functions.invoke('extract-pdf', {
      body: {
        file_data: base64,
        file_name: file.name,
        type: 'answers'
      }
    })

    if (error) throw new Error(error.message)

    answersData.value = data
    console.log('答案 PDF 解析成功:', data)

    // 如果已經有考卷資料，合併答案
    if (importResult.value && importResult.value.questions) {
      mergeAnswers()
    }
  } catch (error) {
    console.error('答案 PDF 上傳失敗:', error)
    errorMessage.value = error.message || '答案 PDF 上傳失敗'
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

  questions.forEach((question, index) => {
    if (answers && answers[index]) {
      question.correct_answer = answers[index]
    }
  })

  console.log('已合併答案:', questions)
}

// 確認匯入
const handleImportConfirm = () => {
  if (!importResult.value) return

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
}

.question-icon { background: var(--primary, #476996); }
.answer-icon { background: #10b981; }

.card-header-custom h6 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.dropzone {
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  background: #fff;
}

.dropzone.uploading { cursor: not-allowed; opacity: 0.7; }
.dropzone.uploaded { background: #f0fdf4; }

.upload-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon { color: var(--text-secondary, #64748B); opacity: 0.5; }

.success-icon {
  width: 48px;
  height: 48px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e5e7eb;
  border-top-color: var(--primary, #476996);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.state-text { font-size: 0.9rem; font-weight: 500; margin: 0; }
.state-subtext { font-size: 0.75rem; color: var(--text-secondary, #64748B); }

.result-container {
  margin: 0 1.5rem 1.5rem;
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: #f0fdf4;
  border-bottom: 2px solid #d1fae5;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #065f46;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-body { padding: 1.5rem; }

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
}

.info-item.highlight { background: #fef3c7; border-color: #fcd34d; }

.info-label { font-size: 0.75rem; color: var(--text-secondary); }
.info-value { font-size: 0.9rem; font-weight: 600; }

.preview-section { margin-bottom: 1.5rem; }

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
}

.preview-title { font-weight: 600; font-size: 0.875rem; }

.chevron { transition: transform 0.2s; }
.chevron.rotated { transform: rotate(180deg); }

.preview-list { padding: 1rem 0; }

.preview-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.question-number {
  width: 28px;
  height: 28px;
  background: var(--primary, #476996);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.question-text { font-size: 0.875rem; }

.options-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.option-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #e5e7eb;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn-confirm, .btn-cancel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm { background: var(--primary, #476996); color: #fff; }
.btn-cancel { background: #f3f4f6; color: var(--text-primary); }

.error-toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
}

.error-close {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0.25rem;
}

.result-fade-enter-active, .result-fade-leave-active { transition: all 0.3s; }
.result-fade-enter-from, .result-fade-leave-to { opacity: 0; transform: translateY(-10px); }

.preview-slide-enter-active, .preview-slide-leave-active { transition: all 0.3s; }
.preview-slide-enter-from, .preview-slide-leave-to { opacity: 0; max-height: 0; }

.error-fade-enter-active, .error-fade-leave-active { transition: all 0.3s; }
.error-fade-enter-from, .error-fade-leave-to { opacity: 0; transform: translateX(20px); }
</style>

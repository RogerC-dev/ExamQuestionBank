<template>
  <div class="card mb-4 ms-3 me-3">
    <div class="card-body">
      <h5 class="card-title mb-4">匯入試卷 PDF</h5>
      
      <!-- 上傳按鈕 -->
      <div class="d-flex gap-3 flex-wrap mb-4">
        <div>
          <label class="d-block mb-2">
            <input
              type="file"
              accept=".pdf"
              @change="handleQuestionPdfUpload"
              ref="questionFileInput"
              style="display: none"
            />
            <button
              type="button"
              class="btn btn-success"
              @click="$refs.questionFileInput.click()"
              :disabled="uploadingQuestions"
            >
              <span v-if="uploadingQuestions" class="spinner-border spinner-border-sm me-2"></span>
              {{ uploadingQuestions ? '匯入中...' : '匯入考卷 PDF' }}
            </button>
          </label>
          <small v-if="questionFileName" class="text-muted d-block">{{ questionFileName }}</small>
        </div>

        <div>
          <label class="d-block mb-2">
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
              <span v-if="uploadingAnswers" class="spinner-border spinner-border-sm me-2"></span>
              {{ uploadingAnswers ? '匯入中...' : '匯入答案 PDF' }}
            </button>
          </label>
          <small v-if="answerFileName" class="text-muted d-block">{{ answerFileName }}</small>
        </div>
      </div>

      <!-- 匯入結果顯示 -->
      <div v-if="importResult" class="card bg-light border-0">
        <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
          <h6 class="mb-0">匯入結果</h6>
          <button type="button" class="btn-close" @click="clearResult"></button>
        </div>

        <div class="card-body">
          <!-- 匯入資訊 -->
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">科目</small>
                <div>{{ importResult.subject || '-' }}</div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">分類</small>
                <div>{{ importResult.category || '-' }}</div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">難度</small>
                <div>{{ importResult.level || '-' }}</div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">時間限制</small>
                <div>{{ importResult.time_length ? `${importResult.time_length} 分鐘` : '-' }}</div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">題目數量</small>
                <div>{{ importResult.count || 0 }} 題</div>
              </div>
            </div>
            <div v-if="answersData" class="col-md-6">
              <div class="mb-2">
                <small class="text-muted fw-bold">答案狀態</small>
                <div class="text-success fw-bold">✓ 已匯入 ({{ answersData.count || 0 }} 個答案)</div>
              </div>
            </div>
          </div>

          <!-- 答案修改提醒 -->
          <div v-if="answersData && answersData.notes" class="alert alert-warning mb-4" role="alert">
            <strong>答案修改提醒</strong>
            <p class="mb-2">{{ answersData.notes }}</p>
            <div v-if="hasModifiedAnswers">
              <small class="fw-bold d-block mb-2">有答案修改的題目：</small>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="(answer, index) in answersData.answers"
                  :key="index"
                  v-show="answer === '*'"
                  class="badge bg-warning text-dark"
                >
                  第 {{ index + 1 }} 題
                </span>
              </div>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="d-flex gap-2">
            <button
              class="btn btn-primary"
              @click="handleImportConfirm"
            >
              確認使用此資料
            </button>
            <button class="btn btn-secondary" @click="clearResult">
              取消
            </button>
          </div>
        </div>
      </div>

      <!-- 錯誤訊息 -->
      <div v-if="errorMessage" class="alert alert-danger mt-3 mb-0" role="alert">
        {{ errorMessage }}
      </div>
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
/* Bootstrap 已提供大部分樣式，這裡只需要微調 */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}
</style>

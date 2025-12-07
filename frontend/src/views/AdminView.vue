<template>
  <div class="admin-view">
    <div class="container">
      <div class="admin-header">
        <h2 class="section-title">題庫管理後台</h2>
        <div class="admin-actions">
          <button class="btn btn-primary" @click="addExam">新增考卷</button>
          <button class="btn btn-primary" @click="batchImport" :disabled="isImporting">
            <span v-if="isImporting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            <span v-if="!isImporting">批次匯入</span>
            <span v-else>匯入中...</span>
          </button>
          <button class="btn btn-secondary" @click="exportExams" :disabled="isExporting">
            <span v-if="isExporting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            <span v-if="!isExporting">匯出考卷</span>
            <span v-else>匯出中...</span>
          </button>
          <!-- JSON import (hidden input) -->
          <input ref="jsonImportInput" type="file" accept="application/json" style="display:none" @change="handleImportFile" />
        </div>
      </div>

      <div class="exam-filters">
        <input
          v-model="searchTerm"
          type="text"
          class="form-control"
          placeholder="搜尋考卷名稱或說明"
          @keyup.enter="applyFilters"
        />

        <select v-model="ordering" class="form-select" @change="applyFilters">
          <option v-for="option in orderingOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <button class="btn btn-secondary" @click="resetFilters">重設條件</button>
        <button class="btn btn-primary" @click="applyFilters">搜尋</button>
      </div>

      <!-- Upload Area -->
      <div v-if="showUploadSection" class="upload-area" @click="handleUpload">
        <div class="upload-icon">[檔案]</div>
        <div class="upload-text">拖放檔案至此或點擊上傳</div>
        <div class="upload-hint">支援格式: JSON, CSV, PDF</div>
      </div>

      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>

      <!-- PDF 匯入模組 -->
      <!-- PDF 匯入模組需在考卷建立/編輯頁使用，admin 列表暫不顯示 -->

      <!-- Exam Table -->
      <div class="exam-table">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th>考卷 ID</th>
              <th>考卷名稱</th>
              <th>考試說明</th>
              <th>題數</th>
              <th>時間限制 (分)</th>
              <th>建立時間</th>
              <th>更新時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
              <td colspan="8" class="table-status">考卷資料載入中...</td>
            </tr>
            <tr v-else-if="!filteredExams.length">
              <td colspan="8" class="table-status">暫無符合條件的考卷</td>
            </tr>
            <tr v-else v-for="exam in filteredExams" :key="exam.id">
              <td>{{ exam.id }}</td>
              <td>{{ exam.name }}</td>
              <td>{{ exam.description }}</td>
              <td>{{ exam.questionCount }}</td>
              <td>{{ exam.timeLimit != null ? exam.timeLimit : '-' }}</td>
              <td>{{ exam.createdAt }}</td>
              <td>{{ exam.updatedAt }}</td>
              <td>
                <div class="dropdown">
                  <button
                    class="btn btn-sm btn-outline-secondary dropdown-toggle"
                    type="button"
                    :id="`dropdownExam${exam.id}`"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    操作
                  </button>
                  <ul class="dropdown-menu" :aria-labelledby="`dropdownExam${exam.id}`">
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="editExam(exam.id)">
                        編輯
                      </a>
                    </li>
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="viewExam(exam.id)">
                        檢視
                      </a>
                    </li>
                    <li><hr class="dropdown-divider" /></li>
                    <li>
                      <a
                        class="dropdown-item"
                        href="#"
                        :class="{ disabled: exportingExams[exam.id] }"
                        @click.prevent="exportExam(exam.id)"
                      >
                        <span v-if="exportingExams[exam.id]" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        <span v-if="!exportingExams[exam.id]">匯出</span>
                        <span v-else>匯出中...</span>
                      </a>
                    </li>
                    <li>
                      <a
                        class="dropdown-item text-danger"
                        href="#"
                        :class="{ disabled: deletingExamId === exam.id }"
                        @click.prevent="deleteExam(exam.id)"
                      >
                        <span v-if="deletingExamId === exam.id" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        <span v-if="!deletingExamId || deletingExamId !== exam.id">刪除</span>
                        <span v-else>刪除中...</span>
                      </a>
                    </li>
                  </ul>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav v-if="paginationState.hasPrev || paginationState.hasNext" class="d-flex justify-content-end align-items-center gap-3">
        <ul class="pagination mb-0">
          <li class="page-item" :class="{ disabled: !paginationState.hasPrev || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasPrev || isLoading" @click="goToPreviousPage">
              上一頁
            </button>
          </li>
          <li class="page-item disabled">
            <span class="page-link">第 {{ currentPage }} 頁</span>
          </li>
          <li class="page-item" :class="{ disabled: !paginationState.hasNext || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasNext || isLoading" @click="goToNextPage">
              下一頁
            </button>
          </li>
        </ul>
      </nav>

      <!-- Activity Log removed -->
    </div>

    <ExamDetailModal
      :visible="isExamDetailVisible"
      :exam="selectedExamDetail"
      :loading="isExamDetailLoading"
      :error="examDetailError"
      @close="closeExamDetail"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import PdfUploadSection from '@/components/PdfUploadSection.vue'
import questionService from '@/services/questionService'
import ExamDetailModal from '@/components/ExamDetailModal.vue'
import { usePdfImportStore } from '@/stores/pdfImport'
import examService from '@/services/examService'

const exams = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const searchTerm = ref('')
const ordering = ref('-created_at')
const currentPage = ref(1)
const paginationState = ref({ hasNext: false, hasPrev: false })
const selectedExamDetail = ref(null)
const isExamDetailVisible = ref(false)
const isExamDetailLoading = ref(false)
const examDetailError = ref('')
const deletingExamId = ref(null)
const showUploadSection = ref(false)
const isImporting = ref(false)
const isExporting = ref(false)
const exportingExams = reactive({})
// showActivityLog removed — no longer used

const filteredExams = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  if (!term) {
    return exams.value
  }

  return exams.value.filter((exam) => {
    const haystack = [
      exam.name,
      exam.description,
      exam.questionCount?.toString(),
      exam.timeLimit?.toString(),
      exam.createdAt,
      exam.updatedAt,
      exam.id?.toString()
    ]
      .filter(Boolean)
      .map((value) => value.toLowerCase())
      .join(' ')

    return haystack.includes(term)
  })
})

const orderingOptions = [
  { label: '最新建立', value: '-created_at' },
  { label: '最舊建立', value: 'created_at' },
  { label: '最近更新', value: '-updated_at' },
  { label: '名稱 (A-Z)', value: 'name' }
]

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const normalizeExam = (exam) => ({
  id: exam.id,
  name: exam.name,
  description: exam.description || '—',
  questionCount: exam.question_count ?? 0,
  timeLimit: exam.time_limit ?? null,
  createdAt: formatDateTime(exam.created_at),
  updatedAt: formatDateTime(exam.updated_at)
})

const normalizeExamDetail = (exam) => ({
  id: exam.id,
  name: exam.name,
  description: exam.description || '—',
  timeLimit: exam.time_limit ?? null,
  createdAt: formatDateTime(exam.created_at),
  updatedAt: formatDateTime(exam.updated_at),
  examQuestions: (exam.exam_questions ?? []).map((question, index) => ({
    id: question.id ?? index,
    order: question.order ?? index + 1,
    points: question.points ?? null,
    questionContent: question.question_content || '—',
    questionSubject: question.question_subject || '',
    questionCategory: question.question_category || ''
  }))
})

const fetchExams = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const params = { page: currentPage.value }
    const trimmedSearch = searchTerm.value.trim()

    if (trimmedSearch) {
      params.search = trimmedSearch
    }

    if (ordering.value) {
      params.ordering = ordering.value
    }

    const { data } = await examService.getExams(params)
    const list = Array.isArray(data) ? data : data.results ?? []

    exams.value = list.map(normalizeExam)

    if (Array.isArray(data)) {
      paginationState.value = { hasNext: false, hasPrev: false }
    } else {
      paginationState.value = {
        hasNext: Boolean(data.next),
        hasPrev: Boolean(data.previous) || currentPage.value > 1
      }
    }
  } catch (error) {
    console.error('Failed to fetch exams', error)
    errorMessage.value = error.response?.data?.detail || '取得考卷列表失敗，請稍後再試。'
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchExams()
}

const resetFilters = () => {
  searchTerm.value = ''
  ordering.value = '-created_at'
  currentPage.value = 1
  fetchExams()
}

const goToPreviousPage = () => {
  if (!paginationState.value.hasPrev || currentPage.value === 1) return
  currentPage.value -= 1
  fetchExams()
}

const goToNextPage = () => {
  if (!paginationState.value.hasNext) return
  currentPage.value += 1
  fetchExams()
}

// activities array removed — activity log UI removed

const addExam = () => {
  pdfImportStore.clearPayload()
  router.push('/admin/exams/new')
}

const jsonImportInput = ref(null)
const batchImport = () => {
  if (isImporting.value) return
  // trigger hidden file input for JSON import using vue ref
  if (jsonImportInput.value) {
    jsonImportInput.value.click()
  }
}

const exportExams = async () => {
  if (isExporting.value) return
  isExporting.value = true
  // Export all currently listed exams as JSON (fetch full details)
  try {
    const fetches = exams.value.map((e) => examService.getExam(e.id).catch(() => null))
    const responses = await Promise.all(fetches)
    const exportData = []
    for (const res of responses) {
      if (!res || !res.data) continue
      const item = res.data
      // fetch full question data for each question
      const detailedQuestions = []
      if (Array.isArray(item.exam_questions)) {
        for (const eq of item.exam_questions) {
          const qId = eq.question
          if (qId) {
            try {
              const qRes = await questionService.getQuestion(qId)
              detailedQuestions.push({
                order: eq.order,
                points: eq.points,
                question: qRes.data
              })
            } catch (err) {
              // fallback: include minimal info
              detailedQuestions.push({ order: eq.order, points: eq.points, question: { id: qId, content: eq.question_content } })
            }
          }
        }
      }
      exportData.push({
        id: item.id,
        name: item.name,
        description: item.description,
        time_limit: item.time_limit,
        created_at: item.created_at,
        updated_at: item.updated_at,
        exam_questions: detailedQuestions
      })
    }
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exams_export_${new Date().toISOString().slice(0, 19).replaceAll(':', '-')}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed', error)
    alert('匯出失敗，請檢查系統日誌')
  } finally {
    isExporting.value = false
  }
}

/**
 * Export single exam (for export button next to each exam)
 */
const exportExam = async (examId) => {
  if (exportingExams[examId]) return
  exportingExams[examId] = true
  try {
    const { data } = await examService.getExam(examId)
    const exportItem = {
      id: data.id,
      name: data.name,
      description: data.description,
      time_limit: data.time_limit,
      created_at: data.created_at,
      updated_at: data.updated_at,
      exam_questions: []
    }
    if (Array.isArray(data.exam_questions)) {
      for (const eq of data.exam_questions) {
        if (eq.question) {
          try {
            const qRes = await questionService.getQuestion(eq.question)
            exportItem.exam_questions.push({ order: eq.order, points: eq.points, question: qRes.data })
          } catch (err) {
            exportItem.exam_questions.push({ order: eq.order, points: eq.points, question: { id: eq.question, content: eq.question_content } })
          }
        }
      }
    }

    const blob = new Blob([JSON.stringify(exportItem, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exam_${exportItem.id || 'export'}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed', error)
    alert('匯出考卷失敗')
  }
  finally {
    exportingExams[examId] = false
  }
}

// viewLogs removed — button removed

const handleUpload = () => {
  alert('📁 檔案上傳功能 - 實際需實作檔案選擇')
}

const handleImportFile = async (event) => {
  if (isImporting.value) return
  isImporting.value = true
  const file = event.target.files && event.target.files[0]
  if (!file) {
    isImporting.value = false
    return
  }
  try {
    const text = await file.text()
    const parsed = JSON.parse(text)
    // allow both array (multiple exams) or single object
    const items = Array.isArray(parsed) ? parsed : [parsed]
    const summaries = []
    for (const it of items) {
      const result = await importExamFromJson(it)
      summaries.push(result)
    }
    // summarize results
    const successCount = summaries.filter(s => s && s.newExamId).length
    const createdQuestionTotal = summaries.reduce((acc, s) => acc + (s.createdQuestionCount || 0), 0)
    const totalFailedAdds = summaries.reduce((acc, s) => acc + (s.failedAdds?.length || 0), 0)
    alert(`匯入完成：建立 ${successCount} 張考卷，新增題目 ${createdQuestionTotal} 題，加入考卷失敗 ${totalFailedAdds} 筆`) 
    // refresh listing
    fetchExams()
  } catch (error) {
    console.error('Import failed', error)
    alert('匯入失敗：' + (error.message || '格式錯誤'))
  } finally {
    // reset file input
    event.target.value = ''
    isImporting.value = false
  }
}

const importExamFromJson = async (payload) => {
  if (!payload || !payload.name) {
    throw new Error('JSON 格式錯誤，缺少 exam.name')
  }
  // create exam
  const examData = {
    name: payload.name,
    description: payload.description || '',
    time_limit: payload.time_limit || null
  }
  const res = await examService.createExam(examData)
  const newExamId = res.data?.id
  if (!newExamId) throw new Error('建立考卷失敗')

  // prepare questions
  const toCreate = []
  const toUseExisting = []
  if (Array.isArray(payload.exam_questions)) {
      for (const eq of payload.exam_questions) {
      if (eq.question && eq.question.id && (!eq.question.content && !eq.question.options)) {
        // reference to existing question
        // Verify existence of question id before adding
        try {
          const exists = await questionService.getQuestion(eq.question.id).catch(() => null)
          if (exists && exists.data) {
            toUseExisting.push({ question: eq.question.id, order: eq.order, points: eq.points })
          } else {
            console.warn('Referenced question id not found; skipping', eq.question.id)
            // if we have embedded content fallback, try to create later
            if (eq.question && (eq.question.content || eq.question.options)) {
              const q = eq.question
              const qPayload = {
                subject: q.subject || '',
                category: q.category || '',
                question_type: q.question_type || '選擇題',
                difficulty: q.difficulty || 'medium',
                content: q.content || q.question_content || '',
                explanation: q.explanation || q.explain || '',
                status: q.status || 'published',
                options: q.options || [],
                tag_ids: q.tag_ids || q.tags || []
              }
              toCreate.push({ qPayload, order: eq.order, points: eq.points })
            }
          }
        } catch (err) {
          console.error('Failed to verify referenced question id', err)
        }
      } else if (eq.question) {
        // has embedded question object with full data
        // prepare create payload for question service
        const q = eq.question
        const qPayload = {
          subject: q.subject || '',
          category: q.category || '',
          question_type: q.question_type || '選擇題',
          difficulty: q.difficulty || 'medium',
          content: q.content || q.question_content || '',
          explanation: q.explanation || q.explain || '',
          status: q.status || 'published',
          options: q.options || [],
          tag_ids: q.tag_ids || q.tags || []
        }
        toCreate.push({ qPayload, order: eq.order, points: eq.points })
      }
    }
  }

  // create questions in bulk
  const createdQuestionIds = []
  if (toCreate.length > 0) {
    const payloadForBulk = toCreate.map(t => t.qPayload)
    try {
        const createRes = await questionService.bulkCreateQuestions(payloadForBulk)
        const results = createRes.data?.results || createRes.data || []
        const failedIndices = []
        for (let i = 0; i < results.length; i++) {
          const r = results[i]
          if (r && r.success && r.id) {
            createdQuestionIds.push({ id: r.id, order: toCreate[i].order, points: toCreate[i].points })
          } else {
            // collect failed indices for retry
            failedIndices.push(i)
          }
        }
        // retry failures one by one with stripped tag_ids to avoid missing tag errors
        for (const idx of failedIndices) {
          const original = toCreate[idx]
          const attemptPayload = { ...original.qPayload }
          // remove tag_ids if present
          if (attemptPayload.tag_ids) delete attemptPayload.tag_ids
          try {
            const singleRes = await questionService.createQuestion(attemptPayload)
            if (singleRes?.data?.id) {
              createdQuestionIds.push({ id: singleRes.data.id, order: original.order, points: original.points })
            }
          } catch (retryErr) {
            console.error('Retry create question failed (stripped tags), skipping index', idx, retryErr)
          }
        }
      } catch (err) {
      // fallback to single create
      for (let i = 0; i < toCreate.length; i++) {
        try {
          const createRes = await questionService.createQuestion(toCreate[i].qPayload)
          createdQuestionIds.push({ id: createRes.data.id, order: toCreate[i].order, points: toCreate[i].points })
        } catch (err2) {
          console.error('Failed to create question, skipping', err2)
          // try fallback without tags
          try {
            const fallback = { ...toCreate[i].qPayload }
            if (fallback.tag_ids) delete fallback.tag_ids
            const fallbackRes = await questionService.createQuestion(fallback)
            createdQuestionIds.push({ id: fallbackRes.data.id, order: toCreate[i].order, points: toCreate[i].points })
          } catch (fallbackErr) {
            console.error('Fallback create failed too', fallbackErr)
          }
        }
      }
    }
  }

  // add existing and created questions to exam
  const adds = []
  for (const ex of toUseExisting) adds.push(ex)
  for (const c of createdQuestionIds) adds.push({ question: c.id, order: c.order, points: c.points })
  const failedAdds = []
  for (const add of adds) {
    try {
      await examService.addQuestionToExam(newExamId, add)
    } catch (err) {
      console.error('Failed to add question to exam', err)
      // if failure due to duplicate order, try without order
      try {
        if (typeof add.order !== 'undefined') {
          const addNoOrder = { question: add.question, points: add.points }
          await examService.addQuestionToExam(newExamId, addNoOrder)
          continue
        }
      } catch (err2) {
        console.error('Failed to add without order fallback', err2)
      }
      failedAdds.push({ add, error: err })
    }
  }

  return { newExamId, createdQuestionCount: createdQuestionIds.length, failedAdds }
}

const router = useRouter()
const pdfImportStore = usePdfImportStore()

const handlePdfImportFromAdmin = (payload) => {
  pdfImportStore.setPayload(payload)
  alert('匯入成功，將前往考卷編輯頁面以完成設定。')
  router.push('/admin/exams/new?source=pdf')
}

const editExam = (id) => {
  router.push(`/admin/exams/${id}/edit`)
}

const viewExam = async (id) => {
  isExamDetailVisible.value = true
  isExamDetailLoading.value = true
  examDetailError.value = ''
  selectedExamDetail.value = null

  try {
    const { data } = await examService.getExam(id)
    selectedExamDetail.value = normalizeExamDetail(data)
  } catch (error) {
    console.error('Failed to load exam detail', error)
    examDetailError.value = error.response?.data?.detail || '無法取得考卷詳細資訊。'
  } finally {
    isExamDetailLoading.value = false
  }
}

const closeExamDetail = () => {
  isExamDetailVisible.value = false
  selectedExamDetail.value = null
  examDetailError.value = ''
}

const deleteExam = async (id) => {
  if (!confirm('確定要刪除此考卷嗎？')) {
    return
  }

  deletingExamId.value = id

  try {
    await examService.deleteExam(id)
    alert('考卷已刪除')

    // 若刪除後頁面無資料且非第一頁，回上一頁再重新載入
    await fetchExams()
    if (!exams.value.length && currentPage.value > 1) {
      currentPage.value -= 1
      await fetchExams()
    }
  } catch (error) {
    console.error('刪除考卷失敗', error)
    alert(error.response?.data?.detail || '刪除考卷失敗，請稍後再試。')
  } finally {
    deletingExamId.value = null
  }
}

onMounted(() => {
  fetchExams()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.admin-actions {
  display: flex;
  gap: 12px;
}

.exam-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.filter-input,
.filter-select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.filter-input {
  flex: 1;
  min-width: 220px;
}

.filter-select {
  width: 220px;
  background: #fff;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 14px;
}

.alert-error {
  background: #fdecea;
  border: 1px solid #f5c2c7;
  color: #842029;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.upload-area {
  background: white;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 60px;
  text-align: center;
  margin-bottom: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.upload-icon {
  font-size: 64px;
  color: #cbd5e0;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 14px;
  color: #999;
}

.pdf-upload-wrapper {
  margin-bottom: 30px;
}

.exam-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

.table-status {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 30px;
}

.page-indicator {
  font-size: 14px;
  color: #4a5568;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  border-bottom: 2px solid #e0e0e0;
}

/* 設定各欄位寬度 */
th:nth-child(1), td:nth-child(1) { width: 8%; }        /* 考卷 ID */
th:nth-child(2), td:nth-child(2) { width: 15%; }       /* 考卷名稱 */
th:nth-child(3), td:nth-child(3) { width: 25%; }       /* 考試說明 */
th:nth-child(4), td:nth-child(4) { width: 8%; }        /* 題數 */
th:nth-child(5), td:nth-child(5) { width: 12%; }       /* 時間限制 */
th:nth-child(6), td:nth-child(6) { width: 15%; }       /* 建立時間 */
th:nth-child(7), td:nth-child(7) { width: 15%; }       /* 更新時間 */
th:nth-child(8), td:nth-child(8) { width: 2%; }        /* 操作 */

td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
}

tr:hover {
  background: #f8f9fa;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: #666;
  padding: 8px;
  transition: color 0.3s;
}

.icon-btn:hover {
  color: #007bff;
}

.icon-btn:disabled {
  cursor: not-allowed;
  color: #c0c4cc;
}

.activity-log {
  background: white;
  padding: 24px;
  border-radius: 8px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-left: 3px solid #007bff;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 12px;
}

.activity-icon {
  font-size: 20px;
  color: #007bff;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.activity-meta {
  font-size: 13px;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .admin-actions {
    flex-wrap: wrap;
  }

  .exam-filters {
    flex-direction: column;
  }

  .filter-select,
  .filter-input {
    width: 100%;
  }
}
</style>

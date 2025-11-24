<template>
  <div class="admin-view">
    <div class="container">
      <div class="admin-header">
        <h2 class="section-title">題庫管理後台</h2>
        <div class="admin-actions">
          <button class="btn btn-primary" @click="addExam">新增考卷</button>
          <button class="btn btn-primary" @click="batchImport">批次匯入</button>
          <button class="btn btn-secondary" @click="exportExams">匯出考卷</button>
          <button class="btn btn-secondary" @click="viewLogs">查看日誌</button>
        </div>
      </div>

      <div class="exam-filters">
        <input
          v-model="searchTerm"
          type="text"
          class="filter-input"
          placeholder="搜尋考卷名稱或說明"
          @keyup.enter="applyFilters"
        />

        <select v-model="ordering" class="filter-select" @change="applyFilters">
          <option v-for="option in orderingOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <button class="btn btn-secondary" @click="resetFilters">重設條件</button>
        <button class="btn btn-primary" @click="applyFilters">搜尋</button>
      </div>

      <!-- Upload Area -->
      <div v-if="showUploadSection" class="upload-area" @click="handleUpload">
        <div class="upload-icon">📁</div>
        <div class="upload-text">拖放檔案至此或點擊上傳</div>
        <div class="upload-hint">支援格式: JSON, CSV, PDF</div>
      </div>

      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- PDF 匯入模組 -->
      <!-- PDF 匯入模組需在考卷建立/編輯頁使用，admin 列表暫不顯示 -->

      <!-- Exam Table -->
      <div class="exam-table">
        <table>
          <thead>
            <tr>
              <th>考卷 ID</th>
              <th>考卷名稱</th>
              <th>考試說明</th>
              <th>題數</th>
              <th>時間限制 (分鐘)</th>
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
                <button class="icon-btn" @click="editExam(exam.id)">✏️</button>
                <button class="icon-btn" @click="viewExam(exam.id)">👁️</button>
                <button
                  class="icon-btn"
                  :disabled="deletingExamId === exam.id"
                  :aria-busy="deletingExamId === exam.id"
                  @click="deleteExam(exam.id)"
                >
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-controls" v-if="paginationState.hasPrev || paginationState.hasNext">
        <button class="btn btn-secondary" :disabled="!paginationState.hasPrev || isLoading" @click="goToPreviousPage">
          上一頁
        </button>
        <span class="page-indicator">第 {{ currentPage }} 頁</span>
        <button class="btn btn-secondary" :disabled="!paginationState.hasNext || isLoading" @click="goToNextPage">
          下一頁
        </button>
      </div>

      <!-- Activity Log -->
      <div v-if="showActivityLog" class="activity-log">
        <h3 class="section-title">操作紀錄</h3>
        <div v-for="activity in activities" :key="activity.id" class="activity-item">
          <div class="activity-icon">{{ activity.icon }}</div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-meta">{{ activity.meta }}</div>
          </div>
        </div>
      </div>
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PdfUploadSection from '@/components/PdfUploadSection.vue'
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
const showActivityLog = ref(false)

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

const activities = ref([
  {
    id: 1,
    icon: '✏️',
    title: '考卷 #301 已更新',
    meta: '管理員 admin@example.com | 2024.03.20 14:30'
  },
  {
    id: 2,
    icon: '📤',
    title: '批次匯入 3 份考卷成功',
    meta: '管理員 admin@example.com | 2024.03.20 10:15'
  }
])

const addExam = () => {
  pdfImportStore.clearPayload()
  router.push('/admin/exams/new')
}

const batchImport = () => {
  alert('批次匯入')
}

const exportExams = () => {
  alert('匯出考卷')
}

const viewLogs = () => {
  alert('查看日誌')
}

const handleUpload = () => {
  alert('📁 檔案上傳功能 - 實際需實作檔案選擇')
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

td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
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

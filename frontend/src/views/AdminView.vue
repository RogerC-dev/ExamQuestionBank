<template>
  <div class="admin-view">
    <div class="container">
      <div class="admin-header">
        <div class="header-top">
          <div class="header-title-section">
            <h2 class="section-title">題庫管理後台</h2>
            <p class="section-subtitle">管理考卷與題目資料</p>
          </div>
          <div class="admin-actions">
            <template v-if="currentTab === 'exams'">
              <button class="action-btn action-btn-secondary" @click="batchImport" :disabled="isImporting">
                <div v-if="isImporting" class="btn-spinner"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                <span>{{ isImporting ? '匯入中...' : '匯入考卷' }}</span>
              </button>
              <button class="action-btn action-btn-primary" @click="addExam">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                <span>新增考卷</span>
              </button>
              <input ref="jsonImportInput" type="file" accept="application/json" style="display:none" @change="handleImportFile" />
            </template>
            <template v-else>
              <button class="action-btn action-btn-secondary" @click="importQuestions" :disabled="isImportingQuestions">
                <div v-if="isImportingQuestions" class="btn-spinner"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                <span>{{ isImportingQuestions ? '匯入中...' : '匯入題目' }}</span>
              </button>
              <button class="action-btn action-btn-primary" @click="addQuestion">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                <span>新增題目</span>
              </button>
              <input ref="questionImportInput" type="file" accept="application/json" style="display:none" @change="handleQuestionImportFile" />
            </template>
          </div>
        </div>
        <div class="admin-tabs">
          <button :class="['tab-btn', { active: currentTab === 'exams' }]" @click="setTab('exams')">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <span>考卷管理</span>
          </button>
          <button :class="['tab-btn', { active: currentTab === 'questions' }]" @click="setTab('questions')">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <span>題目管理</span>
          </button>
        </div>
      </div>

      <!-- Main Content: exams or questions -->
      <div v-if="currentTab === 'exams'">
        <!-- Exam Filters -->
        <div class="exam-filters">
          <div class="filter-search">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <input
              v-model="searchTerm"
              type="text"
              class="filter-input"
              placeholder="搜尋考卷名稱或說明..."
              @keyup.enter="applyFilters"
            />
          </div>

          <div class="filter-select-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="select-icon">
              <line x1="4" y1="21" x2="4" y2="14"></line>
              <line x1="4" y1="10" x2="4" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12" y2="3"></line>
              <line x1="20" y1="21" x2="20" y2="16"></line>
              <line x1="20" y1="12" x2="20" y2="3"></line>
              <line x1="1" y1="14" x2="7" y2="14"></line>
              <line x1="9" y1="8" x2="15" y2="8"></line>
              <line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
            <select v-model="ordering" class="filter-select" @change="applyFilters">
              <option v-for="option in orderingOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <button class="filter-btn filter-btn-reset" @click="resetFilters">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="1 4 1 10 7 10"></polyline>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
            </svg>
            <span>重設</span>
          </button>
          <button class="filter-btn filter-btn-search" @click="applyFilters">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <span>搜尋</span>
          </button>
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
                      <button class="dropdown-item" type="button" @click="editExam(exam.id)">
                        編輯
                      </button>
                    </li>
                    <li>
                      <button class="dropdown-item" type="button" @click="viewExam(exam.id)">
                        檢視
                      </button>
                    </li>
                    <li><hr class="dropdown-divider" /></li>
                    <li>
                      <button
                        class="dropdown-item"
                        type="button"
                        :disabled="exportingExams[exam.id]"
                        :aria-disabled="exportingExams[exam.id]"
                        @click="exportExam(exam.id)"
                      >
                        <span v-if="exportingExams[exam.id]" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        <span v-if="!exportingExams[exam.id]">匯出</span>
                        <span v-else>匯出中...</span>
                      </button>
                    </li>
                    <li>
                      <button
                        class="dropdown-item text-danger"
                        type="button"
                        :disabled="deletingExamId === exam.id"
                        :aria-disabled="deletingExamId === exam.id"
                        @click="deleteExam(exam.id)"
                      >
                        <span v-if="deletingExamId === exam.id" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        <span v-if="!deletingExamId || deletingExamId !== exam.id">刪除</span>
                        <span v-else>刪除中...</span>
                      </button>
                    </li>
                  </ul>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <div v-else>
        <AdminQuestionManagement />
      </div>

      <!-- Enhanced Pagination -->
      <nav v-if="currentTab === 'exams' && paginationState.totalPages > 0" class="pagination-wrapper">
        <div class="pagination-info">
          <span class="text-muted">
            共 {{ paginationState.totalCount }} 筆 | 第 {{ currentPage }} / {{ paginationState.totalPages }} 頁
          </span>
          <select v-model="pageSize" class="form-select form-select-sm page-size-select" @change="onPageSizeChange">
            <option :value="10">每頁 10 筆</option>
            <option :value="20">每頁 20 筆</option>
            <option :value="50">每頁 50 筆</option>
            <option :value="100">每頁 100 筆</option>
          </select>
        </div>

        <ul class="pagination mb-0">
          <li class="page-item" :class="{ disabled: !paginationState.hasPrev || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasPrev || isLoading" @click="goToFirstPage" title="第一頁">
              <span aria-hidden="true">&laquo;</span>
            </button>
          </li>
          <li class="page-item" :class="{ disabled: !paginationState.hasPrev || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasPrev || isLoading" @click="goToPreviousPage" title="上一頁">
              <span aria-hidden="true">&lsaquo;</span>
            </button>
          </li>

          <!-- Page Numbers -->
          <li 
            v-for="page in visiblePages" 
            :key="page" 
            class="page-item" 
            :class="{ active: page === currentPage, disabled: isLoading }"
          >
            <button 
              class="page-link" 
              :disabled="isLoading"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </li>

          <li class="page-item" :class="{ disabled: !paginationState.hasNext || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasNext || isLoading" @click="goToNextPage" title="下一頁">
              <span aria-hidden="true">&rsaquo;</span>
            </button>
          </li>
          <li class="page-item" :class="{ disabled: !paginationState.hasNext || isLoading }">
            <button class="page-link" :disabled="!paginationState.hasNext || isLoading" @click="goToLastPage" title="最後一頁">
              <span aria-hidden="true">&raquo;</span>
            </button>
          </li>
        </ul>

        <div class="page-jumper">
          <span class="text-muted me-2">跳至</span>
          <input 
            v-model.number="jumpToPage" 
            type="number" 
            class="form-control form-control-sm" 
            :min="1" 
            :max="paginationState.totalPages"
            @keyup.enter="handlePageJump"
            placeholder="頁碼"
          />
          <button 
            class="btn btn-sm btn-secondary" 
            :disabled="isLoading || !isValidJumpPage"
            @click="handlePageJump"
          >
            前往
          </button>
        </div>
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

    <!-- Export Progress Modal -->
    <div v-if="isExportProgressVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">考卷匯出中</h5>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <p class="mb-2">正在匯出考卷...</p>
              <div class="progress">
                <div
                  class="progress-bar progress-bar-striped progress-bar-animated"
                  role="progressbar"
                  :style="{ width: exportProgress + '%' }"
                  :aria-valuenow="exportProgress"
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  {{ exportProgress }}%
                </div>
              </div>
            </div>
            <p class="text-muted small">{{ exportProgressText }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Progress Modal -->
    <div v-if="isImportProgressVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">考卷匯入中</h5>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <p class="mb-2">正在匯入考卷...</p>
              <div class="progress">
                <div
                  class="progress-bar progress-bar-striped progress-bar-animated bg-success"
                  role="progressbar"
                  :style="{ width: importProgress + '%' }"
                  :aria-valuenow="importProgress"
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  {{ importProgress }}%
                </div>
              </div>
            </div>
            <p class="text-muted small">{{ importProgressText }}</p>
          </div>
        </div>
      </div>
    </div>
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
import AdminQuestionManagement from '@/components/AdminQuestionManagement.vue'

const exams = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const currentTab = ref('exams')
const searchTerm = ref('')
const ordering = ref('-created_at')
const currentPage = ref(1)
const pageSize = ref(20)
const paginationState = ref({ 
  hasNext: false, 
  hasPrev: false, 
  totalPages: 0, 
  totalCount: 0 
})
const jumpToPage = ref(null)
const selectedExamDetail = ref(null)
const isExamDetailVisible = ref(false)
const isExamDetailLoading = ref(false)
const examDetailError = ref('')
const deletingExamId = ref(null)
const showUploadSection = ref(false)
const isImporting = ref(false)
const isExporting = ref(false)
const exportingExams = reactive({})
const isExportProgressVisible = ref(false)
const exportProgress = ref(0)
const exportProgressText = ref('')
const isImportProgressVisible = ref(false)
const importProgress = ref(0)
const importProgressText = ref('')
const totalImportQuestions = ref(0)
const completedImportQuestions = ref(0)
// showActivityLog removed — no longer used

// Question management refs
const questionImportInput = ref(null)
const isImportingQuestions = ref(false)
const questionManagementRef = ref(null)

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
    const params = { 
      page: currentPage.value,
      page_size: pageSize.value
    }
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

    // Update pagination state
    if (Array.isArray(data)) {
      paginationState.value = { 
        hasNext: false, 
        hasPrev: false, 
        totalPages: 1, 
        totalCount: data.length 
      }
    } else {
      const count = data.count || 0
      const totalPages = Math.ceil(count / pageSize.value)
      paginationState.value = {
        hasNext: Boolean(data.next),
        hasPrev: Boolean(data.previous) || currentPage.value > 1,
        totalPages: totalPages || 1,
        totalCount: count
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

const goToFirstPage = () => { 
  if (currentPage.value === 1 || isLoading.value) return
  currentPage.value = 1
  fetchExams() 
}

const goToPreviousPage = () => {
  if (!paginationState.value.hasPrev || currentPage.value === 1 || isLoading.value) return
  currentPage.value -= 1
  fetchExams()
}

const goToNextPage = () => {
  if (!paginationState.value.hasNext || isLoading.value) return
  currentPage.value += 1
  fetchExams()
}

const goToLastPage = () => { 
  if (currentPage.value === paginationState.value.totalPages || isLoading.value) return
  currentPage.value = paginationState.value.totalPages
  fetchExams() 
}

const goToPage = (page) => {
  if (page === currentPage.value || isLoading.value) return
  if (page < 1 || page > paginationState.value.totalPages) return
  currentPage.value = page
  fetchExams()
}

const handlePageJump = () => {
  if (!isValidJumpPage.value || isLoading.value) return
  currentPage.value = jumpToPage.value
  jumpToPage.value = null
  fetchExams()
}

const onPageSizeChange = () => {
  currentPage.value = 1
  fetchExams()
}

// Computed property for visible page numbers
const visiblePages = computed(() => {
  const total = paginationState.value.totalPages
  const current = currentPage.value
  const pages = []
  
  if (total <= 7) {
    // Show all pages if total <= 7
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)
    
    if (current > 3) {
      pages.push('...')
    }
    
    // Show pages around current page
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    
    for (let i = start; i <= end; i++) {
      if (i !== 1 && i !== total) {
        pages.push(i)
      }
    }
    
    if (current < total - 2) {
      pages.push('...')
    }
    
    // Always show last page
    if (total > 1) {
      pages.push(total)
    }
  }
  
  return pages.filter((p, i, arr) => {
    // Remove duplicate ellipsis
    if (p === '...' && arr[i - 1] === '...') return false
    return true
  })
})

const isValidJumpPage = computed(() => {
  return jumpToPage.value >= 1 && jumpToPage.value <= paginationState.value.totalPages && jumpToPage.value !== currentPage.value
})

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
  isExportProgressVisible.value = true
  exportProgress.value = 0
  exportProgressText.value = '取得考卷資訊...'
  
  try {
    const { data } = await examService.getExam(examId)
    exportProgress.value = 20
    exportProgressText.value = '讀取題目...'
    
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
      const totalQuestions = data.exam_questions.length
      for (let i = 0; i < data.exam_questions.length; i++) {
        const eq = data.exam_questions[i]
        if (eq.question) {
          try {
            const qRes = await questionService.getQuestion(eq.question)
            exportItem.exam_questions.push({ order: eq.order, points: eq.points, question: qRes.data })
          } catch (err) {
            exportItem.exam_questions.push({ order: eq.order, points: eq.points, question: { id: eq.question, content: eq.question_content } })
          }
        }
        // Update progress: 20-80% for fetching questions
        exportProgress.value = 20 + Math.floor((i + 1) / totalQuestions * 60)
        exportProgressText.value = `已讀取 ${i + 1}/${totalQuestions} 題...`
      }
    }

    exportProgress.value = 85
    exportProgressText.value = '準備下載...'

    const blob = new Blob([JSON.stringify(exportItem, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exam_${exportItem.id || 'export'}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    exportProgress.value = 100
    exportProgressText.value = '匯出完成'
    
    // Close modal after 1 second
    setTimeout(() => {
      isExportProgressVisible.value = false
      exportProgress.value = 0
      exportProgressText.value = ''
    }, 1000)
  } catch (error) {
    console.error('Export failed', error)
    alert('匯出考卷失敗')
    isExportProgressVisible.value = false
    exportProgress.value = 0
    exportProgressText.value = ''
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
  isImportProgressVisible.value = true
  importProgress.value = 0
  importProgressText.value = '解析檔案中...'
  totalImportQuestions.value = 0
  completedImportQuestions.value = 0
  
  const file = event.target.files && event.target.files[0]
  if (!file) {
    isImporting.value = false
    isImportProgressVisible.value = false
    return
  }
  try {
    const text = await file.text()
    const parsed = JSON.parse(text)
    importProgress.value = 10
    importProgressText.value = '準備匯入...'
    
    // allow both array (multiple exams) or single object
    const items = Array.isArray(parsed) ? parsed : [parsed]
    
    // First pass: count total questions
    let totalQuestions = 0
    for (const item of items) {
      if (Array.isArray(item.exam_questions)) {
        totalQuestions += item.exam_questions.length
      }
    }
    totalImportQuestions.value = totalQuestions
    completedImportQuestions.value = 0
    
    const summaries = []
    
    for (let i = 0; i < items.length; i++) {
      const onQuestionProgress = (completed, total) => {
        completedImportQuestions.value = completed
        const percentage = totalQuestions > 0 ? Math.floor((completedImportQuestions.value / totalQuestions) * 80) : 0
        importProgress.value = 10 + percentage
        importProgressText.value = `已匯入 ${completedImportQuestions.value}/${totalQuestions} 題...`
      }
      
      const result = await importExamFromJson(items[i], onQuestionProgress)
      summaries.push(result)
      // Update progress: 10-90% for processing exams
      importProgress.value = 10 + Math.floor((i + 1) / items.length * 80)
      importProgressText.value = `已完成 ${i + 1}/${items.length} 張考卷，共 ${completedImportQuestions.value}/${totalQuestions} 題`
    }
    
    importProgress.value = 95
    importProgressText.value = '整理資料中...'
    
    // summarize results
    const successCount = summaries.filter(s => s && s.newExamId).length
    const createdQuestionTotal = summaries.reduce((acc, s) => acc + (s.createdQuestionCount || 0), 0)
    const totalFailedAdds = summaries.reduce((acc, s) => acc + (s.failedAdds?.length || 0), 0)
    
    importProgress.value = 100
    importProgressText.value = '匯入完成'
    
    // Close modal after 1 second
    setTimeout(() => {
      isImportProgressVisible.value = false
      importProgress.value = 0
      importProgressText.value = ''
      totalImportQuestions.value = 0
      completedImportQuestions.value = 0
      alert(`匯入完成：建立 ${successCount} 張考卷，新增題目 ${createdQuestionTotal} 題，加入考卷失敗 ${totalFailedAdds} 筆`)
      // refresh listing
      fetchExams()
    }, 1000)
  } catch (error) {
    console.error('Import failed', error)
    isImportProgressVisible.value = false
    importProgress.value = 0
    importProgressText.value = ''
    totalImportQuestions.value = 0
    completedImportQuestions.value = 0
    alert('匯入失敗：' + (error.message || '格式錯誤'))
  } finally {
    // reset file input
    event.target.value = ''
    isImporting.value = false
  }
}

const importExamFromJson = async (payload, onProgressUpdate) => {
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
              // Clean up options: remove id field and ensure proper order
              const cleanedOptions = (q.options || []).map((opt, idx) => {
                // Ensure order is unique and sequential
                const order = Array.isArray(q.options) && q.options.every(o => o.order === 0 || o.order === undefined) 
                  ? idx 
                  : (typeof opt.order === 'number' && opt.order !== undefined ? opt.order : idx)
                return {
                  content: opt.content || '',
                  is_correct: opt.is_correct === true,
                  order: order
                }
              })
              const qPayload = {
                subject: q.subject || '',
                question_type: q.question_type || '選擇題',
                difficulty: q.difficulty || 'medium',
                content: q.content || q.question_content || '',
                options: cleanedOptions
              }
              // Only add optional fields if they have meaningful values
              if (q.explanation || q.explain) {
                qPayload.explanation = q.explanation || q.explain
              }
              if (q.category && q.category.trim()) {
                qPayload.category = q.category
              }
              if (q.tag_ids && q.tag_ids.length > 0) {
                qPayload.tag_ids = q.tag_ids.filter(id => id)
              }
              if (q.status && q.status !== 'draft') {
                qPayload.status = q.status
              }
              console.log('Fallback qPayload:', qPayload)
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
        // Clean up options: remove id field and ensure proper order
        const cleanedOptions = (q.options || []).map((opt, idx) => {
          // Ensure order is unique and sequential
          const order = Array.isArray(q.options) && q.options.every(o => o.order === 0 || o.order === undefined) 
            ? idx 
            : (typeof opt.order === 'number' && opt.order !== undefined ? opt.order : idx)
          return {
            content: opt.content || '',
            is_correct: opt.is_correct === true,
            order: order
          }
        })
        const qPayload = {
          subject: q.subject || '',
          question_type: q.question_type || '選擇題',
          difficulty: q.difficulty || 'medium',
          content: q.content || q.question_content || '',
          options: cleanedOptions
        }
        // Only add optional fields if they have meaningful values
        if (q.explanation || q.explain) {
          qPayload.explanation = q.explanation || q.explain
        }
        if (q.category && q.category.trim()) {
          qPayload.category = q.category
        }
        if (q.tag_ids && q.tag_ids.length > 0) {
          qPayload.tag_ids = q.tag_ids.filter(id => id)
        }
        if (q.status && q.status !== 'draft') {
          qPayload.status = q.status
        }
        toCreate.push({ qPayload, order: eq.order, points: eq.points })
      }
    }
  }

  const totalQuestions = toCreate.length + toUseExisting.length
  console.log(`importExamFromJson: totalQuestions=${totalQuestions}, toCreate=${toCreate.length}, toUseExisting=${toUseExisting.length}`)

  // create questions in bulk
  const createdQuestionIds = []
  if (toCreate.length > 0) {
    const payloadForBulk = toCreate.map(t => t.qPayload)
    try {
        const createRes = await questionService.bulkCreateQuestions(payloadForBulk)
        const results = createRes.data?.results || createRes.data || []
        console.log(`bulkCreateQuestions results:`, results)
        const failedIndices = []
        for (let i = 0; i < results.length; i++) {
          const r = results[i]
          if (r && r.success && r.id) {
            createdQuestionIds.push({ id: r.id, order: toCreate[i].order, points: toCreate[i].points })
            console.log(`Created question ${i}: id=${r.id}`)
            if (onProgressUpdate) {
              onProgressUpdate(createdQuestionIds.length + toUseExisting.length, totalQuestions)
            }
          } else {
            // collect failed indices for retry
            failedIndices.push(i)
            console.log(`Failed to create question ${i}:`, r)
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
              console.log(`Retry created question ${idx}: id=${singleRes.data.id}`)
              if (onProgressUpdate) {
                onProgressUpdate(createdQuestionIds.length + toUseExisting.length, totalQuestions)
              }
            }
          } catch (retryErr) {
            console.error('Retry create question failed (stripped tags), skipping index', idx, retryErr)
          }
        }
      } catch (err) {
      console.error('bulkCreateQuestions failed, falling back to single create', err)
      // fallback to single create
      for (let i = 0; i < toCreate.length; i++) {
        try {
          const createRes = await questionService.createQuestion(toCreate[i].qPayload)
          createdQuestionIds.push({ id: createRes.data.id, order: toCreate[i].order, points: toCreate[i].points })
          console.log(`Single created question ${i}: id=${createRes.data.id}`)
          if (onProgressUpdate) {
            onProgressUpdate(createdQuestionIds.length + toUseExisting.length, totalQuestions)
          }
        } catch (err2) {
          console.error('Failed to create question, attempting fallback without tags', err2)
          // try fallback without tags and category
          try {
            const fallback = { ...toCreate[i].qPayload }
            if (fallback.tag_ids) delete fallback.tag_ids
            if (fallback.category) delete fallback.category
            console.log(`Fallback payload:`, fallback)
            const fallbackRes = await questionService.createQuestion(fallback)
            createdQuestionIds.push({ id: fallbackRes.data.id, order: toCreate[i].order, points: toCreate[i].points })
            console.log(`Fallback created question ${i}: id=${fallbackRes.data.id}`)
            if (onProgressUpdate) {
              onProgressUpdate(createdQuestionIds.length + toUseExisting.length, totalQuestions)
            }
          } catch (fallbackErr) {
            console.error('Fallback create failed too', fallbackErr, 'Payload was:', toCreate[i].qPayload)
          }
        }
      }
    }
  }

  // add existing and created questions to exam
  const adds = []
  for (const ex of toUseExisting) adds.push(ex)
  for (const c of createdQuestionIds) adds.push({ question: c.id, order: c.order, points: c.points })
  console.log(`Attempting to add ${adds.length} questions to exam ${newExamId}`)
  const failedAdds = []
  let successfulAdds = 0
  for (let i = 0; i < adds.length; i++) {
    const add = adds[i]
    try {
      const res = await examService.addQuestionToExam(newExamId, add)
      successfulAdds++
      console.log(`Added question ${i} (id=${add.question}) to exam, successful=${successfulAdds}`)
      if (onProgressUpdate) {
        onProgressUpdate(successfulAdds, totalQuestions)
      }
    } catch (err) {
      console.error('Failed to add question to exam', err)
      // if failure due to duplicate order, try without order
      try {
        if (typeof add.order !== 'undefined') {
          const addNoOrder = { question: add.question, points: add.points }
          const res = await examService.addQuestionToExam(newExamId, addNoOrder)
          successfulAdds++
          console.log(`Added question ${i} (id=${add.question}) to exam without order, successful=${successfulAdds}`)
          if (onProgressUpdate) {
            onProgressUpdate(successfulAdds, totalQuestions)
          }
          continue
        }
      } catch (err2) {
        console.error('Failed to add without order fallback', err2)
      }
      failedAdds.push({ add, error: err })
    }
  }
  console.log(`importExamFromJson finished: newExamId=${newExamId}, createdQuestions=${createdQuestionIds.length}, successfulAdds=${successfulAdds}, failedAdds=${failedAdds.length}`)

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

const setTab = (tab) => {
  currentTab.value = tab
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

// Question management functions
const addQuestion = () => {
  // Trigger child component method via event or ref
  const event = new CustomEvent('openCreateQuestion')
  window.dispatchEvent(event)
}

const importQuestions = () => {
  if (questionImportInput.value) {
    questionImportInput.value.click()
  }
}

const handleQuestionImportFile = async (event) => {
  if (isImportingQuestions.value) return
  const file = event.target.files && event.target.files[0]
  if (!file) return
  
  isImportingQuestions.value = true
  try {
    const text = await file.text()
    const parsed = JSON.parse(text)
    const items = Array.isArray(parsed) ? parsed : (parsed.questions ? parsed.questions : [parsed])
    
    const payload = items.map(q => ({
      subject: q.subject || '',
      category: q.category || '',
      question_type: q.question_type || '選擇題',
      difficulty: q.difficulty || 'medium',
      content: q.content || q.question_content || '',
      explanation: q.explanation || '',
      options: q.options || [],
      tag_ids: q.tag_ids || []
    }))

    try {
      await questionService.bulkCreateQuestions(payload)
    } catch (err) {
      for (const p of payload) {
        try { 
          await questionService.createQuestion(p) 
        } catch (e) { 
          console.error('create question fallback failed', e) 
        }
      }
    }
    
    alert('題目匯入完成')
    // Trigger child component to refresh
    const refreshEvent = new CustomEvent('refreshQuestions')
    window.dispatchEvent(refreshEvent)
  } catch (err) {
    console.error('Import questions failed', err)
    alert('匯入題目失敗: ' + (err?.message || '格式錯誤'))
  } finally {
    isImportingQuestions.value = false
    event.target.value = ''
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
  padding: 24px;
}

/* Admin Header */
.admin-header {
  margin-bottom: 32px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title-section {
  flex: 1;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #1E293B);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #64748B);
  margin: 0;
}

/* Action Buttons */
.admin-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-btn svg {
  flex-shrink: 0;
}

.action-btn-primary {
  background: var(--primary, #476996);
  color: white;
  box-shadow: 0 2px 4px rgba(71, 105, 150, 0.2);
}

.action-btn-primary:hover {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
}

.action-btn-secondary {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.action-btn-secondary:hover {
  background: #e5e7eb;
  color: var(--text-primary, #1E293B);
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 6px;
  background: #f3f4f6;
  border-radius: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary, #64748B);
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn svg {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary, #1E293B);
  background: rgba(255, 255, 255, 0.5);
}

.tab-btn:hover svg {
  opacity: 1;
}

.tab-btn.active {
  background: white;
  color: var(--primary, #476996);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tab-btn.active svg {
  opacity: 1;
}

/* Filters */
.exam-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border, #CBD5E1);
  flex-wrap: wrap;
}

.filter-search {
  position: relative;
  flex: 1;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary, #64748B);
  pointer-events: none;
}

.filter-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.filter-input:focus {
  outline: none;
  border-color: var(--primary, #476996);
  background: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.filter-select-wrapper {
  position: relative;
  min-width: 200px;
}

.select-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary, #64748B);
  pointer-events: none;
}

.filter-select {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary, #476996);
  background: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-btn svg {
  flex-shrink: 0;
}

.filter-btn-reset {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.filter-btn-reset:hover {
  background: #e5e7eb;
  color: var(--text-primary, #1E293B);
}

.filter-btn-search {
  background: var(--primary, #476996);
  color: white;
}

.filter-btn-search:hover {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
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

/* Upload Area */
.upload-area {
  background: white;
  border: 2px dashed var(--border, #CBD5E1);
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: var(--primary, #476996);
  background: var(--primary-soft, #EEF2FF);
}

.upload-icon {
  font-size: 64px;
  color: var(--text-secondary, #64748B);
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: var(--text-primary, #1E293B);
  font-weight: 500;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

.pdf-upload-wrapper {
  margin-bottom: 30px;
}

/* Table */
.exam-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border, #CBD5E1);
  margin-bottom: 24px;
}

.table-status {
  text-align: center;
  color: var(--text-secondary, #64748B);
  font-size: 14px;
  padding: 60px 20px !important;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: linear-gradient(to bottom, #f9fafb, #f3f4f6);
  border-bottom: 2px solid var(--border, #CBD5E1);
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
  color: var(--text-primary, #1E293B);
  overflow: visible;
  text-overflow: ellipsis;
}

tbody tr {
  transition: all 0.2s ease;
}

tbody tr:hover {
  background: var(--primary-soft, #EEF2FF);
}

tbody tr:last-child td {
  border-bottom: none;
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

/* Responsive */
@media (max-width: 1024px) {
  .header-top {
    flex-direction: column;
    align-items: stretch;
  }
  
  .admin-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .section-subtitle {
    font-size: 14px;
  }

  .admin-tabs {
    width: 100%;
  }

  .tab-btn {
    flex: 1;
    justify-content: center;
    padding: 10px 16px;
    font-size: 14px;
  }

  .tab-btn span {
    display: none;
  }

  .admin-actions {
    width: 100%;
    justify-content: space-between;
  }

  .action-btn span {
    display: none;
  }

  .action-btn {
    padding: 10px 14px;
  }

  .exam-filters {
    flex-direction: column;
    padding: 16px;
  }

  .filter-search,
  .filter-select-wrapper {
    width: 100%;
    min-width: auto;
  }

  .filter-btn {
    flex: 1;
  }

  .exam-table {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }
}

.admin-tabs {
  display:flex;
  gap:8px;
}
.tab-btn {
  background: #f1f5f9;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.tab-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

/* Enhanced Pagination Styles */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-size-select {
  width: auto;
  min-width: 120px;
}

.pagination {
  display: flex;
  gap: 4px;
}

.page-link {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dee2e6;
  color: #495057;
  background-color: #fff;
  transition: all 0.2s;
  cursor: pointer;
}

.page-link:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
  font-weight: 600;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-jumper input {
  width: 70px;
  text-align: center;
}

.page-jumper .btn {
  white-space: nowrap;
}

@media (max-width: 992px) {
  .pagination-wrapper {
    flex-direction: column;
    gap: 12px;
  }

  .pagination-info,
  .pagination,
  .page-jumper {
    width: 100%;
    justify-content: center;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .page-size-select {
    width: 100%;
  }
}
</style>

<template>
    <div class="exam-admin">
        <!-- Exam Filters -->
        <div class="exam-filters">
            <div class="filter-search">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" class="search-icon">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <input v-model="searchTerm" type="text" class="filter-input" placeholder="搜尋考卷名稱或說明..."
                    @keyup.enter="applyFilters" />
            </div>

            <div class="filter-select-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" class="select-icon">
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
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <polyline points="1 4 1 10 7 10"></polyline>
                    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                </svg>
                <span>重設</span>
            </button>
            <button class="filter-btn filter-btn-search" @click="applyFilters">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <span>搜尋</span>
            </button>
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
                        <th style="width:4%">
                            <input type="checkbox" :checked="isPageAllSelected" :disabled="isLoading"
                                @change="toggleSelectAllExams" aria-label="選取全部" />
                        </th>
                        <th style="width:8%">考卷 ID</th>
                        <th style="width:18%">考卷名稱</th>
                        <th style="width:28%">考試說明</th>
                        <th style="width:8%">題數</th>
                        <th style="width:10%">時間限制 (分)</th>
                        <th style="width:12%">建立時間</th>
                        <th style="width:12%">更新時間</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="isLoading">
                        <td colspan="9" class="table-status">考卷資料載入中...</td>
                    </tr>
                    <tr v-else-if="!filteredExams.length">
                        <td colspan="9" class="table-status">暫無符合條件的考卷</td>
                    </tr>
                    <tr v-else v-for="exam in filteredExams" :key="exam.id">
                        <td>
                            <input type="checkbox" :checked="isExamSelected(exam.id)"
                                :disabled="isLoading || deletingExamId === exam.id"
                                @change="toggleSelectExam(exam.id, $event.target.checked)" aria-label="選取考卷" />
                        </td>
                        <td>{{ exam.id }}</td>
                        <td>{{ exam.name }}</td>
                        <td>{{ exam.description }}</td>
                        <td>{{ exam.questionCount }}</td>
                        <td>{{ exam.timeLimit != null ? exam.timeLimit : '-' }}</td>
                        <td>{{ exam.createdAt }}</td>
                        <td>{{ exam.updatedAt }}</td>
                        <td>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button"
                                    :id="`dropdownExam${exam.id}`" data-bs-toggle="dropdown" aria-expanded="false">
                                    操作
                                </button>
                                <ul class="dropdown-menu" :aria-labelledby="`dropdownExam${exam.id}`">
                                    <li>
                                        <button class="dropdown-item" type="button"
                                            @click="editExam(exam.id)">編輯</button>
                                    </li>
                                    <li>
                                        <button class="dropdown-item" type="button"
                                            @click="viewExam(exam.id)">檢視</button>
                                    </li>
                                    <li>
                                        <hr class="dropdown-divider" />
                                    </li>
                                    <li>
                                        <button class="dropdown-item" type="button" :disabled="exportingExams[exam.id]"
                                            @click="exportExam(exam.id)">
                                            <span v-if="exportingExams[exam.id]"
                                                class="spinner-border spinner-border-sm me-2"></span>
                                            {{ exportingExams[exam.id] ? '匯出中...' : '匯出' }}
                                        </button>
                                    </li>
                                    <li>
                                        <button class="dropdown-item" type="button" @click="printExam(exam.id)">
                                            列印
                                        </button>
                                    </li>
                                    <li>
                                        <button class="dropdown-item text-danger" type="button"
                                            :disabled="deletingExamId === exam.id" @click="deleteExam(exam.id)">
                                            <span v-if="deletingExamId === exam.id"
                                                class="spinner-border spinner-border-sm me-2"></span>
                                            {{ deletingExamId === exam.id ? '刪除中...' : '刪除' }}
                                        </button>
                                    </li>
                                </ul>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Selection Toolbar -->
        <SelectionToolbar :selected-count="selectedExamCount" item-unit="張考卷" @clear="clearExamSelection">
            <button class="toolbar-btn toolbar-btn-primary" @click="exportSelectedExams" :disabled="isExporting">
                <svg v-if="!isExporting" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                <div v-else class="toolbar-spinner"></div>
                <span>{{ isExporting ? '匯出中...' : '匯出' }}</span>
            </button>
            <div class="toolbar-divider"></div>
            <button class="toolbar-btn toolbar-btn-danger" @click="deleteSelectedExams" :disabled="isDeletingSelected">
                <div v-if="isDeletingSelected" class="toolbar-spinner"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                <span>{{ isDeletingSelected ? '刪除中...' : '刪除' }}</span>
            </button>
        </SelectionToolbar>

        <!-- Pagination -->
        <PaginationControl :pagination-state="paginationState" :current-page="currentPage" :page-size="pageSize"
            :is-loading="isLoading" @page-change="handlePageChange" @size-change="handleSizeChange" />

        <ExamDetailModal :visible="isExamDetailVisible" :exam="selectedExamDetail" :loading="isExamDetailLoading"
            :error="examDetailError" @close="closeExamDetail" />

        <!-- Hidden file input for import -->
        <input ref="jsonImportInput" type="file" accept="application/json" style="display:none"
            @change="handleImportFile" />
    </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import questionService from '@/services/questionService'
import ExamDetailModal from '@/components/ExamDetailModal.vue'
import { usePdfImportStore } from '@/stores/pdfImport'
import examService from '@/services/examService'
import SelectionToolbar from '@/components/common/SelectionToolbar.vue'
import PaginationControl from '@/components/common/PaginationControl.vue'

const emit = defineEmits(['show-import-progress', 'hide-import-progress', 'show-import-result', 'show-export-progress', 'hide-export-progress'])

const exams = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const searchTerm = ref('')
const ordering = ref('-created_at')
const currentPage = ref(1)
const pageSize = ref(20)
const paginationState = ref({ hasNext: false, hasPrev: false, totalPages: 0, totalCount: 0 })
const selectedExamDetail = ref(null)
const isExamDetailVisible = ref(false)
const isExamDetailLoading = ref(false)
const examDetailError = ref('')
const deletingExamId = ref(null)
const isExporting = ref(false)
const exportingExams = reactive({})
const selectedExamIds = ref([])
const isDeletingSelected = ref(false)
const jsonImportInput = ref(null)

const router = useRouter()
const pdfImportStore = usePdfImportStore()

const orderingOptions = [
    { label: '最新建立', value: '-created_at' },
    { label: '最舊建立', value: 'created_at' },
    { label: '最近更新', value: '-updated_at' },
    { label: '名稱 (A-Z)', value: 'name' }
]

const formatDateTime = (value) => {
    if (!value) return '-'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
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

const filteredExams = computed(() => {
    const term = searchTerm.value.trim().toLowerCase()
    if (!term) return exams.value
    return exams.value.filter((exam) => {
        const haystack = [exam.name, exam.description, exam.questionCount?.toString(), exam.timeLimit?.toString(),
        exam.createdAt, exam.updatedAt, exam.id?.toString()].filter(Boolean).map((v) => v.toLowerCase()).join(' ')
        return haystack.includes(term)
    })
})

const selectedExamCount = computed(() => selectedExamIds.value.length)
const isPageAllSelected = computed(() => {
    if (exams.value.length === 0) return false
    return exams.value.every(exam => selectedExamIds.value.includes(exam.id))
})

const toggleSelectExam = (examId, checked) => {
    if (checked) {
        if (!selectedExamIds.value.includes(examId)) selectedExamIds.value.push(examId)
    } else {
        const index = selectedExamIds.value.indexOf(examId)
        if (index > -1) selectedExamIds.value.splice(index, 1)
    }
}

const toggleSelectAllExams = () => {
    if (isPageAllSelected.value) {
        exams.value.forEach(exam => {
            const index = selectedExamIds.value.indexOf(exam.id)
            if (index > -1) selectedExamIds.value.splice(index, 1)
        })
    } else {
        exams.value.forEach(exam => {
            if (!selectedExamIds.value.includes(exam.id)) selectedExamIds.value.push(exam.id)
        })
    }
}

const isExamSelected = (examId) => selectedExamIds.value.includes(examId)
const clearExamSelection = () => { selectedExamIds.value = [] }

const fetchExams = async () => {
    isLoading.value = true
    errorMessage.value = ''
    try {
        const params = { page: currentPage.value, page_size: pageSize.value }
        if (searchTerm.value.trim()) params.search = searchTerm.value.trim()
        if (ordering.value) params.ordering = ordering.value
        const { data } = await examService.getExams(params)
        const list = Array.isArray(data) ? data : data.results ?? []
        exams.value = list.map(normalizeExam)
        if (Array.isArray(data)) {
            paginationState.value = { hasNext: false, hasPrev: false, totalPages: 1, totalCount: data.length }
        } else {
            const count = data.count || 0
            paginationState.value = {
                hasNext: Boolean(data.next),
                hasPrev: Boolean(data.previous) || currentPage.value > 1,
                totalPages: Math.ceil(count / pageSize.value) || 1,
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

const applyFilters = () => { currentPage.value = 1; fetchExams() }
const resetFilters = () => { searchTerm.value = ''; ordering.value = '-created_at'; currentPage.value = 1; fetchExams() }

const handlePageChange = (page) => {
    if (page !== currentPage.value && page >= 1 && page <= paginationState.value.totalPages) {
        currentPage.value = page
        fetchExams()
    }
}

const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    fetchExams()
}


const normalizeExamDetail = (exam) => ({
    id: exam.id, name: exam.name, description: exam.description || '—', timeLimit: exam.time_limit ?? null,
    createdAt: formatDateTime(exam.created_at), updatedAt: formatDateTime(exam.updated_at),
    examQuestions: (exam.exam_questions ?? []).map((q, i) => ({
        id: q.id ?? i, order: q.order ?? i + 1, points: q.points ?? null,
        questionContent: q.question_content || '—', questionSubject: q.question_subject || '', questionCategory: q.question_category || ''
    }))
})

const viewExam = async (id) => {
    isExamDetailVisible.value = true; isExamDetailLoading.value = true; examDetailError.value = ''; selectedExamDetail.value = null
    try {
        const { data } = await examService.getExam(id)
        selectedExamDetail.value = normalizeExamDetail(data)
    } catch (error) {
        examDetailError.value = error.response?.data?.detail || '無法取得考卷詳細資訊。'
    } finally { isExamDetailLoading.value = false }
}

const closeExamDetail = () => { isExamDetailVisible.value = false; selectedExamDetail.value = null; examDetailError.value = '' }
const editExam = (id) => { router.push(`/admin/exams/${id}/edit`) }
const addExam = () => { pdfImportStore.clearPayload(); router.push('/admin/exams/new') }
const batchImport = () => { if (jsonImportInput.value) jsonImportInput.value.click() }

const deleteExam = async (id) => {
    if (!confirm('確定要刪除此考卷嗎？')) return
    deletingExamId.value = id
    try {
        await examService.deleteExam(id)
        alert('考卷已刪除')
        await fetchExams()
        if (!exams.value.length && currentPage.value > 1) { currentPage.value -= 1; await fetchExams() }
    } catch (error) {
        alert(error.response?.data?.detail || '刪除考卷失敗，請稍後再試。')
    } finally { deletingExamId.value = null }
}

const deleteSelectedExams = async () => {
    if (selectedExamIds.value.length === 0) return
    if (!confirm(`確定要刪除選取的 ${selectedExamIds.value.length} 張考卷嗎？`)) return
    isDeletingSelected.value = true
    let successCount = 0, failCount = 0
    for (const id of [...selectedExamIds.value]) {
        try {
            await examService.deleteExam(id)
            successCount++
            selectedExamIds.value.splice(selectedExamIds.value.indexOf(id), 1)
        } catch { failCount++ }
    }
    isDeletingSelected.value = false
    alert(failCount === 0 ? `成功刪除 ${successCount} 張考卷` : `刪除完成：成功 ${successCount} 張，失敗 ${failCount} 張`)
    fetchExams()
}

const exportExam = async (examId) => {
    if (exportingExams[examId]) return
    exportingExams[examId] = true
    try {
        const { data } = await examService.getExam(examId)
        const exportItem = { id: data.id, name: data.name, description: data.description, time_limit: data.time_limit, exam_questions: [] }
        if (Array.isArray(data.exam_questions)) {
            for (const eq of data.exam_questions) {
                let qId = eq.question ? (typeof eq.question === 'object' ? eq.question.id : eq.question) : eq.question_id
                if (qId) exportItem.exam_questions.push({ question_id: qId, order: eq.order, points: eq.points })
            }
        }
        const blob = new Blob([JSON.stringify(exportItem, null, 2)], { type: 'application/json' })
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = `exam_${exportItem.id || 'export'}.json`
        document.body.appendChild(a); a.click()
        setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href) }, 100)
    } catch (error) { alert('匯出考卷失敗') }
    finally { exportingExams[examId] = false }
}

const exportSelectedExams = async () => {
    if (selectedExamIds.value.length === 0 || isExporting.value) return
    isExporting.value = true
    try {
        const exportData = []
        for (const examId of selectedExamIds.value) {
            try {
                const { data } = await examService.getExam(examId)
                const examQuestions = (data.exam_questions || []).filter(eq => eq.question).map(eq => ({ question_id: eq.question, order: eq.order, points: eq.points }))
                exportData.push({ id: data.id, name: data.name, description: data.description, time_limit: data.time_limit, exam_questions: examQuestions })
            } catch { }
        }
        if (exportData.length === 0) { alert('沒有可匯出的考卷'); return }
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = `selected_exams_${new Date().toISOString().slice(0, 19).replaceAll(':', '-')}.json`
        document.body.appendChild(a); a.click()
        setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(a.href) }, 100)
        alert(`成功匯出 ${exportData.length} 張考卷`)
    } catch { alert('批量匯出失敗') }
    finally { isExporting.value = false }
}

const handleImportFile = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    try {
        const text = await file.text()
        const parsed = JSON.parse(text)
        const items = Array.isArray(parsed) ? parsed : [parsed]
        for (const item of items) {
            if (!item.name) continue
            const examData = { name: item.name, description: item.description || '', time_limit: item.time_limit || null }
            const res = await examService.createExam(examData)
            const newExamId = res.data?.id
            if (newExamId && Array.isArray(item.exam_questions)) {
                for (const eq of item.exam_questions) {
                    if (eq.question_id) {
                        try {
                            const exists = await questionService.getQuestion(eq.question_id).catch(() => null)
                            if (exists?.data) await examService.addQuestionToExam(newExamId, { question: eq.question_id, order: eq.order, points: eq.points })
                        } catch { }
                    }
                }
            }
        }
        alert('匯入完成')
        fetchExams()
    } catch (error) { alert('匯入失敗：' + (error.message || '格式錯誤')) }
    finally { event.target.value = '' }
}

const printExam = (examId) => {
    const printUrl = router.resolve({ path: `/admin/exams/${examId}/print` }).href
    window.open(printUrl, '_blank')
}

defineExpose({ fetchExams, addExam, batchImport })
onMounted(() => { fetchExams() })
</script>

<style scoped>
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

/* Table */
.exam-table {
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    overflow: hidden;
}

.exam-table .table {
    margin-bottom: 0;
}

.table-status {
    text-align: center;
    color: var(--text-secondary, #64748B);
    padding: 60px 20px;
    font-size: 14px;
}

.table th,
.table td {
    padding: 14px 20px;
    vertical-align: middle;
}

.table th {
    font-weight: 600;
    color: var(--text-secondary, #64748B);
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.table td {
    color: var(--text-primary, #1E293B);
    border-bottom: 1px solid #f1f5f9;
    font-size: 13px;
}

.table tbody tr {
    transition: background 0.15s;
}

.table tbody tr:hover {
    background: #f8fafc;
}

.table tbody tr:last-child td {
    border-bottom: none;
}

.table input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--primary, #476996);
}

.toolbar-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>

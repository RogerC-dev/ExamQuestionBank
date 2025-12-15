<template>
    <div class="user-exam-view">
        <div class="container">
            <h1 class="page-title">我的考卷</h1>
            <p class="page-subtitle">管理您的自訂考卷,或建立新的練習考卷</p>

            <!-- Tabs -->
            <div class="tabs-container">
                <button class="tab-btn" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    我的考卷列表
                </button>
                <button class="tab-btn" @click="router.push('/exams/create')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="12" y1="18" x2="12" y2="12"></line>
                        <line x1="9" y1="15" x2="15" y2="15"></line>
                    </svg>
                    建立新考卷
                </button>
            </div>

            <!-- Exam List Tab -->
            <div v-if="activeTab === 'list'" class="tab-content">
                <div class="exam-list-section">
                    <div class="section-header">
                        <h2 class="section-title">我的考卷</h2>
                        <div class="header-actions">
                            <button class="btn btn-secondary btn-sm" @click="loadUserExams" :disabled="loadingExams">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                                    <path d="M3 3v5h5"></path>
                                </svg>
                                重新整理
                            </button>
                        </div>
                    </div>

                    <div v-if="loadingExams" class="loading-state">
                        <div class="spinner"></div>
                        <p>載入考卷中...</p>
                    </div>

                    <div v-else-if="userExams.length === 0" class="empty-state">
                        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                        <p>尚未建立任何考卷</p>
                        <button class="btn btn-primary" @click="activeTab = 'create'">
                            建立第一份考卷
                        </button>
                    </div>

                    <div v-else class="exam-grid">
                        <div v-for="exam in userExams" :key="exam.id" class="exam-card">
                            <div class="exam-card-header">
                                <h3 class="exam-name">{{ exam.name }}</h3>
                                <div class="exam-meta">
                                    <span class="meta-item">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <circle cx="12" cy="12" r="10"></circle>
                                            <polyline points="12 6 12 12 16 14"></polyline>
                                        </svg>
                                        {{ exam.time_limit ? `${exam.time_limit} 分鐘` : '無時間限制' }}
                                    </span>
                                    <span class="meta-item">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                            <polyline points="14 2 14 8 20 8"></polyline>
                                        </svg>
                                        {{ exam.question_count || 0 }} 題
                                    </span>
                                </div>
                            </div>
                            <div class="exam-card-footer">
                                <span class="exam-date">{{ formatDate(exam.created_at) }}</span>
                                <div class="exam-actions">
                                    <button class="btn btn-sm btn-primary" @click="startExam(exam.id)">
                                        開始作答
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="deleteExam(exam.id)"
                                        :disabled="deletingExamId === exam.id">
                                        {{ deletingExamId === exam.id ? '刪除中...' : '刪除' }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Create Exam Tab -->
            <div v-if="activeTab === 'create'" class="tab-content">
                <!-- Question List Component (Search Mode Only) -->
                <QuestionList :questions="[]" :selected-question-id="null" :loading="false"
                    :show-auto-distribute="false" :show-add-question="false" :tags="tags"
                    :search-results="searchQuestions" :search-loading="searchLoading" :total-search-count="totalCount"
                    :pending-edits="{}" @search-questions="handleSearchQuestions" @load-tags="loadTags"
                    @update:selected-ids="handleSelectedIdsChange" />

                <!-- Exam Configuration -->
                <div class="exam-config-section">
                    <h2 class="section-title">考卷設定</h2>

                    <div class="config-form">
                        <div class="form-group">
                            <label class="form-label">考卷名稱 <span class="required">*</span></label>
                            <input v-model="examConfig.name" type="text" class="form-input" placeholder="例如：民法總則練習卷"
                                maxlength="200" />
                        </div>

                        <div class="form-group">
                            <label class="form-label">時間限制（分鐘）</label>
                            <input v-model.number="examConfig.timeLimit" type="number" class="form-input"
                                placeholder="選填，不填則無時間限制" min="5" max="600" />
                        </div>

                        <div class="form-actions">
                            <button class="btn btn-primary btn-lg" @click="createExam"
                                :disabled="!canCreateExam || creating">
                                <svg v-if="!creating" xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="12" y1="18" x2="12" y2="12"></line>
                                    <line x1="9" y1="15" x2="15" y2="15"></line>
                                </svg>
                                <span>{{ creating ? '建立中...' : '建立考卷' }}</span>
                            </button>
                        </div>

                        <div v-if="errorMessage" class="error-message">
                            {{ errorMessage }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { fetchSubjects } from '@/services/api'
import examService from '@/services/examService'
import questionService from '@/services/questionService'
import QuestionList from '@/components/QuestionList.vue'

const router = useRouter()

// Tab state
const activeTab = ref('list')

// Exam list data
const userExams = ref([])
const loadingExams = ref(false)
const deletingExamId = ref(null)

// Create exam - search state
const tags = ref([])
const searchQuestions = ref([])
const searchLoading = ref(false)
const totalCount = ref(0)
const selectedQuestionIds = ref([])

// Create exam - exam config
const examConfig = ref({
    name: '',
    timeLimit: null
})
const creating = ref(false)
const errorMessage = ref('')

// Legacy variables (to be removed after full migration)
const subjects = ref([])
const questions = ref([])
const selectedQuestions = ref(new Set())
const filters = ref({
    subject: '',
    difficulty: '',
    search: '',
    tags: [],
    tag_mode: 'or'
})
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// Computed
const canCreateExam = computed(() => {
    return selectedQuestionIds.value.length > 0 && examConfig.value.name.trim().length > 0
})

const isAllSelected = computed(() => {
    if (questions.value.length === 0) return false
    return questions.value.every(q => selectedQuestions.value.has(q.id))
})

const paginationState = computed(() => {
    const totalPages = Math.ceil(totalCount.value / pageSize.value)
    return {
        totalPages,
        totalCount: totalCount.value,
        hasNext: currentPage.value < totalPages,
        hasPrev: currentPage.value > 1
    }
})

// Methods
const difficultyLabel = (difficulty) => {
    const labels = {
        easy: '簡單',
        medium: '中等',
        hard: '困難'
    }
    return labels[difficulty] || difficulty
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date)
}

const loadUserExams = async () => {
    loadingExams.value = true
    try {
        const { data } = await api.get('/exams/')
        // 處理分頁回應 (data.results) 或直接陣列回應
        const exams = Array.isArray(data) ? data : (data?.results || [])
        // 過濾掉 null 或 undefined 的項目
        userExams.value = exams.filter(exam => exam && exam.id)
    } catch (error) {
        console.error('載入考卷失敗:', error)
        userExams.value = []
    } finally {
        loadingExams.value = false
    }
}

const startExam = (examId) => {
    router.push(`/exams/${examId}/preview`)
}

const deleteExam = async (examId) => {
    if (!confirm('確定要刪除這份考卷嗎？')) return

    deletingExamId.value = examId
    try {
        await api.delete(`/exams/${examId}/`)
        await loadUserExams()
    } catch (error) {
        console.error('刪除考卷失敗:', error)
        if (error.response?.status === 403) {
            alert('您沒有權限刪除此考卷')
        } else {
            alert('刪除考卷失敗，請稍後再試')
        }
    } finally {
        deletingExamId.value = null
    }
}

// QuestionList event handlers
const handleSearchQuestions = async (filters, page = 1, pageSize = 20) => {
    searchLoading.value = true
    try {
        const params = {
            page: page,
            page_size: pageSize
        }

        if (filters.subject) params.subject = filters.subject
        if (filters.difficulty) params.difficulty = filters.difficulty
        if (filters.search) params.search = filters.search
        if (filters.tags && filters.tags.length > 0) {
            params.tags = filters.tags.map(t => t.id).join(',')
            params.tag_mode = filters.tag_mode
        }

        const { data } = await api.get('/question_bank/questions/', { params })

        // Transform search results to match format
        searchQuestions.value = (data.results || []).map(q => ({
            id: `search-${q.id}`,
            question: q.id,
            question_content: q.content || q.question_content,
            question_subject: q.subject_name || q.subject,
            question_category: q.category,
            difficulty: q.difficulty,
            tags: q.tags,
            points: 1,
            order: 0,
            isSearchResult: true,
            originalQuestion: q
        }))
        totalCount.value = data.count || 0
    } catch (error) {
        console.error('搜尋題目失敗:', error)
        searchQuestions.value = []
        totalCount.value = 0
    } finally {
        searchLoading.value = false
    }
}

const handleSelectedIdsChange = (ids) => {
    selectedQuestionIds.value = ids
}

const loadSubjects = async () => {
    try {
        const { data } = await fetchSubjects()
        subjects.value = data
    } catch (error) {
        console.error('載入科目失敗:', error)
    }
}

const loadTags = async () => {
    try {
        const { data } = await api.get('/question_bank/tags/')
        // Handle both array response and paginated response
        tags.value = Array.isArray(data) ? data : (data.results || [])
    } catch (error) {
        console.error('載入標籤失敗:', error)
        tags.value = [] // Ensure tags is always an array
    }
}

const loadQuestions = async () => {
    loading.value = true
    errorMessage.value = ''

    try {
        const params = {
            page: currentPage.value,
            page_size: pageSize.value
        }

        if (filters.value.subject) {
            params.subject = filters.value.subject
        }
        if (filters.value.difficulty) {
            params.difficulty = filters.value.difficulty
        }
        if (filters.value.search) {
            params.search = filters.value.search
        }
        if (filters.value.tags && filters.value.tags.length > 0) {
            params.tags = filters.value.tags.map(t => t.id).join(',')
            params.tag_mode = filters.value.tag_mode
        }

        const { data } = await api.get('/question_bank/questions/', { params })

        questions.value = data.results || []
        totalCount.value = data.count || 0
    } catch (error) {
        console.error('載入題目失敗:', error)
        errorMessage.value = '載入題目失敗，請稍後再試'
    } finally {
        loading.value = false
    }
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

const toggleQuestion = (question) => {
    if (selectedQuestions.value.has(question.id)) {
        selectedQuestions.value.delete(question.id)
    } else {
        selectedQuestions.value.add(question.id)
    }
    // Trigger reactivity
    selectedQuestions.value = new Set(selectedQuestions.value)
}

const toggleSelectAll = () => {
    if (isAllSelected.value) {
        // Deselect all on current page
        questions.value.forEach(q => {
            selectedQuestions.value.delete(q.id)
        })
    } else {
        // Select all on current page
        questions.value.forEach(q => {
            selectedQuestions.value.add(q.id)
        })
    }
    selectedQuestions.value = new Set(selectedQuestions.value)
}

const clearSelection = () => {
    selectedQuestions.value.clear()
    selectedQuestions.value = new Set(selectedQuestions.value)
}

const handlePageChange = (page) => {
    currentPage.value = page
    loadQuestions()
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handlePageSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    loadQuestions()
}

const createExam = async () => {
    if (!canCreateExam.value) {
        errorMessage.value = '請選擇至少一題並填寫考卷名稱'
        return
    }

    creating.value = true
    errorMessage.value = ''

    try {
        const payload = {
            name: examConfig.value.name.trim(),
            question_ids: selectedQuestionIds.value
        }

        if (examConfig.value.timeLimit && examConfig.value.timeLimit > 0) {
            payload.time_limit = examConfig.value.timeLimit
        }

        const response = await examService.createCustomExam(payload)

        // Reset form
        examConfig.value = { name: '', timeLimit: null }
        selectedQuestionIds.value = []

        // Reload exam list
        await loadUserExams()

        // Switch to list tab
        activeTab.value = 'list'

        // Show success message
        alert('考卷建立成功！')
    } catch (error) {
        console.error('建立考卷失敗:', error)
        errorMessage.value = error.response?.data?.detail || error.response?.data?.error || '建立考卷失敗，請稍後再試'
    } finally {
        creating.value = false
    }
}

// Lifecycle
onMounted(async () => {
    await loadUserExams()
    await Promise.all([
        loadSubjects(),
        loadTags()
    ])
    // Only load questions when switching to create tab
    if (activeTab.value === 'create') {
        await loadQuestions()
    }
})
</script>

<style scoped>
.user-exam-view {
    min-height: 100vh;
    background: var(--bg-page, #F8FAFC);
    padding: 32px 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}

.page-title {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary, #1E293B);
    margin-bottom: 8px;
}

.page-subtitle {
    font-size: 16px;
    color: var(--text-secondary, #64748B);
    margin-bottom: 32px;
}

/* Tabs */
.tabs-container {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    border-bottom: 2px solid #e5e7eb;
}

.tab-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    color: var(--text-secondary, #64748B);
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: -2px;
}

.tab-btn:hover {
    color: var(--primary, #476996);
    background: var(--primary-soft, #EEF2FF);
}

.tab-btn.active {
    color: var(--primary, #476996);
    border-bottom-color: var(--primary, #476996);
}

.tab-content {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Exam List Section */
.exam-list-section {
    background: var(--surface, #FFFFFF);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary, #1E293B);
    margin: 0;
}

.header-actions {
    display: flex;
    gap: 8px;
}

.exam-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
}

.exam-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 200px;
    background: #f9fafb;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s;
}

.exam-card:hover {
    border-color: var(--primary, #476996);
    box-shadow: 0 4px 12px rgba(71, 105, 150, 0.15);
    transform: translateY(-2px);
}

.exam-card-header {
    margin-bottom: 16px;
}

.exam-name {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary, #1E293B);
    margin: 0 0 12px 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}

.exam-meta {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--text-secondary, #64748B);
}

.meta-item svg {
    flex-shrink: 0;
}

.exam-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16px;
    margin-top: auto;
    border-top: 1px solid #e5e7eb;
}

.exam-date {
    font-size: 12px;
    color: var(--text-secondary, #64748B);
}

.exam-actions {
    display: flex;
    gap: 8px;
}

/* Filters Section */
.filters-section {
    background: var(--surface, #FFFFFF);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.filter-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-item-wide {
    grid-column: span 2;
}

.filter-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary, #1E293B);
}

.filter-select,
.filter-input {
    padding: 10px 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    background: #f9fafb;
    transition: all 0.2s;
}

.filter-select:focus,
.filter-input:focus {
    outline: none;
    border-color: var(--primary, #476996);
    background: white;
    box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.search-input-wrapper {
    position: relative;
    display: flex;
    gap: 8px;
}

.search-input-wrapper .filter-input {
    flex: 1;
}

.search-btn {
    padding: 10px 16px;
    background: var(--primary, #476996);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-btn:hover:not(:disabled) {
    background: var(--primary-hover, #35527a);
}

.search-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.filter-row {
    margin-bottom: 16px;
}

.filter-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
}

.result-count {
    font-size: 14px;
    color: var(--text-secondary, #64748B);
    font-weight: 500;
}

/* Selected Summary */
.selected-summary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
}

.summary-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.summary-text {
    display: flex;
    align-items: center;
    gap: 12px;
    color: white;
    font-size: 16px;
    font-weight: 600;
}

.summary-text svg {
    flex-shrink: 0;
}

/* Questions Section */
.questions-section {
    background: var(--surface, #FFFFFF);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.selection-actions {
    display: flex;
    gap: 8px;
}

.loading-state,
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    color: var(--text-secondary, #64748B);
}

.spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #e5e7eb;
    border-top-color: var(--primary, #476996);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.empty-state svg {
    color: #cbd5e1;
    margin-bottom: 16px;
}

.empty-state p {
    font-size: 16px;
    margin-bottom: 16px;
}

.questions-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.question-card {
    display: flex;
    gap: 16px;
    padding: 16px;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    background: #f9fafb;
    transition: all 0.2s;
}

.question-card:hover {
    border-color: #cbd5e1;
    background: white;
}

.question-card.selected {
    border-color: var(--primary, #476996);
    background: var(--primary-soft, #EEF2FF);
}

.question-checkbox {
    flex-shrink: 0;
    padding-top: 2px;
}

.question-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: var(--primary, #476996);
}

.question-content {
    flex: 1;
    min-width: 0;
}

.question-header {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 8px;
}

.question-text {
    font-size: 15px;
    color: var(--text-primary, #1E293B);
    line-height: 1.6;
    cursor: pointer;
    display: block;
}

.question-meta {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.meta-badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

.meta-badge.subject {
    background: #dbeafe;
    color: #1e40af;
}

.meta-badge.difficulty.easy {
    background: #dcfce7;
    color: #16a34a;
}

.meta-badge.difficulty.medium {
    background: #fef3c7;
    color: #d97706;
}

.meta-badge.difficulty.hard {
    background: #fee2e2;
    color: #dc2626;
}

.question-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.tag {
    padding: 3px 8px;
    background: #e0e7ff;
    color: #4f46e5;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
}

/* Exam Config Section */
.exam-config-section {
    background: var(--surface, #FFFFFF);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.config-form {
    max-width: 600px;
}

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary, #1E293B);
    margin-bottom: 8px;
}

.required {
    color: #dc2626;
}

.form-input {
    width: 100%;
    padding: 12px 14px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    background: #f9fafb;
    transition: all 0.2s;
}

.form-input:focus {
    outline: none;
    border-color: var(--primary, #476996);
    background: white;
    box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.form-actions {
    margin-top: 24px;
}

.error-message {
    margin-top: 16px;
    padding: 12px 16px;
    background: #fee2e2;
    color: #dc2626;
    border-radius: 8px;
    font-size: 14px;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background: var(--primary, #476996);
    color: white;
    box-shadow: 0 2px 4px rgba(71, 105, 150, 0.2);
}

.btn-primary:hover:not(:disabled) {
    background: var(--primary-hover, #35527a);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(71, 105, 150, 0.3);
}

.btn-secondary {
    background: #f1f5f9;
    color: var(--text-primary, #1E293B);
}

.btn-secondary:hover:not(:disabled) {
    background: #e2e8f0;
}

.btn-ghost {
    background: transparent;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-ghost:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
}

.btn-danger {
    background: #fee;
    color: #dc2626;
    border: 1px solid #fecaca;
}

.btn-danger:hover:not(:disabled) {
    background: #dc2626;
    color: white;
    border-color: #dc2626;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(220, 38, 38, 0.3);
}

.btn-sm {
    padding: 6px 12px;
    font-size: 13px;
}

.btn-lg {
    padding: 14px 28px;
    font-size: 16px;
}

/* Responsive */
@media (max-width: 768px) {
    .filter-item-wide {
        grid-column: span 1;
    }

    .page-title {
        font-size: 24px;
    }

    .filters-section,
    .questions-section,
    .exam-config-section,
    .exam-list-section {
        padding: 16px;
    }

    .summary-content {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
    }

    .question-card {
        flex-direction: column;
        gap: 12px;
    }

    .exam-grid {
        grid-template-columns: 1fr;
    }

    .exam-card-footer {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
    }

    .exam-actions {
        width: 100%;
        justify-content: flex-end;
    }
}
</style>

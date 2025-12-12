<template>
  <div class="question-admin">
    <!-- Question Filters -->
    <div class="question-filters">
      <div class="filter-search">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input 
          v-model="searchTerm" 
          type="text" 
          class="filter-input" 
          placeholder="搜尋題目內容、科目..."
          @keyup.enter="applyFilters" 
        />
      </div>

      <div class="filter-tags-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="tags-icon">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
        <multiselect
          v-model="selectedSearchTags"
          :options="tagOptions"
          :multiple="true"
          :close-on-select="false"
          :clear-on-select="false"
          :preserve-search="true"
          placeholder="選擇標籤..."
          track-by="id"
          label="name"
          class="tag-multiselect"
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
          <option value="-created_at">最新建立</option>
          <option value="created_at">最舊建立</option>
          <option value="-updated_at">最近更新</option>
          <option value="content">題目內容 A-Z</option>
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

    <div class="question-table">
      <table class="table table-striped table-hover">
        <thead>
          <tr>
            <th style="width:4%">
              <input
                ref="pageSelectAllCheckbox"
                type="checkbox"
                :checked="isPageAllSelected"
                :indeterminate="selectedCount > 0 && !isPageAllSelected"
                :disabled="isLoading"
                @change="toggleSelectAll"
                aria-label="選取全部"
              />
            </th>
            <th>ID</th>
            <th>科目</th>
            <th>內容</th>
            <th>題型</th>
            <th>難度</th>
            <th>建立時間</th>
            <th>更新時間</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="9" class="table-status">題目資料載入中...</td>
          </tr>
          <tr v-else-if="!questions.length">
            <td colspan="9" class="table-status">暫無符合條件的題目</td>
          </tr>
          <tr v-else v-for="q in questions" :key="q.id">
            <td>
              <input
                type="checkbox"
                :checked="isRowSelected(q.id)"
                :disabled="isLoading || deletingId === q.id"
                @change="toggleSelect(q.id, $event.target.checked)"
                aria-label="選取題目"
              />
            </td>
            <td>{{ q.id }}</td>
            <td>
              <div>{{ q.subject }}</div>
              <div style="margin-top:6px">
                <span v-for="t in q.tags" :key="t.id" class="meta-badge tag-badge">{{ t.name }}</span>
              </div>
            </td>
            <td :title="q.content">{{ q.contentSnippet }}</td>
            <td>{{ q.question_type }}</td>
            <td>{{ q.difficulty }}</td>
            <td>{{ q.createdAt }}</td>
            <td>{{ q.updatedAt }}</td>
            <td>
              <div class="dropdown">
                <button
                  class="btn btn-sm btn-outline-secondary dropdown-toggle"
                  type="button"
                  :id="`dropdownQuestion${q.id}`"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  操作
                </button>
                <ul class="dropdown-menu" :aria-labelledby="`dropdownQuestion${q.id}`">
                  <li>
                    <button class="dropdown-item" type="button" @click="openEditQuestion(q.id)">
                      編輯
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" type="button" @click="viewQuestion(q.id)">
                      檢視
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" type="button" @click="viewAssociatedExams(q.id, q.content)">
                      查看關聯考卷
                    </button>
                  </li>
                  <li><hr class="dropdown-divider" /></li>
                  <li>
                    <button
                      class="dropdown-item text-danger"
                      type="button"
                      :disabled="deletingId === q.id"
                      :aria-disabled="deletingId === q.id"
                      @click="deleteQuestion(q.id)"
                    >
                      <span v-if="deletingId === q.id" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      <span v-if="!deletingId || deletingId !== q.id">刪除</span>
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

    <!-- Selection Toolbar (Sticky) -->
    <transition name="slide-up">
      <div class="selection-toolbar-wrapper" v-if="selectedCount > 0">
        <div class="selection-toolbar">
          <div class="toolbar-content">
            <div class="toolbar-info">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 11 12 14 22 4"></polyline>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <span class="toolbar-text">已選取</span>
              <span class="toolbar-count">{{ selectedCount }}</span>
              <span class="toolbar-text">個題目</span>
            </div>
            
            <div class="toolbar-divider"></div>
            
            <div class="toolbar-actions">
              <button class="toolbar-btn toolbar-btn-secondary" @click="clearSelection" title="清除選取">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                <span>清除</span>
              </button>
              
              <button class="toolbar-btn toolbar-btn-primary" @click="openAddToExamModal" title="加入到考卷">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
                <span>加入考卷</span>
              </button>
              
              <button class="toolbar-btn toolbar-btn-secondary" @click="openBulkTagModal" title="批次編輯標籤">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
                <span>編輯標籤</span>
              </button>
              
              <button class="toolbar-btn toolbar-btn-secondary" @click="openBulkSubjectModal" title="批次編輯科目">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                <span>編輯科目</span>
              </button>
              
              <div class="toolbar-divider"></div>
              
              <button class="toolbar-btn toolbar-btn-danger" @click="deleteSelectedQuestions" :disabled="isDeleting" title="批量刪除">
                <div v-if="isDeleting" class="toolbar-spinner"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                <span>{{ isDeleting ? '刪除中...' : '刪除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Enhanced Pagination -->
    <nav v-if="paginationState.totalPages > 0" class="pagination-wrapper">
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
            @click="typeof page === 'number' ? goToPage(page) : null"
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

    <div v-if="isEditorVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">題目編輯</h5>
            <button type="button" class="btn-close" @click="closeEditor"></button>
          </div>
          <div class="modal-body">
            <QuestionEditor :question="currentQuestion" :saving="saving" @save="handleSave" />
          </div>
        </div>
      </div>
    </div>

    <!-- View Associated Exams Modal -->
    <div v-if="isViewExamsModalVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">題目關聯考卷</h5>
            <button type="button" class="btn-close" @click="closeViewExamsModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label fw-semibold">題目內容</label>
              <p class="text-break">{{ currentQuestionContent }}</p>
            </div>
            <div>
              <label class="form-label fw-semibold">關聯考卷</label>
              <div v-if="isLoadingAssociatedExams" class="text-center">
                <div class="spinner-border" role="status">
                  <span class="visually-hidden">加載中...</span>
                </div>
              </div>
              <div v-else-if="associatedExams.length === 0" class="alert alert-info small">
                此題目未關聯到任何考卷
              </div>
              <div v-else class="list-group">
                <div v-for="exam in associatedExams" :key="exam.id" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ exam.name }}</h6>
                      <small class="text-muted">ID: {{ exam.id }}</small>
                    </div>
                    <span class="badge bg-secondary">{{ exam.question_count || 0 }} 題</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeViewExamsModal">關閉</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add to Exam Modal -->
    <div v-if="isAddToExamModalVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">加入到考卷</h5>
            <button type="button" class="btn-close" @click="closeAddToExamModal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info" role="alert">
              將 {{ selectedCount }} 題加入到選定的考卷
            </div>
            <div class="mb-3">
              <label class="form-label">選擇考卷</label>
              <multiselect
                v-model="selectedExams"
                :options="availableExams"
                :loading="isLoadingExams"
                :multiple="true"
                :close-on-select="false"
                placeholder="搜尋或選擇考卷..."
                track-by="id"
                label="name"
                :searchable="true"
              />
            </div>
            <div v-if="selectedExams.length > 0" class="alert alert-secondary small">
              <div><strong>已選擇 {{ selectedExams.length }} 個考卷：</strong></div>
              <ul class="mb-0 mt-2">
                <li v-for="exam in selectedExams" :key="exam.id" class="small">
                  {{ exam.name }} (ID: {{ exam.id }} | 現有題數: {{ exam.question_count || 0 }})
                </li>
              </ul>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeAddToExamModal">取消</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="addQuestionsToExam"
              :disabled="selectedExams.length === 0 || isAddingToExam"
            >
              <span v-if="isAddingToExam" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isAddingToExam ? '加入中...' : '確認加入' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Edit Modals -->
    <BulkTagEditor
      v-if="showBulkTagModal"
      :questions="questions"
      :pendingQuestions="[]"
      :preselectedIds="selectedIds"
      @close="showBulkTagModal = false"
      @applied="handleBulkTagsApplied"
    />

    <BulkSubjectEditor
      v-if="showBulkSubjectModal"
      :questions="questions"
      :pendingQuestions="[]"
      :preselectedIds="selectedIds"
      @close="showBulkSubjectModal = false"
      @applied="handleBulkSubjectApplied"
    />

    <!-- Delete Confirmation Modal -->
    <div v-if="isDeleteConfirmModalVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">確認刪除</h5>
            <button type="button" class="btn-close" @click="closeDeleteConfirmModal" :disabled="isDeleting"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-danger mb-3" role="alert">
              <strong>⚠️ 警告：此操作無法復原</strong>
            </div>
            <div class="mb-3">
              <p class="mb-2">您將刪除 <strong>{{ selectedCount }} 題</strong>。</p>
              <div v-if="isLoadingAffectedExams" class="text-center my-3">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">加載中...</span>
                </div>
              </div>
              <div v-else-if="affectedExamsForDelete.length > 0" class="alert alert-warning small">
                <p class="mb-2"><strong>這些題目涉及 {{ affectedExamsForDelete.length }} 份考卷：</strong></p>
                <ul class="mb-0">
                  <li v-for="exam in affectedExamsForDelete" :key="exam.id">
                    {{ exam.name }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDeleteConfirmModal" :disabled="isDeleting">
              取消
            </button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="confirmDelete"
              :disabled="isDeleting || isLoadingAffectedExams"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isDeleting ? '刪除中...' : '確認刪除' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import questionService from '@/services/questionService'
import examService from '@/services/examService'
import QuestionEditor from '@/components/QuestionEditor.vue'
import BulkTagEditor from '@/components/BulkTagEditor.vue'
import BulkSubjectEditor from '@/components/BulkSubjectEditor.vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import tagService from '@/services/tagService'

const questions = ref([])
const isLoading = ref(false)
const error = ref('')
const searchTerm = ref('')
const selectedSearchTags = ref([])
const tagOptions = ref([])
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
const deletingId = ref(null)
const selectedIds = ref([])
const pageSelectAllCheckbox = ref(null)

const isEditorVisible = ref(false)
const currentQuestion = ref(null)
const saving = ref(false)

// View Associated Exams Modal state
const isViewExamsModalVisible = ref(false)
const currentQuestionId = ref(null)
const currentQuestionContent = ref('')
const associatedExams = ref([])
const isLoadingAssociatedExams = ref(false)

// Add to Exam Modal state
const isAddToExamModalVisible = ref(false)
const selectedExams = ref([])
const availableExams = ref([])
const isLoadingExams = ref(false)
const isAddingToExam = ref(false)
const isDeleting = ref(false)
const showBulkTagModal = ref(false)
const showBulkSubjectModal = ref(false)

const openBulkTagModal = () => {
  console.log('Admin: openBulkTagModal called. selectedCount=', selectedCount.value)
  console.log('Admin: questions=', questions.value)
  console.log('Admin: selectedIds=', selectedIds.value)
  showBulkTagModal.value = true
  console.log('Admin: showBulkTagModal set to true')
  setTimeout(() => {
    const overlay = document.querySelector('.modal-overlay')
    console.log('Admin: modal-overlay in DOM?', !!overlay, overlay)
  }, 100)
}

const openBulkSubjectModal = () => {
  console.log('Admin: openBulkSubjectModal called. selectedCount=', selectedCount.value)
  console.log('Admin: questions=', questions.value)
  console.log('Admin: selectedIds=', selectedIds.value)
  showBulkSubjectModal.value = true
  console.log('Admin: showBulkSubjectModal set to true')
  setTimeout(() => {
    const overlay = document.querySelector('.modal-overlay')
    console.log('Admin: modal-overlay in DOM?', !!overlay, overlay)
  }, 100)
}

// Debugging watch to observe modal states
watch(showBulkTagModal, (v) => console.log('showBulkTagModal changed:', v))
watch(showBulkSubjectModal, (v) => console.log('showBulkSubjectModal changed:', v))

// Affected exams state for delete confirmation
const isDeleteConfirmModalVisible = ref(false)
const affectedExamsForDelete = ref([])
const isLoadingAffectedExams = ref(false)

// Selection helpers
const isRowSelected = (id) => selectedIds.value.includes(id)
const selectedCount = computed(() => selectedIds.value.length)

const isPageAllSelected = computed(() => {
  if (!questions.value || questions.value.length === 0) return false
  return questions.value.every(q => selectedIds.value.includes(q.id))
})

const emit = defineEmits(["update:selected-ids"])

const toggleSelect = (id, checked) => {
  const idx = selectedIds.value.indexOf(id)
  if (checked && idx === -1) {
    selectedIds.value = [...selectedIds.value, id]
  } else if (!checked && idx !== -1) {
    selectedIds.value = selectedIds.value.filter(x => x !== id)
  }
}

const toggleSelectAll = () => {
  if (isPageAllSelected.value) {
    // remove current page ids from selection
    const pageIds = questions.value.map(q => q.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
  } else {
    // add all page ids (avoid duplicates)
    const pageIds = questions.value.map(q => q.id)
    const set = new Set([...selectedIds.value, ...pageIds])
    selectedIds.value = Array.from(set)
  }
}

const clearSelection = () => { selectedIds.value = [] }

// Emit selection changes to parent
watch(selectedIds, (val) => {
  try { emit('update:selected-ids', val) } catch (e) { /* noop if parent not listening */ }
}, { deep: true })


const normalize = (q) => ({
  id: q.id,
  subject: q.subject || '',
  category: q.category || '',
  question_type: q.question_type || '',
  difficulty: q.difficulty || '',
  tags: q.tags || [],
  contentSnippet: (() => {
    const raw = q.content || ''
    return raw.length > 20 ? raw.slice(0, 20) + '…' : raw
  })(),
  content: q.content || '',
  createdAt: formatDateTime(q.created_at),
  updatedAt: formatDateTime(q.updated_at)
})

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(date)
}

const fetchQuestions = async () => {
  isLoading.value = true
  try {
    const params = { 
      page: currentPage.value,
      page_size: pageSize.value
    }
    const trimmed = searchTerm.value?.trim()
    if (trimmed) params.search = trimmed
    if (ordering.value) params.ordering = ordering.value
    if (selectedSearchTags.value.length > 0) {
      params.tags = selectedSearchTags.value.map(t => t.id).join(',')
    }
    const { data } = await questionService.getQuestions(params)
    const list = Array.isArray(data) ? data : data.results || []
    questions.value = list.map(normalize)
    
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
  } catch (err) {
    console.error('Failed to fetch questions', err)
    error.value = err.response?.data?.detail || '取得題目列表失敗'
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => { currentPage.value = 1; fetchQuestions() }
const resetFilters = () => { searchTerm.value = ''; selectedSearchTags.value = []; ordering.value = '-created_at'; currentPage.value = 1; fetchQuestions() }

// Pagination functions
const goToFirstPage = () => { 
  if (currentPage.value === 1 || isLoading.value) return
  currentPage.value = 1
  fetchQuestions() 
}

const goToPreviousPage = () => { 
  if (!paginationState.value.hasPrev || currentPage.value === 1 || isLoading.value) return
  currentPage.value -= 1
  fetchQuestions() 
}

const goToNextPage = () => { 
  if (!paginationState.value.hasNext || isLoading.value) return
  currentPage.value += 1
  fetchQuestions() 
}

const goToLastPage = () => { 
  if (currentPage.value === paginationState.value.totalPages || isLoading.value) return
  currentPage.value = paginationState.value.totalPages
  fetchQuestions() 
}

const goToPage = (page) => {
  if (page === currentPage.value || isLoading.value) return
  if (page < 1 || page > paginationState.value.totalPages) return
  currentPage.value = page
  fetchQuestions()
}

const handlePageJump = () => {
  if (!isValidJumpPage.value || isLoading.value) return
  currentPage.value = jumpToPage.value
  jumpToPage.value = null
  fetchQuestions()
}

const onPageSizeChange = () => {
  currentPage.value = 1
  fetchQuestions()
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

// load tags
const loadTags = async () => {
  try {
    const res = await tagService.getTags()
    let items = res.data?.results || res.data
    if (!Array.isArray(items)) items = []
    tagOptions.value = items.filter(t => t != null)
  } catch (err) {
    console.error('載入標籤失敗:', err)
  }
}

onMounted(() => { 
  fetchQuestions()
  loadTags()
  
  // Listen for events from parent component
  window.addEventListener('openCreateQuestion', openCreateQuestion)
  window.addEventListener('refreshQuestions', fetchQuestions)
})

// Clean up event listeners
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('openCreateQuestion', openCreateQuestion)
  window.removeEventListener('refreshQuestions', fetchQuestions)
})

const openEditQuestion = async (id) => {
  try {
    isEditorVisible.value = true
    saving.value = false
    currentQuestion.value = null
    const { data } = await questionService.getQuestion(id)
    currentQuestion.value = data
  } catch (err) {
    console.error('Load question failed', err)
    alert('載入題目失敗')
    isEditorVisible.value = false
  }
}

const openCreateQuestion = () => { currentQuestion.value = null; isEditorVisible.value = true }

const closeEditor = () => { isEditorVisible.value = false; currentQuestion.value = null }

const handleSave = async ({ questionData }) => {
  try {
    saving.value = true
    if (currentQuestion.value && currentQuestion.value.id) {
      await questionService.updateQuestion(currentQuestion.value.id, questionData)
      alert('題目更新成功')
    } else {
      await questionService.createQuestion(questionData)
      alert('題目建立成功')
    }
    closeEditor()
    fetchQuestions()
  } catch (err) {
    console.error('Save question failed', err)
    alert('儲存題目失敗')
  } finally {
    saving.value = false
  }
}

const viewQuestion = async (id) => {
  // For now, reuse openEdit but set view-only (not necessary)
  openEditQuestion(id)
}

const openAddToExamModal = async () => {
  isAddToExamModalVisible.value = true
  selectedExams.value = []
  await loadAvailableExams()
}

const closeAddToExamModal = () => {
  isAddToExamModalVisible.value = false
  selectedExams.value = []
}

const loadAvailableExams = async () => {
  isLoadingExams.value = true
  try {
    const { data } = await examService.getExams({ pageSize: 100 })
    const list = Array.isArray(data) ? data : data.results || []
    availableExams.value = list
    console.log('Loaded exams:', list)
  } catch (err) {
    console.error('Failed to load exams', err)
    alert('載入考卷列表失敗')
  } finally {
    isLoadingExams.value = false
  }
}

const addQuestionsToExam = async () => {
  if (selectedExams.value.length === 0 || selectedCount.value === 0) return
  
  isAddingToExam.value = true
  try {
    // Add each question to each selected exam
    // According to API docs: POST /exams/{id}/add_question/ with { question, order, points }
    for (const exam of selectedExams.value) {
      for (let i = 0; i < selectedIds.value.length; i++) {
        const questionId = selectedIds.value[i]
        await examService.addQuestionToExam(exam.id, {
          question: questionId,
          order: i + 1
        })
      }
    }
    
    const examNames = selectedExams.value.map(e => e.name).join('、')
    alert(`成功將 ${selectedCount.value} 題加入到考卷「${examNames}」`)
    closeAddToExamModal()
    clearSelection()
  } catch (err) {
    console.error('Error adding questions to exam', err)
    alert('加入考卷失敗：' + (err.response?.data?.detail || err.message || '請重試'))
  } finally {
    isAddingToExam.value = false
  }
}

const closeViewExamsModal = () => {
  isViewExamsModalVisible.value = false
  currentQuestionId.value = null
  currentQuestionContent.value = ''
  associatedExams.value = []
}

const viewAssociatedExams = async (questionId, content) => {
  isViewExamsModalVisible.value = true
  currentQuestionId.value = questionId
  currentQuestionContent.value = content
  await loadAssociatedExams(questionId)
}

const loadAssociatedExams = async (questionId) => {
  isLoadingAssociatedExams.value = true
  try {
    // Use dedicated API endpoint to get exams containing this question
    const { data } = await examService.getExamsByQuestion(questionId)
    const exams = Array.isArray(data) ? data : data.results || []
    associatedExams.value = exams
    console.log('Associated exams:', exams)
  } catch (err) {
    console.error('Failed to load associated exams', err)
    alert('載入關聯考卷失敗')
  } finally {
    isLoadingAssociatedExams.value = false
  }
}

const deleteQuestion = async (id) => {
  if (!confirm('確定要刪除此題目嗎？')) return
  deletingId.value = id
  try {
    await questionService.deleteQuestion(id)
    // remove from selection if present
    if (selectedIds.value.includes(id)) {
      selectedIds.value = selectedIds.value.filter(x => x !== id)
    }
    alert('題目已刪除')
    fetchQuestions()
  } catch (err) {
    console.error('Delete question failed', err)
    alert('刪除題目失敗')
  } finally {
    deletingId.value = null
  }
}

const deleteSelectedQuestions = async () => {
  if (selectedCount.value === 0) return
  
  // Load affected exams first
  isLoadingAffectedExams.value = true
  try {
    const response = await examService.getExamsByQuestions(selectedIds.value)
    const exams = Array.isArray(response) ? response : response.data ? response.data : []
    console.log('Affected exams:', exams)
    affectedExamsForDelete.value = exams
  } catch (err) {
    console.error('Failed to load affected exams', err)
    affectedExamsForDelete.value = []
  } finally {
    isLoadingAffectedExams.value = false
  }
  
  // Show confirmation modal
  isDeleteConfirmModalVisible.value = true
}

const closeDeleteConfirmModal = () => {
  isDeleteConfirmModalVisible.value = false
}

const confirmDelete = async () => {
  isDeleting.value = true
  try {
    const idsToDelete = [...selectedIds.value]
    let successCount = 0
    let failCount = 0
    
    for (const id of idsToDelete) {
      try {
        await questionService.deleteQuestion(id)
        successCount++
      } catch (err) {
        console.error(`Failed to delete question ${id}`, err)
        failCount++
      }
    }
    
    selectedIds.value = []
    affectedExamsForDelete.value = []
    isDeleteConfirmModalVisible.value = false
    
    if (failCount === 0) {
      alert(`成功刪除 ${successCount} 題`)
    } else {
      alert(`成功刪除 ${successCount} 題，失敗 ${failCount} 題`)
    }
    
    fetchQuestions()
  } catch (err) {
    console.error('Batch delete failed', err)
    alert('批量刪除失敗')
  } finally {
    isDeleting.value = false
  }
}

// Handlers for Bulk Tag/Subject modals
const handleBulkTagsApplied = ({ successCount, errors, pendingUpdates }) => {
  if (successCount > 0) alert(`成功更新 ${successCount} 題標籤`)
  if (errors && errors.length > 0) alert(`有 ${errors.length} 題更新失敗，請查看 console`)
  // Close modal and refresh
  showBulkTagModal.value = false
  clearSelection()
  fetchQuestions()
}

const handleBulkSubjectApplied = ({ successCount, errors, pendingUpdates }) => {
  if (successCount > 0) alert(`成功更新 ${successCount} 題科目`)
  if (errors && errors.length > 0) alert(`有 ${errors.length} 題更新失敗，請查看 console`)
  showBulkSubjectModal.value = false
  clearSelection()
  fetchQuestions()
}

</script>

<style scoped>
.question-admin {
  padding: 0;
}

/* Filters */
.question-filters {
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
  display: flex;
  height: fit-content;
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

.filter-tags-wrapper {
  position: relative;
  flex: 1;
  min-width: 240px;
  align-self: flex-start;
}

.tags-icon {
  position: absolute;
  left: 14px;
  top: 16px;
  z-index: 1;
  color: var(--text-secondary, #64748B);
  pointer-events: none;
}

.tag-multiselect {
  width: 100%;
}

.tag-multiselect :deep(.multiselect__tags) {
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px 12px 8px 44px;
  background: #f9fafb;
  min-height: 44px;
  transition: all 0.2s ease;
}

.tag-multiselect :deep(.multiselect__tags):focus-within {
  border-color: var(--primary, #476996);
  background: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.tag-multiselect :deep(.multiselect__tag) {
  background: var(--primary, #476996);
  color: white;
  border-radius: 6px;
  padding: 6px 26px 6px 10px;
  margin: 2px 4px 2px 0;
}

.tag-multiselect :deep(.multiselect__tag-icon:after) {
  color: rgba(255, 255, 255, 0.8);
}

.tag-multiselect :deep(.multiselect__tag-icon:hover) {
  background: var(--primary-hover, #35527a);
}

.tag-multiselect :deep(.multiselect__option--highlight) {
  background: var(--primary, #476996);
}

.tag-multiselect :deep(.multiselect__option--selected) {
  background: var(--primary-soft, #EEF2FF);
  color: var(--primary, #476996);
}

.tag-multiselect :deep(.multiselect__content-wrapper) {
  position: absolute;
  width: 100%;
  z-index: 50;
}

.filter-select-wrapper {
  display: flex;
  height: fit-content;
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
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary, #476996);
  background-color: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.filter-btn {
  display: flex;
  align-items: center;
  height: fit-content;
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

/* Table */
.question-table { 
  background: white; 
  border-radius: 12px; 
  padding: 0; 
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

.meta-badge {
  display: inline-block;
  padding: 4px 10px;
  margin-right: 6px;
  margin-bottom: 4px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.tag-badge {
  display: inline-flex;
  align-items: center;
  background: var(--primary-soft, #EEF2FF);
  border: 1px solid var(--border, #CBD5E1);
  color: var(--primary, #476996);
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  margin-right: 6px;
  margin-bottom: 4px;
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

th input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--primary, #476996);
}

th:nth-child(1), td:nth-child(1) { width: 4%; }        /* 選取欄 */
th:nth-child(2), td:nth-child(2) { width: 8%; }        /* ID */
th:nth-child(3), td:nth-child(3) { width: 18%; }       /* 科目 */
th:nth-child(4), td:nth-child(4) { width: 22%; }       /* 內容 */
th:nth-child(5), td:nth-child(5) { width: 12%; }       /* 題型 */
th:nth-child(6), td:nth-child(6) { width: 10%; }       /* 難度 */
th:nth-child(7), td:nth-child(7) { width: 12%; }       /* 建立時間 */
th:nth-child(8), td:nth-child(8) { width: 12%; }       /* 更新時間 */
th:nth-child(9), td:nth-child(9) { width: 5%; }        /* 操作 */

/* Selection Toolbar Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.selection-toolbar-wrapper {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: calc(100% - 48px);
  max-width: 1200px;
}

.selection-toolbar {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border, #CBD5E1);
}

.toolbar-content {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  gap: 16px;
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: var(--primary-soft, #EEF2FF);
  border-radius: 10px;
}

.toolbar-info svg {
  color: var(--primary, #476996);
  flex-shrink: 0;
}

.toolbar-text {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
  font-weight: 500;
}

.toolbar-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 10px;
  background: var(--primary, #476996);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.toolbar-divider {
  width: 1px;
  height: 32px;
  background: #e5e7eb;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.toolbar-btn svg {
  flex-shrink: 0;
}

.toolbar-btn-secondary {
  background: #f3f4f6;
  color: var(--text-secondary, #64748B);
}

.toolbar-btn-secondary:hover {
  background: #e5e7eb;
  color: var(--text-primary, #1E293B);
  transform: translateY(-1px);
}

.toolbar-btn-primary {
  background: var(--primary, #476996);
  color: white;
}

.toolbar-btn-primary:hover {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
}

.toolbar-btn-danger {
  background: #fef2f2;
  color: #dc2626;
}

.toolbar-btn-danger:hover:not(:disabled) {
  background: #fee2e2;
  color: #b91c1c;
  transform: translateY(-1px);
}

.toolbar-btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toolbar-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(220, 38, 38, 0.3);
  border-top-color: #dc2626;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .toolbar-content {
    flex-wrap: wrap;
    padding: 12px 16px;
  }
  
  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .toolbar-btn span {
    display: none;
  }
  
  .toolbar-btn {
    padding: 8px 12px;
  }
  
  .toolbar-divider {
    display: none;
  }
}


td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: var(--text-primary, #1E293B);
  overflow: visible;
  text-overflow: ellipsis;
}

td input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--primary, #476996);
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

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border, #CBD5E1);
  flex-wrap: wrap;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-info .text-muted {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
  font-weight: 500;
}

.page-size-select {
  width: auto;
  min-width: 130px;
  padding: 8px 32px 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.page-size-select:focus {
  outline: none;
  border-color: var(--primary, #476996);
  background-color: white;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.pagination {
  display: flex;
  gap: 6px;
}

.page-link {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  color: var(--text-primary, #1E293B);
  background-color: white;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.page-link:hover:not(:disabled) {
  background-color: var(--primary-soft, #EEF2FF);
  border-color: var(--primary, #476996);
  color: var(--primary, #476996);
  transform: translateY(-1px);
}

.page-item.active .page-link {
  background: var(--primary, #476996);
  border-color: var(--primary, #476996);
  color: white;
  box-shadow: 0 2px 4px rgba(71, 105, 150, 0.2);
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.4;
  transform: none;
}

.page-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-jumper .text-muted {
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

.page-jumper input {
  width: 70px;
  text-align: center;
  padding: 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-jumper input:focus {
  outline: none;
  border-color: var(--primary, #476996);
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.page-jumper .btn {
  white-space: nowrap;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #476996);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-jumper .btn:hover:not(:disabled) {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
}

.page-jumper .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Responsive */
@media (max-width: 768px) {
  .question-admin {
    padding: 0;
  }

  .question-filters {
    flex-direction: column;
    padding: 16px;
  }

  .filter-search,
  .filter-tags-wrapper,
  .filter-select-wrapper {
    display: flex;
    height: fit-content;
    width: 100%;
    min-width: auto;
  }

  .filter-btn {
    flex: 1;
  }

  .question-table {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }

  .pagination-wrapper {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
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

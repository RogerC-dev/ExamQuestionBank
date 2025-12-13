<template>
  <div class="question-admin">
    <!-- Question Filters -->
    <div class="question-filters">
      <div class="filter-search">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input v-model="searchTerm" type="text" class="filter-input" placeholder="搜尋題目內容、科目..."
          @keyup.enter="applyFilters" />
      </div>

      <div class="filter-tags-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" class="tags-icon">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
        <multiselect v-model="selectedSearchTags" :options="tagOptions" :multiple="true" :close-on-select="false"
          :clear-on-select="false" :preserve-search="true" placeholder="選擇標籤..." track-by="id" label="name"
          class="tag-multiselect" />
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
          <option value="-created_at">最新建立</option>
          <option value="created_at">最舊建立</option>
          <option value="-updated_at">最近更新</option>
          <option value="content">題目內容 A-Z</option>
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

    <!-- Pending Questions Section -->
    <div v-if="pendingQuestions.length > 0" class="pending-section">
      <div class="pending-header">
        <div class="header-icon">
          <input type="checkbox" :checked="isAllPendingSelected" @change="toggleSelectAllPending" title="全選/取消全選"
            style="width: 18px; height: 18px; cursor: pointer;" />
        </div>
        <div class="header-content">
          <h3 class="pending-title">暫存題目</h3>
          <p class="pending-subtitle">
            共 {{ pendingQuestions.length }} 題
            <span v-if="selectedPendingIds.length > 0">（已選 {{ selectedPendingIds.length }} 題）</span>
          </p>
        </div>
        <div class="header-actions">
          <button v-if="selectedPendingIds.length > 0" class="btn-bulk-edit-pending"
            @click="openBulkSubjectModalForPending" title="批量編輯科目">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            編輯科目
          </button>
          <button v-if="selectedPendingIds.length > 0" class="btn-bulk-edit-pending" @click="openBulkTagModalForPending"
            title="批量編輯標籤">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
              <line x1="7" y1="7" x2="7.01" y2="7"></line>
            </svg>
            編輯標籤
          </button>
          <button class="btn-clear-pending" @click="clearPendingQuestions">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            清除全部
          </button>
          <button class="btn-save-pending" @click="savePendingQuestions" :disabled="isSavingPending">
            <svg v-if="!isSavingPending" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <div v-else class="pending-spinner"></div>
            {{ isSavingPending ? `儲存中... (${savingPendingProgress}/${pendingQuestions.length})` : '儲存全部' }}
          </button>
        </div>
      </div>

      <div class="pending-list">
        <div v-for="(item, index) in pendingQuestions" :key="`pending-${index}`" class="pending-item">
          <input type="checkbox" :checked="selectedPendingIds.includes(index)"
            @change="toggleSelectPending(index, $event.target.checked)" class="pending-checkbox" />
          <div class="pending-number">{{ index + 1 }}</div>
          <div class="pending-content">
            <div class="pending-text">{{ item.content }}</div>
            <div class="pending-meta">
              <span class="meta-badge">{{ item.subject }}</span>
              <span class="meta-badge">{{ item.category }}</span>
              <span v-if="item.options && item.options.length > 0" class="meta-info">{{ item.options.length }} 選項</span>
              <span v-if="getCorrectAnswer(item)" class="meta-badge meta-answer">答案: {{ getCorrectAnswer(item) }}</span>
            </div>
          </div>
          <div class="pending-actions">
            <button class="btn-edit-pending" @click="editPendingQuestion(index)" title="編輯">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button class="btn-remove-pending" @click="removePendingQuestion(index)" title="移除">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="question-table">
      <table class="table table-striped table-hover">
        <thead>
          <tr>
            <th style="width:4%">
              <input ref="pageSelectAllCheckbox" type="checkbox" :checked="isPageAllSelected"
                :indeterminate="selectedCount > 0 && !isPageAllSelected" :disabled="isLoading" @change="toggleSelectAll"
                aria-label="選取全部" />
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
              <input type="checkbox" :checked="isRowSelected(q.id)" :disabled="isLoading || deletingId === q.id"
                @change="toggleSelect(q.id, $event.target.checked)" aria-label="選取題目" />
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
                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button"
                  :id="`dropdownQuestion${q.id}`" data-bs-toggle="dropdown" aria-expanded="false">
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
                  <li>
                    <hr class="dropdown-divider" />
                  </li>
                  <li>
                    <button class="dropdown-item text-danger" type="button" :disabled="deletingId === q.id"
                      :aria-disabled="deletingId === q.id" @click="deleteQuestion(q.id)">
                      <span v-if="deletingId === q.id" class="spinner-border spinner-border-sm me-2" role="status"
                        aria-hidden="true"></span>
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
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                <span>清除</span>
              </button>

              <button class="toolbar-btn toolbar-btn-primary" @click="openAddToExamModal" title="加入到考卷">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
                <span>加入考卷</span>
              </button>

              <button class="toolbar-btn toolbar-btn-secondary" @click="openBulkTagModal" title="批次編輯標籤">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
                <span>編輯標籤</span>
              </button>

              <button class="toolbar-btn toolbar-btn-secondary" @click="openBulkSubjectModal" title="批次編輯科目">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                <span>編輯科目</span>
              </button>

              <div class="toolbar-divider"></div>

              <button class="toolbar-btn toolbar-btn-danger" @click="deleteSelectedQuestions" :disabled="isDeleting"
                title="批量刪除">
                <div v-if="isDeleting" class="toolbar-spinner"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
          <button class="page-link" :disabled="!paginationState.hasPrev || isLoading" @click="goToFirstPage"
            title="第一頁">
            <span aria-hidden="true">&laquo;</span>
          </button>
        </li>
        <li class="page-item" :class="{ disabled: !paginationState.hasPrev || isLoading }">
          <button class="page-link" :disabled="!paginationState.hasPrev || isLoading" @click="goToPreviousPage"
            title="上一頁">
            <span aria-hidden="true">&lsaquo;</span>
          </button>
        </li>

        <!-- Page Numbers -->
        <li v-for="page in visiblePages" :key="page" class="page-item"
          :class="{ active: page === currentPage, disabled: isLoading }">
          <button class="page-link" :disabled="isLoading" @click="typeof page === 'number' ? goToPage(page) : null">
            {{ page }}
          </button>
        </li>

        <li class="page-item" :class="{ disabled: !paginationState.hasNext || isLoading }">
          <button class="page-link" :disabled="!paginationState.hasNext || isLoading" @click="goToNextPage" title="下一頁">
            <span aria-hidden="true">&rsaquo;</span>
          </button>
        </li>
        <li class="page-item" :class="{ disabled: !paginationState.hasNext || isLoading }">
          <button class="page-link" :disabled="!paginationState.hasNext || isLoading" @click="goToLastPage"
            title="最後一頁">
            <span aria-hidden="true">&raquo;</span>
          </button>
        </li>
      </ul>

      <div class="page-jumper">
        <span class="text-muted me-2">跳至</span>
        <input v-model.number="jumpToPage" type="number" class="form-control form-control-sm" :min="1"
          :max="paginationState.totalPages" @keyup.enter="handlePageJump" placeholder="頁碼" />
        <button class="btn btn-sm btn-secondary" :disabled="isLoading || !isValidJumpPage" @click="handlePageJump">
          前往
        </button>
      </div>
    </nav>

    <div v-if="isEditorVisible" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content modern-modal">
          <div class="modern-modal-header">
            <div class="header-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </div>
            <div class="header-content-wrapper">
              <h5 class="modern-modal-title">{{ currentQuestion ? '編輯題目' : '新增題目' }}</h5>
              <p class="modern-modal-subtitle">{{ currentQuestion ? '修改題目資訊' : '填寫題目資訊並選擇儲存方式' }}</p>
            </div>
            <button type="button" class="modern-close-btn" @click="closeEditor" :disabled="saving">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          <div class="modal-body modern-modal-body">
            <QuestionEditor ref="questionEditorRef" :question="currentQuestion" :saving="saving" @save="handleSave"
              @save-pending="handleSaveToPendingFromEditor" @save-direct="handleSaveDirectlyFromEditor" />
          </div>
          <div class="modern-modal-footer" v-if="!currentQuestion">
            <div class="footer-info">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>選擇儲存方式：直接儲存到題庫或暫存後批次儲存</span>
            </div>
            <div class="footer-actions">
              <button class="footer-btn footer-btn-secondary" @click="closeEditor" :disabled="saving">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                取消
              </button>
              <button class="footer-btn footer-btn-pending" @click="handleSaveToPending"
                :disabled="saving || !isEditorFormValid">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                  <polyline points="17 21 17 13 7 13 7 21"></polyline>
                  <polyline points="7 3 7 8 15 8"></polyline>
                </svg>
                加入暫存
              </button>
              <button class="footer-btn footer-btn-primary" @click="handleSaveDirectly"
                :disabled="saving || !isEditorFormValid">
                <svg v-if="!saving" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                  fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <div v-else class="btn-spinner-small"></div>
                {{ saving ? '儲存中...' : '直接儲存' }}
              </button>
            </div>
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
              <multiselect v-model="selectedExams" :options="availableExams" :loading="isLoadingExams" :multiple="true"
                :close-on-select="false" placeholder="搜尋或選擇考卷..." track-by="id" label="name" :searchable="true" />
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
            <button type="button" class="btn btn-primary" @click="addQuestionsToExam"
              :disabled="selectedExams.length === 0 || isAddingToExam">
              <span v-if="isAddingToExam" class="spinner-border spinner-border-sm me-2" role="status"
                aria-hidden="true"></span>
              {{ isAddingToExam ? '加入中...' : '確認加入' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Edit Modals -->
    <BulkTagEditor v-if="showBulkTagModal" :questions="bulkEditMode === 'list' ? questions : []"
      :pendingQuestions="bulkEditMode === 'pending' ? pendingQuestions : []"
      :preselectedIds="bulkEditMode === 'list' ? selectedIds : []"
      :preselectedPendingIds="bulkEditMode === 'pending' ? selectedPendingIds : []" @close="closeBulkTagModal"
      @applied="handleBulkTagsApplied" />

    <BulkSubjectEditor v-if="showBulkSubjectModal" :questions="bulkEditMode === 'list' ? questions : []"
      :pendingQuestions="bulkEditMode === 'pending' ? pendingQuestions : []"
      :preselectedIds="bulkEditMode === 'list' ? selectedIds : []"
      :preselectedPendingIds="bulkEditMode === 'pending' ? selectedPendingIds : []" @close="closeBulkSubjectModal"
      @applied="handleBulkSubjectApplied" />

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
            <button type="button" class="btn btn-danger" @click="confirmDelete"
              :disabled="isDeleting || isLoadingAffectedExams">
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status"
                aria-hidden="true"></span>
              {{ isDeleting ? '刪除中...' : '確認刪除' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content modern-modal">
          <div class="modern-modal-header">
            <div class="header-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
            </div>
            <div class="header-content-wrapper">
              <h5 class="modern-modal-title">匯入題目</h5>
              <p class="modern-modal-subtitle">選擇匯入方式並上傳檔案</p>
            </div>
            <button type="button" class="modern-close-btn" @click="closeImportModal">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          <div class="modal-body modern-modal-body">
            <div class="import-options">
              <div class="import-option" @click="selectImportType('json')">
                <div class="option-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                  </svg>
                </div>
                <div class="option-content">
                  <h6 class="option-title">JSON 檔案</h6>
                  <p class="option-description">匯入結構化的 JSON 格式題目檔案</p>
                  <div class="option-hint">支援格式: .json</div>
                </div>
                <div class="option-arrow">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </div>
              </div>

              <div class="import-option" @click="selectImportType('pdf')">
                <div class="option-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <div class="option-content">
                  <h6 class="option-title">PDF 檔案</h6>
                  <p class="option-description">自動解析考選部 PDF 考卷檔案</p>
                  <div class="option-hint">支援格式: .pdf</div>
                </div>
                <div class="option-arrow">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </div>
              </div>
            </div>

            <!-- JSON Import Section -->
            <div v-if="importType === 'json'" class="import-section">
              <div class="upload-zone" @click="$refs.jsonFileInput.click()" @dragover.prevent
                @drop.prevent="handleJsonDrop">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p class="upload-text">點擊或拖放檔案至此</p>
                <p class="upload-hint">支援 JSON 格式檔案</p>
                <input ref="jsonFileInput" type="file" accept=".json,application/json" style="display: none"
                  @change="handleJsonFileSelect" />
              </div>
              <div v-if="selectedJsonFile" class="selected-file">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                  <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <span>{{ selectedJsonFile.name }}</span>
                <button @click="clearJsonFile" class="btn-clear-file">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>

            <!-- PDF Import Section -->
            <div v-if="importType === 'pdf'" class="import-section">
              <PdfUploadSection ref="pdfUploadRef" @import-success="handlePdfImportSuccess" />
            </div>
          </div>
          <div class="modern-modal-footer" v-if="importType === 'json' && selectedJsonFile">
            <div class="footer-info">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>檔案將被解析並添加到暫存區</span>
            </div>
            <div class="footer-actions">
              <button class="footer-btn footer-btn-secondary" @click="closeImportModal">
                取消
              </button>
              <button class="footer-btn footer-btn-primary" @click="processJsonImport" :disabled="isImporting">
                <svg v-if="!isImporting" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                  fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <div v-else class="btn-spinner-small"></div>
                {{ isImporting ? '匯入中...' : '開始匯入' }}
              </button>
            </div>
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
import PdfUploadSection from '@/components/PdfUploadSection.vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import tagService from '@/services/tagService'

const questions = ref([])
const pendingQuestions = ref([])
const isSavingPending = ref(false)
const savingPendingProgress = ref(0)
const selectedPendingIds = ref([]) // 暫存題目選中的索引
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
const questionEditorRef = ref(null)
const editingPendingIndex = ref(null) // 追蹤正在編輯的暫存題目索引
const isEditorFormValid = computed(() => {
  return questionEditorRef.value?.isFormValid ?? false
})

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
const bulkEditMode = ref('list') // 'list' or 'pending' - 標記批量編輯的來源

// Import Modal state
const showImportModal = ref(false)
const importType = ref(null) // 'json' or 'pdf'
const selectedJsonFile = ref(null)
const jsonFileInput = ref(null)
const pdfUploadRef = ref(null)
const isImporting = ref(false)

const openBulkTagModal = () => {
  bulkEditMode.value = 'list'
  showBulkTagModal.value = true
}

const openBulkSubjectModal = () => {
  bulkEditMode.value = 'list'
  showBulkSubjectModal.value = true
}

const openBulkTagModalForPending = () => {
  bulkEditMode.value = 'pending'
  showBulkTagModal.value = true
}

const openBulkSubjectModalForPending = () => {
  bulkEditMode.value = 'pending'
  showBulkSubjectModal.value = true
}

const closeBulkTagModal = () => {
  showBulkTagModal.value = false
  bulkEditMode.value = 'list'
}

const closeBulkSubjectModal = () => {
  showBulkSubjectModal.value = false
  bulkEditMode.value = 'list'
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

// Pending questions selection
const isAllPendingSelected = computed(() => {
  if (pendingQuestions.value.length === 0) return false
  return selectedPendingIds.value.length === pendingQuestions.value.length
})

const toggleSelectPending = (index, checked) => {
  if (checked) {
    if (!selectedPendingIds.value.includes(index)) {
      selectedPendingIds.value.push(index)
    }
  } else {
    selectedPendingIds.value = selectedPendingIds.value.filter(i => i !== index)
  }
}

const toggleSelectAllPending = () => {
  if (isAllPendingSelected.value) {
    selectedPendingIds.value = []
  } else {
    selectedPendingIds.value = pendingQuestions.value.map((_, index) => index)
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

const closeEditor = () => { isEditorVisible.value = false; currentQuestion.value = null; saving.value = false }

const handleSave = async ({ questionData }) => {
  // This is called when editing existing question
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

// New: Save directly to database
const handleSaveDirectly = () => {
  if (!questionEditorRef.value) return
  questionEditorRef.value.requestSaveDirect()
}

// New: Save to pending list
const handleSaveToPending = () => {
  if (!questionEditorRef.value) return
  questionEditorRef.value.requestSavePending()
}

// Called from QuestionEditor when save direct is triggered
const handleSaveDirectlyFromEditor = async ({ questionData }) => {
  try {
    saving.value = true

    // 如果是編輯暫存題目
    if (editingPendingIndex.value !== null) {
      pendingQuestions.value[editingPendingIndex.value] = questionData
      alert('暫存題目已更新')
      closeEditor()
      editingPendingIndex.value = null
      return
    }

    await questionService.createQuestion(questionData)
    alert('題目建立成功')
    closeEditor()
    fetchQuestions()
  } catch (err) {
    console.error('Save question failed', err)
    alert('儲存題目失敗：' + (err.response?.data?.detail || err.message || ''))
  } finally {
    saving.value = false
  }
}

// Called from QuestionEditor when save to pending is triggered
const handleSaveToPendingFromEditor = ({ questionData }) => {
  // 如果是編輯暫存題目，直接更新
  if (editingPendingIndex.value !== null) {
    pendingQuestions.value[editingPendingIndex.value] = questionData
    alert('暫存題目已更新')
    editingPendingIndex.value = null
  } else {
    addPendingQuestion(questionData)
    alert('已加入暫存列表')
  }
  closeEditor()
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
  let totalUpdated = successCount

  // 處理暫存題目的更新
  if (pendingUpdates && pendingUpdates.length > 0) {
    pendingUpdates.forEach(update => {
      if (update.index !== undefined) {
        // 更新暫存題目
        if (pendingQuestions.value[update.index]) {
          pendingQuestions.value[update.index].tags = update.tags || []
          pendingQuestions.value[update.index].tag_ids = update.tag_ids || []
          totalUpdated++
        }
      }
    })
  }

  if (totalUpdated > 0) alert(`成功更新 ${totalUpdated} 題標籤`)
  if (errors && errors.length > 0) alert(`有 ${errors.length} 題更新失敗，請查看 console`)

  closeBulkTagModal()
  if (bulkEditMode.value === 'pending') {
    selectedPendingIds.value = []
  } else {
    clearSelection()
    fetchQuestions()
  }
}

const handleBulkSubjectApplied = ({ successCount, errors, pendingUpdates }) => {
  let totalUpdated = successCount

  // 處理暫存題目的更新
  if (pendingUpdates && pendingUpdates.length > 0) {
    pendingUpdates.forEach(update => {
      if (update.index !== undefined) {
        // 更新暫存題目
        if (pendingQuestions.value[update.index]) {
          if (update.subject !== undefined) {
            pendingQuestions.value[update.index].subject = update.subject
          }
          if (update.category !== undefined) {
            pendingQuestions.value[update.index].category = update.category
          }
          totalUpdated++
        }
      }
    })
  }

  if (totalUpdated > 0) alert(`成功更新 ${totalUpdated} 題科目`)
  if (errors && errors.length > 0) alert(`有 ${errors.length} 題更新失敗，請查看 console`)

  closeBulkSubjectModal()
  if (bulkEditMode.value === 'pending') {
    selectedPendingIds.value = []
  } else {
    clearSelection()
    fetchQuestions()
  }
}

// Pending Questions handlers
const addPendingQuestion = (questionData) => {
  pendingQuestions.value.push(questionData)
}

const getCorrectAnswer = (question) => {
  if (!question.options || !Array.isArray(question.options)) return ''

  const correctOptions = question.options
    .map((opt, idx) => opt.is_correct ? String.fromCharCode(65 + idx) : null)
    .filter(Boolean)

  return correctOptions.join(', ')
}

const editPendingQuestion = (index) => {
  editingPendingIndex.value = index
  currentQuestion.value = { ...pendingQuestions.value[index] }
  isEditorVisible.value = true
}

const removePendingQuestion = (index) => {
  if (confirm('確定要移除這個暫存題目嗎？')) {
    pendingQuestions.value.splice(index, 1)
  }
}

const clearPendingQuestions = () => {
  if (confirm(`確定要清除全部 ${pendingQuestions.value.length} 個暫存題目嗎？`)) {
    pendingQuestions.value = []
  }
}

const savePendingQuestions = async () => {
  if (pendingQuestions.value.length === 0) return

  if (!confirm(`即將儲存 ${pendingQuestions.value.length} 個題目到題庫，確定要繼續嗎？`)) {
    return
  }

  isSavingPending.value = true
  savingPendingProgress.value = 0

  let successCount = 0
  let failCount = 0
  const errors = []

  try {
    for (let i = 0; i < pendingQuestions.value.length; i++) {
      const questionData = pendingQuestions.value[i]
      savingPendingProgress.value = i + 1

      try {
        await questionService.createQuestion(questionData)
        successCount++
      } catch (err) {
        console.error(`儲存題目 ${i + 1} 失敗:`, err)
        failCount++
        errors.push({ index: i + 1, error: err })
      }
    }

    // Clear pending questions after save
    pendingQuestions.value = []
    savingPendingProgress.value = 0

    // Show result
    if (failCount === 0) {
      alert(`成功儲存 ${successCount} 題到題庫`)
    } else {
      alert(`成功儲存 ${successCount} 題，失敗 ${failCount} 題`)
    }

    // Refresh question list
    fetchQuestions()
  } catch (err) {
    console.error('批量儲存失敗:', err)
    alert('批量儲存失敗')
  } finally {
    isSavingPending.value = false
    savingPendingProgress.value = 0
  }
}

// Import Modal Functions
const showImportModalFunc = () => {
  showImportModal.value = true
  importType.value = null
  selectedJsonFile.value = null
}

const closeImportModal = () => {
  showImportModal.value = false
  importType.value = null
  selectedJsonFile.value = null
  isImporting.value = false
}

const selectImportType = (type) => {
  importType.value = type
}

const handleJsonFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/json') {
    selectedJsonFile.value = file
  } else {
    alert('請選擇有效的 JSON 檔案')
  }
}

const handleJsonDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/json') {
    selectedJsonFile.value = file
  } else {
    alert('請選擇有效的 JSON 檔案')
  }
}

const clearJsonFile = () => {
  selectedJsonFile.value = null
  if (jsonFileInput.value) {
    jsonFileInput.value.value = ''
  }
}

const processJsonImport = async () => {
  if (!selectedJsonFile.value) return

  isImporting.value = true
  try {
    const fileContent = await selectedJsonFile.value.text()
    const data = JSON.parse(fileContent)

    // Check if data is array of questions
    let questionsToImport = []
    if (Array.isArray(data)) {
      questionsToImport = data
    } else if (data.questions && Array.isArray(data.questions)) {
      questionsToImport = data.questions
    } else {
      throw new Error('JSON 格式不正確，應為題目陣列或包含 questions 屬性的物件')
    }

    // Add to pending questions
    const validQuestions = questionsToImport.filter(q => q.content && q.question_type)
    if (validQuestions.length === 0) {
      throw new Error('沒有找到有效的題目數據')
    }

    pendingQuestions.value.push(...validQuestions)
    alert(`成功匯入 ${validQuestions.length} 題到暫存區`)
    closeImportModal()
  } catch (err) {
    console.error('JSON 匯入失敗:', err)
    alert(`匯入失敗: ${err.message}`)
  } finally {
    isImporting.value = false
  }
}

const handlePdfImportSuccess = (data) => {
  if (data && data.questions && data.questions.length > 0) {
    // 轉換 PDF 數據格式為系統需要的格式
    const formattedQuestions = data.questions.map(q => {
      // 將選項陣列轉換為對象格式，並標記正確答案
      const correctAnswer = q.correct_answer || ''
      let formattedOptions = []

      if (q.options && Array.isArray(q.options) && q.options.length > 0) {
        formattedOptions = q.options.map((optionText, index) => {
          // 選項標籤: A, B, C, D...
          const optionLabel = String.fromCharCode(65 + index) // A=65, B=66...
          return {
            content: optionText,
            is_correct: correctAnswer === optionLabel || correctAnswer === optionText
          }
        })
      }

      return {
        content: q.question || q.content || '',
        subject: data.examData?.subject || '',
        category: data.examData?.category || '',
        question_type: q.options && q.options.length > 0 ? '選擇題' : '申論題',
        options: formattedOptions,
        difficulty: data.examData?.level || 'medium',
        explanation: '',
        status: 'draft',
        tags: [],
        tag_ids: []
      }
    })

    pendingQuestions.value.push(...formattedQuestions)
    alert(`成功從 PDF 解析 ${formattedQuestions.length} 題到暫存區`)
    closeImportModal()
  }
}

// Expose function for external use (e.g., from PDF import)
defineExpose({
  addPendingQuestion,
  addPendingQuestions: (questions) => {
    pendingQuestions.value.push(...questions)
  },
  showImportModal: showImportModalFunc
})

</script>

<style scoped>
.question-admin {
  padding: 0;
}

/* Pending Questions Section */
.pending-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px dashed #d89b32;
  margin-bottom: 24px;
  overflow: hidden;
}

.pending-header {
  background: linear-gradient(135deg, #d89b32 0%, #c88a2a 100%);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
}

.header-icon svg {
  color: white;
}

.header-content {
  flex: 1;
}

.pending-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0 0 4px 0;
}

.pending-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-bulk-edit-pending,
.btn-clear-pending,
.btn-save-pending {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-bulk-edit-pending {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-bulk-edit-pending:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-1px);
}

.btn-clear-pending {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-clear-pending:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.btn-save-pending {
  background: white;
  color: #d89b32;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-save-pending:hover:not(:disabled) {
  background: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-save-pending:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.pending-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(216, 155, 50, 0.3);
  border-top-color: #d89b32;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.pending-list {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.pending-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  margin-bottom: 10px;
  background: #fff7eb;
  border: 1px dashed #d89b32;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.pending-item:hover {
  background: #fef3e2;
  border-color: #c88a2a;
  box-shadow: 0 2px 8px rgba(216, 155, 50, 0.1);
}

.pending-checkbox {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-top: 8px;
  cursor: pointer;
}

.pending-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #d89b32;
  color: white;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
}

.pending-content {
  flex: 1;
  min-width: 0;
}

.pending-text {
  font-size: 14px;
  color: var(--text-primary, #1E293B);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.pending-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.meta-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(216, 155, 50, 0.15);
  color: #c88a2a;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.meta-badge.meta-answer {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
  font-weight: 700;
}

.meta-info {
  font-size: 12px;
  color: var(--text-secondary, #64748B);
}

.pending-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-edit-pending,
.btn-remove-pending {
  flex-shrink: 0;
  padding: 8px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit-pending {
  color: var(--primary, #476996);
}

.btn-edit-pending:hover {
  background: var(--primary-soft, #EEF2FF);
  transform: scale(1.05);
}

.btn-remove-pending {
  color: #dc2626;
}

.btn-remove-pending:hover {
  background: #fee2e2;
  transform: scale(1.05);
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

th:nth-child(1),
td:nth-child(1) {
  width: 4%;
}

/* 選取欄 */
th:nth-child(2),
td:nth-child(2) {
  width: 8%;
}

/* ID */
th:nth-child(3),
td:nth-child(3) {
  width: 18%;
}

/* 科目 */
th:nth-child(4),
td:nth-child(4) {
  width: 22%;
}

/* 內容 */
th:nth-child(5),
td:nth-child(5) {
  width: 12%;
}

/* 題型 */
th:nth-child(6),
td:nth-child(6) {
  width: 10%;
}

/* 難度 */
th:nth-child(7),
td:nth-child(7) {
  width: 12%;
}

/* 建立時間 */
th:nth-child(8),
td:nth-child(8) {
  width: 12%;
}

/* 更新時間 */
th:nth-child(9),
td:nth-child(9) {
  width: 5%;
}

/* 操作 */

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
  bottom: 100px;
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
  to {
    transform: rotate(360deg);
  }
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
  position: sticky;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border, #CBD5E1);
  flex-wrap: wrap;
  z-index: 100;
  margin-top: 24px;
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

/* Modern Modal Styles */
.modern-modal {
  border-radius: 16px;
  overflow: hidden;
  border: none;
}

.modern-modal-header {
  background: linear-gradient(135deg, var(--primary, #476996) 0%, var(--primary-hover, #35527a) 100%);
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-icon-wrapper {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
}

.header-icon-wrapper svg {
  color: white;
}

.header-content-wrapper {
  flex: 1;
}

.modern-modal-title {
  font-size: 22px;
  font-weight: 700;
  color: white;
  margin: 0 0 4px 0;
  letter-spacing: -0.02em;
}

.modern-modal-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  font-weight: 400;
}

.modern-close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.modern-close-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.modern-close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modern-close-btn svg {
  color: white;
}

.modern-modal-body {
  padding: 28px;
  max-height: calc(90vh - 250px);
  overflow-y: auto;
}

.modern-modal-footer {
  padding: 20px 28px;
  background: #f9fafb;
  border-top: 1px solid var(--border, #CBD5E1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary, #64748B);
  font-size: 13px;
  flex: 1;
}

.footer-info svg {
  flex-shrink: 0;
}

.footer-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.footer-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.footer-btn svg {
  flex-shrink: 0;
}

.footer-btn-secondary {
  background: white;
  color: var(--text-secondary, #64748B);
  border: 1px solid var(--border, #CBD5E1);
}

.footer-btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
  color: var(--text-primary, #1E293B);
  border-color: #94a3b8;
}

.footer-btn-pending {
  background: #fff7eb;
  color: #d89b32;
  border: 1px solid #f7d7a8;
}

.footer-btn-pending:hover:not(:disabled) {
  background: #fef3e2;
  border-color: #d89b32;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(216, 155, 50, 0.2);
}

.footer-btn-primary {
  background: var(--primary, #476996);
  color: white;
  box-shadow: 0 2px 4px rgba(71, 105, 150, 0.2);
}

.footer-btn-primary:hover:not(:disabled) {
  background: var(--primary-hover, #35527a);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(71, 105, 150, 0.3);
}

.footer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@media (max-width: 768px) {
  .modern-modal-header {
    padding: 20px;
  }

  .modern-modal-title {
    font-size: 18px;
  }

  .modern-modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-info {
    order: -1;
  }

  .footer-actions {
    width: 100%;
    flex-direction: column;
  }

  .footer-btn {
    width: 100%;
  }
}

/* Import Modal Styles */
.import-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.import-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border: 2px solid var(--border, #CBD5E1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.import-option:hover {
  border-color: var(--primary, #476996);
  background: var(--primary-soft, #EEF2FF);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.15);
}

.option-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary, #476996), var(--primary-hover, #35527a));
  border-radius: 12px;
  color: white;
  flex-shrink: 0;
}

.option-content {
  flex: 1;
}

.option-title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
}

.option-description {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

.option-hint {
  font-size: 12px;
  color: var(--text-secondary, #64748B);
  background: #f8fafc;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
}

.option-arrow {
  color: var(--text-secondary, #64748B);
  flex-shrink: 0;
}

.import-option:hover .option-arrow {
  color: var(--primary, #476996);
  transform: translateX(4px);
}

.import-section {
  margin-top: 16px;
}

.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: #f8fafc;
  border: 2px dashed var(--border, #CBD5E1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.upload-zone:hover {
  border-color: var(--primary, #476996);
  background: var(--primary-soft, #EEF2FF);
}

.upload-zone svg {
  color: var(--primary, #476996);
  margin-bottom: 16px;
}

.upload-text {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
}

.upload-hint {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #64748B);
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px 16px;
  background: white;
  border: 1px solid var(--border, #CBD5E1);
  border-radius: 8px;
}

.selected-file svg {
  color: var(--primary, #476996);
  flex-shrink: 0;
}

.selected-file span {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary, #1E293B);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-clear-file {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary, #64748B);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-clear-file:hover {
  background: #fee;
  color: #dc2626;
}

@media (max-width: 768px) {
  .import-option {
    padding: 16px;
  }

  .option-icon {
    width: 48px;
    height: 48px;
  }

  .option-icon svg {
    width: 24px;
    height: 24px;
  }

  .option-title {
    font-size: 15px;
  }

  .option-description {
    font-size: 13px;
  }

  .upload-zone {
    padding: 32px 16px;
  }
}
</style>

<template>
  <div class="exam-edit-view">
    <!-- 上方：考卷資訊表單 -->
    <ExamForm
      :exam="exam"
      :saving="savingExam"
      @save="handleSaveExam"
      @cancel="handleCancel"
    />

    <!-- PDF 匯入區 -->
    <PdfUploadSection
      ref="pdfUploadSectionRef"
      @import-success="handlePdfImport"
    />

    <!-- 下方：左右分欄 -->
    <div class="content-container">
      <!-- 左側：題目編輯器 -->
      <div class="left-panel">
        <QuestionEditor
          :question="selectedQuestion"
          :exam-question="selectedExamQuestion"
          :saving="savingQuestion"
          @save="handleSaveQuestion"
        />
      </div>

      <!-- 右側：題目列表 -->
      <div class="right-panel">
        <div class="right-panel-inner">
          <div class="d-flex gap-2 align-items-center ps-3 pe-3 pt-2 pb-2 border-bottom flex-wrap">
            <button class="btn btn-sm btn-secondary" @click="isAutoDistributeModalVisible = true" :disabled="autoDistributeLoading">自動配分</button>
            <button class="btn btn-sm btn-secondary" @click="showBulkTagModal = true">
              批次編輯標籤{{ selectedQuestionIds.length > 0 ? ` (${selectedQuestionIds.length})` : '' }}
            </button>
            <button class="btn btn-sm btn-secondary" @click="showBulkSubjectModal = true">
              批次編輯科目{{ selectedQuestionIds.length > 0 ? ` (${selectedQuestionIds.length})` : '' }}
            </button>
            <button 
              v-if="selectedQuestionIds.length > 0" 
              class="btn btn-sm btn-danger" 
              @click="handleBulkRemove"
            >
              批次移除 ({{ selectedQuestionIds.length }})
            </button>
          </div>
          <div class="question-list-wrapper">
            <QuestionList
              ref="questionListRef"
              :questions="allQuestions"
              :selected-question-id="selectedQuestionId"
              :loading="loadingQuestions"
              v-model:total-points="autoPointsTotal"
              :auto-distribute-loading="autoDistributeLoading"
              :pending-edits="pendingQuestionEdits"
              :show-auto-distribute="false"
              @select-question="handleSelectQuestion"
              @add-question="handleAddQuestion"
              @add-existing-question="showAddModal = true"
              @remove-question="handleRemoveQuestion"
              @auto-distribute="autoDistributePoints"
              @update:selected-ids="handleSelectedIdsChange"
            />
          </div>
          <div class="right-actions">
            <!-- Reserved for other actions or quick links -->
          </div>
        </div>
      </div>
    </div>

    <!-- 新增題目的彈窗 -->
    <AddQuestionModal
      v-if="showAddModal"
      @close="showAddModal = false"
      @add="handleAddQuestionToExam"
    />
    <BulkTagEditor 
      v-if="showBulkTagModal" 
      :questions="allQuestions" 
      :pendingQuestions="pendingQuestions" 
      :examId="examId" 
      :preselectedIds="selectedQuestionIds"
      @close="showBulkTagModal=false" 
      @applied="handleBulkTagsApplied" 
    />
    <BulkSubjectEditor 
      v-if="showBulkSubjectModal" 
      :questions="allQuestions" 
      :pendingQuestions="pendingQuestions" 
      :examId="examId" 
      :preselectedIds="selectedQuestionIds"
      @close="showBulkSubjectModal=false" 
      @applied="handleBulkSubjectApplied" 
    />

    <!-- 儲存進度 Modal -->
    <div v-if="isSavingProgressVisible" class="modal d-block" style="background: rgba(0, 0, 0, 0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">儲存進度</h5>
          </div>
          <div class="modal-body">
            <p class="mb-2">{{ savingProgressMessage }}</p>
            <p v-if="savingTotalSteps > 0" class="text-muted small mb-3">
              {{ savingCurrentStep }}/{{ savingTotalSteps }}
            </p>
            <div class="progress">
              <div
                class="progress-bar progress-bar-striped progress-bar-animated"
                role="progressbar"
                :style="{ width: savingProgressPercent + '%' }"
                :aria-valuenow="savingProgressPercent"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                {{ savingProgressPercent }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 自動配分 Modal -->
    <div v-if="isAutoDistributeModalVisible" class="modal d-block" style="background: rgba(0, 0, 0, 0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">自動配分試算</h5>
            <button type="button" class="btn-close" @click="isAutoDistributeModalVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="autoDistributePointsInput" class="form-label">滿分</label>
              <input
                id="autoDistributePointsInput"
                v-model.number="autoPointsTotal"
                type="number"
                min="1"
                step="0.01"
                class="form-control"
                @input="calculateAutoDistribute"
              />
            </div>
            <div v-if="autoDistributeQuotaList.length > 0" class="card bg-light">
              <div class="card-body">
                <div class="row">
                  <div class="col-6">
                    <p class="text-muted mb-1">題數</p>
                    <p class="fs-5 fw-bold">{{ autoDistributeQuotaList.length }} 題</p>
                  </div>
                  <div class="col-6">
                    <p class="text-muted mb-1">平均配分</p>
                    <p class="fs-5 fw-bold">{{ (autoPointsTotal / autoDistributeQuotaList.length).toFixed(2) }} 分</p>
                  </div>
                </div>
              </div>
            </div>
            <p v-if="autoDistributeMessage" class="text-muted small mt-3 mb-0">{{ autoDistributeMessage }}</p>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="isAutoDistributeModalVisible = false"
            >
              取消
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="applyAutoDistribute"
            >
              確認配分
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ExamForm from '../components/ExamForm.vue'
import QuestionEditor from '../components/QuestionEditor.vue'
import QuestionList from '../components/QuestionList.vue'
import AddQuestionModal from '../components/AddQuestionModal.vue'
import BulkTagEditor from '../components/BulkTagEditor.vue'
import BulkSubjectEditor from '../components/BulkSubjectEditor.vue'
import PdfUploadSection from '../components/PdfUploadSection.vue'
import examService from '../services/examService'
import questionService from '../services/questionService'
import { usePdfImportStore } from '@/stores/pdfImport'

const route = useRoute()
const router = useRouter()

// 考卷資料
const exam = ref(null)
const examQuestions = ref([])
const autoPointsTotal = ref(100)
const autoDistributeLoading = ref(false)
const pendingQuestionEdits = ref({})

// 暫存的 PDF 解析題目（尚未儲存到資料庫）
const pendingQuestions = ref([])

// 選中的題目
const selectedQuestionId = ref(null)
const selectedQuestion = ref(null)
const selectedExamQuestion = ref(null)

// 多選的題目 IDs
const selectedQuestionIds = ref([])
const questionListRef = ref(null)

// 載入和儲存狀態
const loadingQuestions = ref(false)
const savingExam = ref(false)
const savingQuestion = ref(false)

// 儲存進度 Modal
const isSavingProgressVisible = ref(false)
const savingProgressMessage = ref('準備儲存...')
const savingProgressPercent = ref(0)
const savingCurrentStep = ref(0)
const savingTotalSteps = ref(0)
const savingStepType = ref('') // 'exam', 'questions', 'updates'

// 新增題目彈窗
const showAddModal = ref(false)
const showBulkTagModal = ref(false)
const showBulkSubjectModal = ref(false)

// 自動配分 Modal
const isAutoDistributeModalVisible = ref(false)
const autoDistributeQuotaList = ref([])
const autoDistributeMessage = ref('')

const pdfImportStore = usePdfImportStore()

// 計算 examId
const examId = computed(() => {
  return route.params.id ? parseInt(route.params.id) : null
})

// 合併已儲存的題目和暫存的題目
const allQuestions = computed(() => {
  // 已儲存的題目
  const saved = examQuestions.value.map(eq => ({
    ...eq,
    isPending: false
  }))

  // 暫存的題目（加上 pending 標記）
  const pending = pendingQuestions.value.map((q, index) => ({
    id: `pending-${index}`,
    question: null,
    order: q.order !== undefined ? q.order : (saved.length + index + 1),
    points: q.points || 0,
    question_content: q.content || q.question || '',
    question_subject: q.subject || exam.value?.name || '',
    question_category: q.category || '',
    isPending: true,
    pendingData: q // 保存完整的暫存資料
  }))

  return [...saved, ...pending]
})

// 載入考卷資料
const loadExam = async () => {
  if (!examId.value) {
    // 新建模式
    exam.value = null
    return
  }

  try {
    const response = await examService.getExam(examId.value)
    exam.value = response.data
    examQuestions.value = response.data.exam_questions || []
  } catch (error) {
    console.error('載入考卷失敗:', error)
    alert('載入考卷失敗')
  }
}

// 儲存考卷
const handleSaveExam = async (examData) => {
  savingExam.value = true
  isSavingProgressVisible.value = true
  savingProgressMessage.value = '準備儲存...'
  savingProgressPercent.value = 0

  try {
    let currentExamId = examId.value

    savingProgressMessage.value = '儲存考卷資訊...'
    savingProgressPercent.value = 10

    if (currentExamId) {
      // 更新現有考卷
      const response = await examService.updateExam(currentExamId, examData)
      exam.value = response.data
    } else {
      // 建立新考卷
      const response = await examService.createExam(examData)
      exam.value = response.data
      currentExamId = response.data.id
      // 導向編輯頁面
      await router.replace(`/admin/exams/${response.data.id}/edit`)
    }

    const summaryParts = []
    let shouldReload = false

    // 如果有暫存的題目，批次建立並加入考卷（改用 bulk API）
    if (pendingQuestions.value.length > 0) {
      savingProgressMessage.value = `建立題目中`
      savingProgressPercent.value = 20
      savingStepType.value = 'questions'
      savingTotalSteps.value = pendingQuestions.value.length
      savingCurrentStep.value = 0

      console.log(`開始批次建立 ${pendingQuestions.value.length} 個題目...`)
      const createPayload = []
      const meta = [] // keep mapping of index -> order & points for later adding to exam
      let skipCount = 0

      for (let i = 0; i < pendingQuestions.value.length; i++) {
        const questionData = pendingQuestions.value[i]
        const questionPayload = {
          subject: questionData.subject,
          category: questionData.category,
          question_type: questionData.question_type || '選擇題',
          difficulty: questionData.difficulty || 'medium',
          content: questionData.content,
          explanation: questionData.explanation,
          status: 'published',
          options: questionData.options,
          tag_ids: questionData.tag_ids || []
        }

        // basic validation: ensure required fields exist
        if (!questionPayload.content || !questionPayload.content.trim() || !questionPayload.subject || !questionPayload.subject.trim()) {
          console.warn(`跳過建立題目 #${i + 1}: content or subject 為空`)
          skipCount++
          continue
        }

        createPayload.push(questionPayload)
        meta.push({ index: i, order: questionData.order !== undefined ? questionData.order : (examQuestions.value.length + i + 1), points: questionData.points })
      }

      let successCount = 0
      let failCount = 0
      if (createPayload.length > 0) {
        try {
          const res = await questionService.bulkCreateQuestions(createPayload)
          const results = res.data?.results || res.data
          for (let i = 0; i < results.length; i++) {
            const r = results[i]
            const m = meta[i]
            
            // 更新進度
            savingCurrentStep.value = i + 1
            savingProgressMessage.value = `建立題目中 (${i + 1}/${results.length}題)`
            savingProgressPercent.value = 20 + Math.floor((i / results.length) * 30)

            if (r.success) {
              // Add created question to exam
              try {
                await examService.addQuestionToExam(currentExamId, {
                  question: r.id,
                  order: m.order,
                  points: m.points
                })
                successCount++
              } catch (err) {
                console.error('加入考卷失敗', err)
                failCount++
              }
            } else {
              failCount++
              const detail = r.errors
              summaryParts.push(`${r.index !== undefined ? `第 ${r.index + 1} 題`: '某題'} 建立失敗: ${JSON.stringify(detail)}`)
            }
          }
        } catch (err) {
          // fallback: if bulk create failed entirely, try single create to get more info - but for now, treat as failed
          console.error('批次建立題目失敗', err)
          summaryParts.push(`批次建立題目失敗: ${err.response?.data || err.message}`)
          failCount += createPayload.length
        }
      }

      // 清空暫存列表（已加入或嘗試加入）
      pendingQuestions.value = []
      shouldReload = true
      summaryParts.push(`題目建立：成功 ${successCount} 題，失敗 ${failCount} 題，略過 ${skipCount} 題`)
    }

    savingProgressMessage.value = '更新題目設定中'
    savingProgressPercent.value = 50
    savingStepType.value = 'updates'

    const { questionUpdates, settingUpdates, errors: editErrors } = await applyPendingQuestionEdits(currentExamId)
    if (questionUpdates || settingUpdates || (editErrors && editErrors.length)) {
      shouldReload = true
      savingProgressPercent.value = 75
      summaryParts.push(`暫存更新：題目內容 ${questionUpdates} 題、配分/順序 ${settingUpdates} 題`)
      if (editErrors && editErrors.length) {
        editErrors.forEach(err => {
          summaryParts.push(`更新失敗：${JSON.stringify(err)}`)
        })
      }
    }

    if (shouldReload) {
      savingProgressMessage.value = '重新載入資料...'
      savingProgressPercent.value = 85
      await loadExam()
    }

    savingProgressMessage.value = '完成！'
    savingProgressPercent.value = 100

    const baseMessage = summaryParts.length
      ? `考卷儲存成功！\n${summaryParts.join('\n')}`
      : '考卷儲存成功'

    // 1 秒後關閉 Modal
    setTimeout(() => {
      isSavingProgressVisible.value = false
      savingProgressPercent.value = 0
      savingProgressMessage.value = '準備儲存...'
      savingCurrentStep.value = 0
      savingTotalSteps.value = 0
      savingStepType.value = ''
      alert(baseMessage)
    }, 1000)
  } catch (error) {
    console.error('儲存考卷失敗:', error)
    console.error('錯誤詳情:', error.response?.data)
    console.error('發送的資料:', examData)
    isSavingProgressVisible.value = false
    savingProgressPercent.value = 0
    savingProgressMessage.value = '準備儲存...'
    alert('儲存考卷失敗：' + JSON.stringify(error.response?.data || error.message))
  } finally {
    savingExam.value = false
  }
}

// PDF import dialog trigger removed from toolbar.

// 取消編輯
const handleCancel = () => {
  router.push('/admin/exams')
}

// 選擇題目
const handleSelectQuestion = async (examQuestion) => {
  selectedQuestionId.value = examQuestion.question
  selectedExamQuestion.value = {
    ...examQuestion,
    ...(pendingQuestionEdits.value[examQuestion.id]?.examSettings || {})
  }

  // 如果是暫存題目，直接使用暫存的資料
  if (examQuestion.isPending && examQuestion.pendingData) {
    selectedQuestion.value = {
      id: null,
      subject: examQuestion.pendingData.subject,
      category: examQuestion.pendingData.category,
      question_type: examQuestion.pendingData.question_type || '選擇題',
      difficulty: examQuestion.pendingData.difficulty || 'medium',
      content: examQuestion.pendingData.content,
      explanation: examQuestion.pendingData.explanation,
      status: 'draft',
      options: examQuestion.pendingData.options || [],
      tag_ids: examQuestion.pendingData.tag_ids || [],
      tags: null // 標籤從 tag_ids 解析，讓 QuestionEditor 自行處理
    }
    return
  }

  // 載入完整的題目資料（已儲存的題目）
  if (!examQuestion.question) return

  loadingQuestions.value = true
  try {
    const response = await questionService.getQuestion(examQuestion.question)
    const pendingEdit = pendingQuestionEdits.value[examQuestion.id]
    selectedQuestion.value = pendingEdit?.questionData
      ? { ...response.data, ...pendingEdit.questionData }
      : response.data
  } catch (error) {
    console.error('載入題目失敗:', error)
    alert('載入題目失敗')
  } finally {
    loadingQuestions.value = false
  }
}

// 重新排序暫存題目（當修改 order 時自動調整其他暫存題目）
// 注意：已保存的題目會由後端 API 自動重排序
const reorderPendingQuestions = (currentId, newOrder, oldOrder) => {
  // 獲取所有題目（已保存的和暫存的）
  const allQs = allQuestions.value

  // 如果順序沒變，不需要重排
  if (newOrder === oldOrder) return

  // 只調整暫存題目的順序（已保存的題目會由後端自動處理）
  allQs.forEach(q => {
    if (q.id === currentId) return // 跳過當前題目
    if (!q.isPending) return // 跳過已保存的題目（後端會處理）

    const qOrder = q.order || 0

    if (newOrder < oldOrder) {
      // 向前移動：原本在 [newOrder, oldOrder) 之間的題目順序 +1
      if (qOrder >= newOrder && qOrder < oldOrder) {
        const idx = parseInt(q.id.replace('pending-', ''))
        if (pendingQuestions.value[idx]) {
          pendingQuestions.value[idx].order = qOrder + 1
        }
      }
    } else {
      // 向後移動：(oldOrder, newOrder] 之間的題目順序 -1
      if (qOrder > oldOrder && qOrder <= newOrder) {
        const idx = parseInt(q.id.replace('pending-', ''))
        if (pendingQuestions.value[idx]) {
          pendingQuestions.value[idx].order = qOrder - 1
        }
      }
    }
  })
}

const queueExamQuestionEdit = (examQuestionId, payload) => {
  const current = pendingQuestionEdits.value[examQuestionId] || {}

  pendingQuestionEdits.value = {
    ...pendingQuestionEdits.value,
    [examQuestionId]: {
      questionId: payload.questionId || current.questionId,
      questionData: payload.questionData || current.questionData,
      examSettings: payload.examSettings
        ? { ...(current.examSettings || {}), ...payload.examSettings }
        : current.examSettings
    }
  }
}

const applyPendingQuestionEdits = async (currentExamId) => {
  if (!currentExamId) {
    return { questionUpdates: 0, settingUpdates: 0 }
  }

  const entries = Object.entries(pendingQuestionEdits.value)
  if (!entries.length) {
    return { questionUpdates: 0, settingUpdates: 0 }
  }

  let questionUpdates = 0
  let settingUpdates = 0
  const errors = []

  for (let idx = 0; idx < entries.length; idx++) {
    const [examQuestionId, edit] = entries[idx]
    
    // 更新進度
    savingCurrentStep.value = idx + 1
    savingProgressMessage.value = `更新題目設定中 (${idx + 1}/${entries.length}題)`
    savingProgressPercent.value = 50 + Math.floor((idx / entries.length) * 25)

    if (edit.questionData && edit.questionId) {
      try {
        await questionService.updateQuestion(edit.questionId, edit.questionData)
        questionUpdates += 1
      } catch (err) {
        console.error('更新題目失敗:', err)
        errors.push({ id: edit.questionId, error: err.response?.data || err.message })
      }
    }

    if (edit.examSettings) {
      const payload = {}
      if (edit.examSettings.order !== undefined) {
        payload.order = edit.examSettings.order
      }
      if (edit.examSettings.points !== undefined) {
        payload.points = edit.examSettings.points
      }

      if (Object.keys(payload).length > 0) {
        try {
          await examService.updateExamQuestion(currentExamId, {
            exam_question_id: Number(examQuestionId),
            ...payload
          })
          settingUpdates += 1
        } catch (err) {
          console.error('更新考卷題目設定失敗:', err)
          errors.push({ exam_question_id: Number(examQuestionId), error: err.response?.data || err.message })
        }
      }
    }
  }

  pendingQuestionEdits.value = {}
  return { questionUpdates, settingUpdates, errors }
}

// 儲存題目
const handleSaveQuestion = async ({ questionData, examSettings }) => {
  savingQuestion.value = true
  try {
    // 如果是暫存題目，只更新暫存資料
    if (selectedExamQuestion.value?.isPending) {
      const pendingId = selectedExamQuestion.value.id
      const index = parseInt(pendingId.replace('pending-', ''))

      if (pendingQuestions.value[index]) {
        const oldOrder = pendingQuestions.value[index].order || (examQuestions.value.length + index + 1)
        const newOrder = examSettings?.order || oldOrder

        // 如果順序改變了，重新排序其他暫存題目
        if (newOrder !== oldOrder) {
          reorderPendingQuestions(pendingId, newOrder, oldOrder)
        }

        // 更新暫存題目的資料
        pendingQuestions.value[index] = {
          ...pendingQuestions.value[index],
          subject: questionData.subject,
          category: questionData.category,
          question_type: questionData.question_type,
          difficulty: questionData.difficulty,
          tag_ids: questionData.tag_ids || pendingQuestions.value[index].tag_ids || [],
          content: questionData.content,
          explanation: questionData.explanation,
          options: questionData.options,
          points: examSettings?.points || pendingQuestions.value[index].points,
          order: newOrder
        }

        alert('暫存題目已更新\n請儲存考卷以建立此題目')

        // 重新選擇這個題目以刷新顯示
        await handleSelectQuestion(selectedExamQuestion.value)
      }
      return
    }

    if (!selectedExamQuestion.value || !selectedQuestionId.value) return

    queueExamQuestionEdit(selectedExamQuestion.value.id, {
      questionId: selectedQuestionId.value,
      questionData,
      examSettings: examSettings || undefined
    })

    const eqIndex = examQuestions.value.findIndex(eq => eq.id === selectedExamQuestion.value.id)
    if (eqIndex !== -1) {
      const current = examQuestions.value[eqIndex]
      examQuestions.value[eqIndex] = {
        ...current,
        question_content: questionData.content,
        question_subject: questionData.subject,
        question_category: questionData.category,
        points: examSettings?.points ?? current.points,
        order: examSettings?.order ?? current.order
      }
    }

    selectedExamQuestion.value = {
      ...selectedExamQuestion.value,
      points: examSettings?.points ?? selectedExamQuestion.value.points,
      order: examSettings?.order ?? selectedExamQuestion.value.order,
      question_content: questionData.content,
      question_subject: questionData.subject,
      question_category: questionData.category
    }

    selectedQuestion.value = selectedQuestion.value
      ? { ...selectedQuestion.value, ...questionData }
      : { ...questionData }

    alert('變更已暫存，請於儲存考卷後套用至資料庫。')
  } catch (error) {
    console.error('儲存題目失敗:', error)
    alert('儲存題目失敗：' + (error.response?.data?.message || error.message))
  } finally {
    savingQuestion.value = false
  }
}

// 新增空白題目
const handleAddQuestion = () => {
  // 創建一個新的空白題目到 pending 列表
  const newQuestion = {
    content: '',
    subject: exam.value?.name || '未分類',
    category: '選擇題',
    question_type: '選擇題',
    difficulty: 'medium',
    tag_ids: [],
    explanation: '',
    options: [
      { content: '', is_correct: false },
      { content: '', is_correct: false },
      { content: '', is_correct: false },
      { content: '', is_correct: false }
    ],
    points: 1
  }

  // 加入到暫存列表
  pendingQuestions.value.push(newQuestion)

  // 自動選中這個新題目
  const newIndex = pendingQuestions.value.length - 1
  const newExamQuestion = {
    id: `pending-${newIndex}`,
    question: null,
    order: examQuestions.value.length + newIndex + 1,
    points: newQuestion.points,
    question_content: newQuestion.content,
    question_subject: newQuestion.subject,
    question_category: newQuestion.category,
    isPending: true,
    pendingData: newQuestion
  }

  handleSelectQuestion(newExamQuestion)
}

// 將題目新增到考卷（支援多選）
const handleAddQuestionToExam = async (questionIds, points) => {
  if (!examId.value) return

  // 確保 questionIds 是陣列
  const ids = Array.isArray(questionIds) ? questionIds : [questionIds]
  
  try {
    let successCount = 0
    let failCount = 0
    const currentOrder = examQuestions.value.length

    for (let i = 0; i < ids.length; i++) {
      try {
        await examService.addQuestionToExam(examId.value, {
          question: ids[i],
          order: currentOrder + i + 1,
          points: points
        })
        successCount++
      } catch (err) {
        console.error(`新增題目 ${ids[i]} 失敗:`, err)
        failCount++
      }
    }

    showAddModal.value = false
    
    if (failCount === 0) {
      alert(`成功新增 ${successCount} 題`)
    } else {
      alert(`新增完成：成功 ${successCount} 題，失敗 ${failCount} 題`)
    }

    // 重新載入考卷資料
    await loadExam()
  } catch (error) {
    console.error('新增題目失敗:', error)
    alert('新增題目失敗：' + (error.response?.data?.message || error.message))
  }
}

// 處理多選變更
const handleSelectedIdsChange = (ids) => {
  selectedQuestionIds.value = ids
}

const handleBulkTagsApplied = async ({ successCount, errors, pendingUpdates = [] }) => {
  let msg = `已成功更新 ${successCount} 題。`
  if (errors && errors.length) {
    msg += `
失敗：${errors.length} 題，詳情請查看 console。`
    console.error('批次標籤更新錯誤：', errors)
  }
  alert(msg)
  // Apply pending updates locally
  if (pendingUpdates.length) {
    pendingUpdates.forEach(u => {
      if (pendingQuestions.value[u.idx]) {
        pendingQuestions.value[u.idx].tag_ids = u.tag_ids
      }
    })
  }
  // Reload exam only if some saved questions were updated
  if (successCount > 0) {
    await loadExam()
  }
}

const handleBulkSubjectApplied = async ({ successCount, errors, pendingUpdates = [] }) => {
  let msg = `已成功更新 ${successCount} 題。`
  if (errors && errors.length) {
    msg += `
失敗：${errors.length} 題，詳情請查看 console。`
    console.error('批次科目更新錯誤：', errors)
  }
  alert(msg)
  // Apply pending updates locally
  if (pendingUpdates.length) {
    pendingUpdates.forEach(u => {
      if (pendingQuestions.value[u.idx]) {
        pendingQuestions.value[u.idx].subject = u.subject
      }
    })
  }
  // Reload exam only if some saved questions were updated
  if (successCount > 0) {
    await loadExam()
  }
}

// 從考卷移除題目
const handleRemoveQuestion = async (examQuestionId) => {
  if (!confirm('確定要移除這個題目嗎？')) return

  try {
    // 如果是暫存題目，直接從陣列中移除
    if (typeof examQuestionId === 'string' && examQuestionId.startsWith('pending-')) {
      const index = parseInt(examQuestionId.replace('pending-', ''))
      pendingQuestions.value.splice(index, 1)

      // 如果移除的是當前選中的題目，清空選擇
      if (selectedExamQuestion.value?.id === examQuestionId) {
        selectedQuestionId.value = null
        selectedQuestion.value = null
        selectedExamQuestion.value = null
      }

      alert('暫存題目已移除')
      return
    }

    // 已儲存的題目，呼叫 API 移除
    if (pendingQuestionEdits.value[examQuestionId]) {
      const nextEdits = { ...pendingQuestionEdits.value }
      delete nextEdits[examQuestionId]
      pendingQuestionEdits.value = nextEdits
    }

    await examService.removeQuestionFromExam(examId.value, examQuestionId)
    alert('題目移除成功')

    // 如果移除的是當前選中的題目，清空選擇
    if (selectedExamQuestion.value?.id === examQuestionId) {
      selectedQuestionId.value = null
      selectedQuestion.value = null
      selectedExamQuestion.value = null
    }

    // 重新載入考卷資料
    await loadExam()
  } catch (error) {
    console.error('移除題目失敗:', error)
    alert('移除題目失敗：' + (error.response?.data?.message || error.message))
  }
}

// 批次移除題目
const handleBulkRemove = async () => {
  if (selectedQuestionIds.value.length === 0) return
  if (!confirm(`確定要移除選取的 ${selectedQuestionIds.value.length} 個題目嗎？`)) return

  let successCount = 0
  let failCount = 0

  for (const id of selectedQuestionIds.value) {
    try {
      if (typeof id === 'string' && id.startsWith('pending-')) {
        const index = parseInt(id.replace('pending-', ''))
        pendingQuestions.value.splice(index, 1)
        successCount++
      } else {
        if (pendingQuestionEdits.value[id]) {
          const nextEdits = { ...pendingQuestionEdits.value }
          delete nextEdits[id]
          pendingQuestionEdits.value = nextEdits
        }
        await examService.removeQuestionFromExam(examId.value, id)
        successCount++
      }
    } catch (err) {
      console.error(`移除題目 ${id} 失敗:`, err)
      failCount++
    }
  }

  // 清空選擇
  selectedQuestionIds.value = []
  selectedQuestionId.value = null
  selectedQuestion.value = null
  selectedExamQuestion.value = null

  if (failCount === 0) {
    alert(`成功移除 ${successCount} 題`)
  } else {
    alert(`移除完成：成功 ${successCount} 題，失敗 ${failCount} 題`)
  }

  await loadExam()
}

const startAutoDistribute = async () => {
  calculateAutoDistribute()
}

const calculateAutoDistribute = () => {
  const questions = [...allQuestions.value].sort((a, b) => {
    const orderA = Number.isFinite(Number(a.order)) ? Number(a.order) : Number.MAX_SAFE_INTEGER
    const orderB = Number.isFinite(Number(b.order)) ? Number(b.order) : Number.MAX_SAFE_INTEGER
    if (orderA === orderB) {
      return String(a.id).localeCompare(String(b.id))
    }
    return orderA - orderB
  })

  if (!questions.length) {
    autoDistributeMessage.value = '目前尚無題目可配分'
    autoDistributeQuotaList.value = []
    return
  }

  const total = Number(autoPointsTotal.value)
  if (!Number.isFinite(total) || total <= 0) {
    autoDistributeMessage.value = '請輸入大於 0 的滿分'
    autoDistributeQuotaList.value = []
    return
  }

  const totalCents = Math.round(total * 100)
  const count = questions.length
  const base = Math.floor(totalCents / count)
  let remainder = totalCents - base * count

  autoDistributeQuotaList.value = questions.map((question) => {
    let cents = base
    if (remainder > 0) {
      cents += 1
      remainder -= 1
    }
    const points = cents / 100

    return {
      id: question.id,
      content: question.question_content || question.pendingData?.content || '（暫存題目）',
      points: points
    }
  })

  autoDistributeMessage.value = `將自動均勻分配 ${total} 分至 ${count} 題`
}

const applyAutoDistribute = async () => {
  if (autoDistributeQuotaList.value.length === 0) {
    alert('請先計算配分試算')
    return
  }

  autoDistributeLoading.value = true

  try {
    const questions = [...allQuestions.value].sort((a, b) => {
      const orderA = Number.isFinite(Number(a.order)) ? Number(a.order) : Number.MAX_SAFE_INTEGER
      const orderB = Number.isFinite(Number(b.order)) ? Number(b.order) : Number.MAX_SAFE_INTEGER
      if (orderA === orderB) {
        return String(a.id).localeCompare(String(b.id))
      }
      return orderA - orderB
    })

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i]
      const quotaItem = autoDistributeQuotaList.value[i]
      const points = quotaItem.points

      if (question.isPending) {
        const pendingIndex = parseInt(String(question.id).replace('pending-', ''), 10)
        if (!Number.isNaN(pendingIndex) && pendingQuestions.value[pendingIndex]) {
          pendingQuestions.value[pendingIndex].points = points
        }
      } else if (question.id) {
        queueExamQuestionEdit(question.id, {
          examSettings: { points }
        })

        const eqIndex = examQuestions.value.findIndex(eq => eq.id === question.id)
        if (eqIndex !== -1) {
          examQuestions.value[eqIndex] = {
            ...examQuestions.value[eqIndex],
            points
          }
        }

        if (selectedExamQuestion.value?.id === question.id) {
          selectedExamQuestion.value = {
            ...selectedExamQuestion.value,
            points
          }
        }
      }
    }

    isAutoDistributeModalVisible.value = false
    autoDistributeQuotaList.value = []
    autoDistributeMessage.value = ''
    alert(`已配分完成！請記得儲存考卷以套用變更。`)
  } catch (error) {
    console.error('應用配分失敗:', error)
    alert('應用配分失敗，請稍後再試。')
  } finally {
    autoDistributeLoading.value = false
  }
}

const autoDistributePoints = async () => {
  // 打開配分試算 Modal
  isAutoDistributeModalVisible.value = true
  calculateAutoDistribute()
}

// 處理 PDF 匯入
const handlePdfImport = ({ examData, questions, answers }) => {
  console.log('處理 PDF 匯入:', { examData, questions, answers })

  // 1. 自動填寫考卷欄位
  if (examData) {
    exam.value = {
      name: examData.name || exam.value?.name || '',
      description: examData.description || exam.value?.description || '',
      time_limit: examData.time_limit || exam.value?.time_limit || null
    }
  }

  // 2. 將解析的題目加入暫存列表
  const processedQuestions = questions.map((q, index) => {
    // 取得此題目的答案
    const correctAnswer = answers?.answers?.[index] || q.correct_answer
    const hasModifiedAnswer = correctAnswer === '*'

    // 處理選項：將字串陣列轉換為物件陣列，並根據答案標記正確選項
    const options = (q.options || []).map((optionText, optIndex) => {
      const optionLabel = String.fromCharCode(65 + optIndex) // A, B, C, D...
      return {
        content: typeof optionText === 'string' ? optionText : (optionText.content || ''),
        is_correct: !hasModifiedAnswer && correctAnswer === optionLabel // 如果答案是 *，則不標記任何選項為正確
      }
    })

    return {
      content: q.content || q.question || `題目 ${index + 1}`,
      subject: examData?.subject || '未分類',
      category: examData?.category || '選擇題',
      explanation: q.explanation || '',
      options: options,
      points: q.points || 0,
      correct_answer: correctAnswer,
      has_modified_answer: hasModifiedAnswer
    }
  })

  // 將新題目加入暫存列表
  pendingQuestions.value = [...pendingQuestions.value, ...processedQuestions]

  console.log(`已加入 ${processedQuestions.length} 個暫存題目`)
  alert(`已匯入 ${processedQuestions.length} 題到暫存列表\n請儲存考卷以建立這些題目`)
}

const consumePendingPdfImport = () => {
  const payload = pdfImportStore.consumePayload()
  if (payload) {
    handlePdfImport(payload)
  }
}

onMounted(async () => {
  await loadExam()
  consumePendingPdfImport()
})
</script>

<style scoped>
.exam-edit-view {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  height: calc(100vh - 300px);
  min-height: 600px;
}

.left-panel,
.right-panel {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.right-panel-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

@media (max-width: 1200px) {
  .content-container {
    grid-template-columns: 1fr;
    height: auto;
  }

  .left-panel,
  .right-panel {
    height: 600px;
    display: flex;
    flex-direction: column;
  }
}

.question-list-wrapper {
  flex: 1;
  min-height: 0; /* for proper scrolling in flex container */
  overflow: auto;
}
.question-list-wrapper > * {
  height: 100%;
}
.right-actions {
  padding: 12px 0 0 0;
  display:flex;
  gap:8px;
}
</style>

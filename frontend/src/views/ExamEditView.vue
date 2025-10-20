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
        <QuestionList
          :questions="allQuestions"
          :selected-question-id="selectedQuestionId"
          :loading="loadingQuestions"
          @select-question="handleSelectQuestion"
          @add-question="handleAddQuestion"
          @remove-question="handleRemoveQuestion"
        />
      </div>
    </div>

    <!-- 新增題目的彈窗 -->
    <AddQuestionModal
      v-if="showAddModal"
      @close="showAddModal = false"
      @add="handleAddQuestionToExam"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ExamForm from '../components/ExamForm.vue'
import QuestionEditor from '../components/QuestionEditor.vue'
import QuestionList from '../components/QuestionList.vue'
import AddQuestionModal from '../components/AddQuestionModal.vue'
import PdfUploadSection from '../components/PdfUploadSection.vue'
import examService from '../services/examService'
import questionService from '../services/questionService'

const route = useRoute()
const router = useRouter()

// 考卷資料
const exam = ref(null)
const examQuestions = ref([])

// 暫存的 PDF 解析題目（尚未儲存到資料庫）
const pendingQuestions = ref([])

// 選中的題目
const selectedQuestionId = ref(null)
const selectedQuestion = ref(null)
const selectedExamQuestion = ref(null)

// 載入和儲存狀態
const loadingQuestions = ref(false)
const savingExam = ref(false)
const savingQuestion = ref(false)

// 新增題目彈窗
const showAddModal = ref(false)

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
  try {
    let currentExamId = examId.value

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

    // 如果有暫存的題目，批次建立並加入考卷
    if (pendingQuestions.value.length > 0) {
      console.log(`開始批次建立 ${pendingQuestions.value.length} 個題目...`)

      let successCount = 0
      let failCount = 0

      for (let i = 0; i < pendingQuestions.value.length; i++) {
        const questionData = pendingQuestions.value[i]

        try {
          // 建立題目
          const questionPayload = {
            subject: questionData.subject,
            category: questionData.category,
            content: questionData.content,
            explanation: questionData.explanation,
            status: 'published',
            options: questionData.options
          }

          const createResponse = await questionService.createQuestion(questionPayload)
          const newQuestion = createResponse.data

          // 將題目加入考卷，使用暫存題目中的 order（如果有的話）
          await examService.addQuestionToExam(currentExamId, {
            question: newQuestion.id,
            order: questionData.order !== undefined ? questionData.order : (examQuestions.value.length + i + 1),
            points: questionData.points
          })

          successCount++
        } catch (error) {
          console.error(`建立題目 ${i + 1} 失敗:`, error)
          failCount++
        }
      }

      // 清空暫存列表
      pendingQuestions.value = []

      // 重新載入考卷資料
      await loadExam()

      alert(`考卷儲存成功！\n題目建立：成功 ${successCount} 題，失敗 ${failCount} 題`)
    } else {
      alert('考卷儲存成功')
    }
  } catch (error) {
    console.error('儲存考卷失敗:', error)
    console.error('錯誤詳情:', error.response?.data)
    console.error('發送的資料:', examData)
    alert('儲存考卷失敗：' + JSON.stringify(error.response?.data || error.message))
  } finally {
    savingExam.value = false
  }
}

// 取消編輯
const handleCancel = () => {
  router.push('/admin/exams')
}

// 選擇題目
const handleSelectQuestion = async (examQuestion) => {
  selectedQuestionId.value = examQuestion.question
  selectedExamQuestion.value = examQuestion

  // 如果是暫存題目，直接使用暫存的資料
  if (examQuestion.isPending && examQuestion.pendingData) {
    selectedQuestion.value = {
      id: null,
      subject: examQuestion.pendingData.subject,
      category: examQuestion.pendingData.category,
      content: examQuestion.pendingData.content,
      explanation: examQuestion.pendingData.explanation,
      status: 'draft',
      options: examQuestion.pendingData.options || [],
      tags: []
    }
    return
  }

  // 載入完整的題目資料（已儲存的題目）
  if (!examQuestion.question) return

  loadingQuestions.value = true
  try {
    const response = await questionService.getQuestion(examQuestion.question)
    selectedQuestion.value = response.data
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

    // 已儲存的題目，正常更新
    if (!selectedQuestionId.value) return

    // 如果有考卷設定，更新考卷中的題目資訊
    // 注意：後端 API 會自動重排序其他題目，避免 unique constraint 衝突
    if (examSettings && selectedExamQuestion.value) {
      await examService.updateExamQuestion(examId.value, {
        exam_question_id: selectedExamQuestion.value.id,
        order: examSettings.order,
        points: examSettings.points
      })
    }

    // 更新題目本身
    await questionService.updateQuestion(selectedQuestionId.value, questionData)

    alert('題目儲存成功')

    // 重新載入考卷資料
    await loadExam()

    // 重新載入選中的題目
    if (selectedExamQuestion.value) {
      const updatedExamQuestion = examQuestions.value.find(
        eq => eq.id === selectedExamQuestion.value.id
      )
      if (updatedExamQuestion) {
        await handleSelectQuestion(updatedExamQuestion)
      }
    }
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

// 將題目新增到考卷
const handleAddQuestionToExam = async (questionId, order, points) => {
  if (!examId.value) return

  try {
    await examService.addQuestionToExam(examId.value, {
      question: questionId,
      order: order,
      points: points
    })

    showAddModal.value = false
    alert('題目新增成功')

    // 重新載入考卷資料
    await loadExam()
  } catch (error) {
    console.error('新增題目失敗:', error)
    alert('新增題目失敗：' + (error.response?.data?.message || error.message))
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

onMounted(() => {
  loadExam()
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
}

@media (max-width: 1200px) {
  .content-container {
    grid-template-columns: 1fr;
    height: auto;
  }

  .left-panel,
  .right-panel {
    height: 600px;
  }
}
</style>

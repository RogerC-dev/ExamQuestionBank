<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>批次編輯科目</h3>
        <button class="btn-close" @click="close">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>套用範圍</label>
          <div>
            <label><input type="radio" v-model="applyTo" value="all"> 全部題目</label>
            <label style="margin-left:16px"><input type="radio" v-model="applyTo" value="selected"> 選取題目</label>
          </div>
        </div>

        <div v-if="applyTo === 'selected'" class="form-group">
          <label>選擇題目</label>
          <div class="question-list">
            <label v-for="q in questions" :key="q.id || q.order" class="question-item">
              <input type="checkbox" v-model="selectedQuestionIds" :value="q.question || (q.id || q.order)"> 
              <span class="question-summary">{{ q.question_content || q.pendingData?.content || '未命名題目' }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>科目</label>
          <input v-model="selectedSubject" type="text" class="form-control" placeholder="輸入科目名稱">
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button class="btn btn-primary" :disabled="processing || !selectedSubject" @click="apply">套用</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import questionService from '@/services/questionService'

const props = defineProps({
  questions: { type: Array, required: true },
  pendingQuestions: { type: Array, required: true },
  examId: { type: Number, required: false }
})

const emit = defineEmits(['close', 'applied'])

const applyTo = ref('all')
const selectedSubject = ref('')
const selectedQuestionIds = ref([])
const processing = ref(false)

onMounted(async () => {
  // 不需要載入科目選項，使用者直接輸入
})

const targetQuestions = computed(() => {
  if (applyTo.value === 'all') return props.questions
  return props.questions.filter(q => selectedQuestionIds.value.includes(q.question || q.id || q.order))
})

const apply = async () => {
  processing.value = true
  const errors = []
  let successCount = 0
  const pendingUpdates = []

  const savedUpdates = []
  for (const q of targetQuestions.value) {
    try {
      if (q.isPending) {
        // pending question stored locally
        const idx = parseInt(q.id.toString().replace('pending-', ''), 10)
        if (props.pendingQuestions[idx]) {
          pendingUpdates.push({ idx, subject: selectedSubject.value })
          successCount++ // 計數暫存題目
        }
      } else {
        // saved question -> update via API
        savedUpdates.push({ id: q.question, subject: selectedSubject.value })
      }
    } catch (err) {
      console.error('更新題目科目失敗', q, err)
      errors.push({ id: q.question || q.id || q.order, error: err.response?.data || err.message })
    }
  }

  // Execute bulk update for saved questions if any
  if (savedUpdates.length > 0) {
    try {
      const res = await questionService.bulkUpdateQuestions(savedUpdates)
      const results = res.data?.results || res.data
      for (const r of results) {
        if (r.success) successCount++
        else errors.push({ id: r.index ?? r.id, error: r.errors })
      }
    } catch (err) {
      console.error('批次更新失敗', err)
      errors.push({ id: 'bulk-update', error: err.response?.data || err.message })
    }
  }

  processing.value = false
  emit('applied', { successCount, errors, pendingUpdates })
  close()
}

const close = () => emit('close')
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.4); z-index:1000 }
.modal-content { width:90%; max-width:900px; background:white; border-radius:6px; overflow:hidden }
.modal-header { display:flex; justify-content:space-between; padding:16px; border-bottom:1px solid #eee }
.modal-body { padding: 16px }
.modal-footer { padding: 12px 16px; display:flex; gap: 8px; justify-content:flex-end; border-top:1px solid #eee }
.question-list { max-height:220px; overflow:auto; border:1px solid #eee; padding:8px; border-radius:6px }
.question-item { display:flex; gap:8px; align-items:center; padding:4px 8px }
.question-summary { color:#444 }
.form-group { margin-bottom: 16px }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #333 }
.form-control { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px }
</style>

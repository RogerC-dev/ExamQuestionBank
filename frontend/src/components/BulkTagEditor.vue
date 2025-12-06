<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>批次編輯標籤</h3>
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
          <label>標籤操作</label>
          <div>
            <label><input type="radio" v-model="mode" value="add"> 新增標籤</label>
            <label style="margin-left:16px"><input type="radio" v-model="mode" value="remove"> 移除標籤</label>
          </div>
        </div>

        <div class="form-group">
          <label>標籤</label>
          <multiselect v-model="selectedTags" :options="tagOptions" :multiple="true" track-by="id" label="name" placeholder="選擇標籤"></multiselect>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button class="btn btn-primary" :disabled="processing || (selectedTags.length===0)" @click="apply">套用</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import tagService from '@/services/tagService'
import questionService from '@/services/questionService'

const props = defineProps({
  questions: { type: Array, required: true }, // examQuestions list
  pendingQuestions: { type: Array, required: true },
  examId: { type: Number, required: false }
})

const emit = defineEmits(['close', 'applied'])

const applyTo = ref('all')
const mode = ref('add')
const tagOptions = ref([])
const selectedTags = ref([])
const selectedQuestionIds = ref([])
const processing = ref(false)

onMounted(async () => {
  try {
    const res = await tagService.getTags()
    let items = res.data?.results || res.data
    if (!Array.isArray(items)) items = []
    tagOptions.value = items
  } catch (err) {
    console.error('載入標籤失敗', err)
  }
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

  for (const q of targetQuestions.value) {
    try {
      if (q.isPending) {
        // pending question stored locally (pendingQuestions indexed by pending-<index>)
        const idx = parseInt(q.id.toString().replace('pending-', ''), 10)
        if (props.pendingQuestions[idx]) {
          const current = props.pendingQuestions[idx]
          const currentTagIds = current.tag_ids || current.tags || []
          const tagIds = selectedTags.value.map(t => t.id)
          let newIds = []
          if (mode.value === 'add') {
            newIds = Array.from(new Set([...(currentTagIds || []), ...tagIds]))
          } else {
            newIds = (currentTagIds || []).filter(id => !tagIds.includes(id))
          }
          pendingUpdates.push({ idx, tag_ids: newIds })
        }
      } else {
        // saved question -> update via API
        // fetch current question tags if not present
        let currentQuestion = q.questionDetail
        if (!currentQuestion) {
          const res = await questionService.getQuestion(q.question)
          currentQuestion = res.data
        }
        const currentTagIds = currentQuestion.tags ? currentQuestion.tags.map(t => t.id) : []
        const tagIdsToModify = selectedTags.value.map(t => t.id)
        let newTagIds
        if (mode.value === 'add') {
          newTagIds = Array.from(new Set([...currentTagIds, ...tagIdsToModify]))
        } else {
          newTagIds = currentTagIds.filter(id => !tagIdsToModify.includes(id))
        }
        await questionService.updateQuestion(q.question, { tag_ids: newTagIds })
        successCount++
      }
    } catch (err) {
      console.error('更新題目標籤失敗', q, err)
      errors.push({ id: q.question || q.id || q.order, error: err.response?.data || err.message })
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
</style>

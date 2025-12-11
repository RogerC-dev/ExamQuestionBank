<template>
  <div class="question-editor">
    <div v-if="!question" class="empty-state">
      <p>請從右側選擇一個題目進行編輯，或新增一個題目</p>
    </div>

    <div v-else class="editor-content">
        <div class="editor-header">
        <h3>編輯題目</h3>
        <button class="btn btn-sm btn-success" @click="handleSave" :disabled="saving || !isFormValid">
          {{ saving ? '儲存中...' : '儲存' }}
        </button>
      </div>

      <div class="form-body">
        <form @submit.prevent="handleSave">
          <!-- 科目 -->
          <div class="form-group">
            <label for="subject">科目 *</label>
            <input
              id="subject"
              v-model="formData.subject"
              type="text"
              required
              placeholder="例：民法、刑法"
              class="form-input"
            />
            <div v-if="!formValidation.subject" style="color:#d32f2f; font-size:12px; margin-top:6px">科目為必填</div>
          </div>
  
          <!-- 題型分類 -->
          <div class="form-group">
            <label for="category">題型分類 *</label>
            <input
              id="category"
              v-model="formData.category"
              type="text"
              required
              placeholder="例：選擇題、申論題"
              class="form-input"
            />
          </div>

          <!-- 題型 -->
          <div class="form-group">
            <label for="question_type">題型</label>
            <select id="question_type" v-model="formData.question_type" class="form-input">
              <option value="選擇題">選擇題</option>
              <option value="多選題">多選題</option>
              <option value="是非題">是非題</option>
              <option value="申論題">申論題</option>
            </select>
          </div>

          <!-- 難度 -->
          <div class="form-group">
            <label for="difficulty">難度</label>
            <select id="difficulty" v-model="formData.difficulty" class="form-input">
              <option value="easy">容易</option>
              <option value="medium">中等</option>
              <option value="hard">困難</option>
            </select>
          </div>
  
          <!-- 題目內容 -->
          <div class="form-group">
            <label for="content">題目內容 *</label>
            <textarea
              id="content"
              v-model="formData.content"
              rows="5"
              required
              placeholder="請輸入題目內容"
              class="form-input"
            ></textarea>
            <div v-if="!formValidation.content" style="color:#d32f2f; font-size:12px; margin-top:6px">題目內容為必填</div>
          </div>
  
          <!-- 解析 -->
          <div class="form-group">
            <label for="explanation">解析</label>
            <textarea
              id="explanation"
              v-model="formData.explanation"
              rows="4"
              placeholder="請輸入題目解析"
              class="form-input"
            ></textarea>
          </div>
  
          <!-- 狀態 -->
          <div class="form-group">
            <label for="status">狀態</label>
            <select id="status" v-model="formData.status" class="form-input">
              <option value="draft">草稿</option>
              <option value="published">已發布</option>
            </select>
          </div>

          <!-- 標籤 (Multiselect) -->
          <div class="form-group">
            <label for="tags">標籤</label>
            <div style="display:flex; gap:8px; align-items:center;">
              <multiselect
                v-model="selectedTags"
                :options="tagOptions"
                :multiple="true"
                :close-on-select="false"
                :clear-on-select="false"
                :preserve-search="true"
                :internal-search="false"
                placeholder="選擇或新增標籤"
                track-by="id"
                label="name"
                @search-change="onTagSearch"
                style="flex:1"
              />
              <div style="display:flex; gap:8px; align-items:center">
                <input id="new-tag" v-model="newTagName" class="form-input" placeholder="新增標籤" @keyup.enter="handleCreateTag" />
                <button type="button" class="btn btn-sm btn-secondary" @click="handleCreateTag">新增</button>
              </div>
            </div>
          </div>
  
          <!-- 選項 -->
          <div class="form-group">
            <label>選項</label>
            <div class="options-list">
              <div
                v-for="(option, index) in formData.options"
                :key="index"
                class="option-item"
              >
                <input
                  v-model="option.content"
                  type="text"
                  placeholder="選項內容"
                  class="option-input"
                />
                <label class="checkbox-label">
                  <input
                    v-model="option.is_correct"
                    type="checkbox"
                  />
                  正確答案
                </label>
                <button
                  type="button"
                  class="btn-remove"
                  @click="removeOption(index)"
                >
                  ×
                </button>
              </div>
            </div>
            <button type="button" class="btn btn-sm btn-secondary" @click="addOption">
              + 新增選項
            </button>
          </div>
  
          <!-- 考卷中的順序和配分 (如果是從考卷編輯進來的) -->
          <div v-if="examQuestion" class="exam-settings">
            <h4>考卷設定</h4>
            <div class="form-row">
              <div class="form-group">
                <label for="order">順序</label>
                <input
                  id="order"
                  v-model.number="examSettings.order"
                  type="number"
                  min="1"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="points">配分</label>
                <input
                  id="points"
                  v-model.number="examSettings.points"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-input"
                />
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    default: null
  },
  examQuestion: {
    type: Object,
    default: null
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'save-exam-settings'])

const formData = ref({
  subject: '',
  category: '',
  question_type: '選擇題',
  difficulty: 'medium',
  content: '',
  explanation: '',
  status: 'draft',
  options: [],
  tag_ids: []
})

const examSettings = ref({
  order: 1,
  points: 0
})

// Tag options for multi-select (定義在 watch 之前)
const tagOptions = ref([])
const selectedTags = ref([])

// 監聽 question prop 的變化
watch(() => props.question, (newQuestion) => {
  if (newQuestion) {
    formData.value = {
      subject: newQuestion.subject || '',
      category: newQuestion.category || '',
      question_type: newQuestion.question_type || '選擇題',
      difficulty: newQuestion.difficulty || 'medium',
      content: newQuestion.content || '',
      explanation: newQuestion.explanation || '',
      status: newQuestion.status || 'draft',
      options: newQuestion.options ? [...newQuestion.options] : [],
      tag_ids: newQuestion.tag_ids ? newQuestion.tag_ids : (newQuestion.tags ? newQuestion.tags.map(t => t.id) : [])
    }
    // set selectedTags to match tag objects
    if (newQuestion.tags && Array.isArray(newQuestion.tags)) {
      selectedTags.value = newQuestion.tags
    } else if (newQuestion.tag_ids && Array.isArray(newQuestion.tag_ids) && tagOptions.value.length > 0) {
      selectedTags.value = tagOptions.value.filter(t => newQuestion.tag_ids.includes(t.id))
    } else {
      selectedTags.value = []
    }
  }
}, { immediate: true, deep: true })

// 監聯 tagOptions 載入完成後，重新設定 selectedTags
watch(() => tagOptions.value, (newTagOptions) => {
  if (newTagOptions.length > 0 && props.question?.tag_ids && Array.isArray(props.question.tag_ids)) {
    // 如果有 tag_ids 但 selectedTags 還是空的，重新設定
    if (selectedTags.value.length === 0 && props.question.tag_ids.length > 0) {
      selectedTags.value = newTagOptions.filter(t => props.question.tag_ids.includes(t.id))
    }
  }
}, { immediate: true })

// 監聽 examQuestion prop 的變化
watch(() => props.examQuestion, (newExamQuestion) => {
  if (newExamQuestion) {
    examSettings.value = {
      order: newExamQuestion.order || 1,
      points: newExamQuestion.points || 0
    }
  }
}, { immediate: true, deep: true })

const addOption = () => {
  formData.value.options.push({
    content: '',
    is_correct: false
  })
}

const removeOption = (index) => {
  formData.value.options.splice(index, 1)
}

const isFormValid = computed(() => {
  const content = (formData.value.content || '').toString().trim()
  const subject = (formData.value.subject || '').toString().trim()
  return content.length > 0 && subject.length > 0
})

const formValidation = computed(() => ({
  content: (formData.value.content || '').toString().trim().length > 0,
  subject: (formData.value.subject || '').toString().trim().length > 0
}))

const handleSave = () => {
  // 儲存題目基本資料
  // Final guard: trim and ensure content not empty
  if (!isFormValid.value) {
    alert('請填寫題目內容與科目後再儲存。')
    return
  }

  // Ensure tag_ids are taken from selectedTags
  formData.value.tag_ids = selectedTags.value.map(t => t.id)

  const payload = {
    ...formData.value,
    content: formData.value.content?.toString().trim()
  }

  emit('save', {
    questionData: payload,
    examSettings: props.examQuestion ? examSettings.value : null
  })
}

// Tag service and components
import tagService from '../services/tagService'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import { useDebounceFn } from '@vueuse/core'

// tagOptions 和 selectedTags 已在上方定義
const newTagName = ref('')
const tagSearchQuery = ref('')

// 用於在 tagOptions 載入完成後重新設定 selectedTags
const updateSelectedTagsFromIds = () => {
  if (props.question?.tag_ids && Array.isArray(props.question.tag_ids) && tagOptions.value.length > 0) {
    // 如果 selectedTags 還沒設定，根據 tag_ids 設定
    if (selectedTags.value.length === 0 && props.question.tag_ids.length > 0) {
      selectedTags.value = tagOptions.value.filter(t => props.question.tag_ids.includes(t.id))
    }
  }
}

onMounted(async () => {
  try {
    const res = await tagService.getTags()
    let items = res.data?.results || res.data
    if (!Array.isArray(items)) items = []
    tagOptions.value = items.filter(t => t != null)
    // tagOptions 載入完成後，重新設定 selectedTags
    updateSelectedTagsFromIds()
  } catch (err) {
    console.error('載入標籤失敗:', err)
  }
    tagSearchQuery.value = ''
})

const handleCreateTag = async () => {
  const name = newTagName.value?.trim()
  if (!name) return
  try {
    const resp = await tagService.createTag({ name })
    const createdTag = resp.data
    if (!createdTag || !createdTag.id) {
      throw new Error('Invalid tag returned')
    }
    // Add to local options if not exists
    if (!tagOptions.value.find(t => t.id === createdTag.id)) {
      tagOptions.value.push(createdTag)
      // sort by name
      tagOptions.value.sort((a, b) => a.name.localeCompare(b.name))
    }
    // Add to selectedTags (object) and keep formData.tag_ids in sync
    if (!selectedTags.value.find(t => t.id === createdTag.id)) {
      selectedTags.value.push(createdTag)
    }
    formData.value.tag_ids = selectedTags.value.map(t => t.id)
    newTagName.value = ''
  } catch (err) {
    console.error('建立標籤失敗:', err)
    alert('建立標籤失敗')
  }
}

// Debounced search for tags
const doTagSearch = useDebounceFn(async (query) => {
  try {
    const res = await tagService.getTags({ search: query })
    let items = res.data?.results || res.data
    if (!Array.isArray(items)) items = []
    tagOptions.value = items.filter(t => t != null)
  } catch (err) {
    console.error('搜尋標籤失敗: ', err)
  }
}, 250)

const onTagSearch = (query) => {
  tagSearchQuery.value = query
  doTagSearch(query)
}
</script>

<style scoped>
.question-editor {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: #999;
}

.editor-content {
  flex: 1;
  padding: 20px;
  height: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #eee;
}

.editor-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 85%;
  overflow: scroll;
}

form {
  display: flex;
  flex-direction: column;
  
  .form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    width: 100%;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
    font-size: 14px;
  }
  
  .form-input {
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.3s;
  }
  .form-input:focus {
    outline: none;
    border-color: #4CAF50;
  }
}

textarea.form-input {
  resize: vertical;
  font-family: inherit;
}

select.form-input {
  cursor: pointer;
}

.options-list {
  margin-bottom: 12px;
}

.option-item {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.option-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.option-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.btn-remove {
  width: 28px;
  height: 28px;
  border: none;
  background: #f44336;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-remove:hover {
  background: #d32f2f;
}

.exam-settings {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid #eee;
}

.exam-settings h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}
</style>

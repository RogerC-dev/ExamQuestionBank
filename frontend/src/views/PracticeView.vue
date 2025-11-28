<template>
  <div class="practice-view">
    <div class="container">
      <!-- Filter Section -->
      <div class="filter-section">
        <div class="filter-row">
          <div class="filter-group">
            <label>考試別</label>
            <select v-model="filters.examSeries">
              <option value="">全部</option>
              <option value="judicial">司法官</option>
              <option value="lawyer">律師</option>
            </select>
          </div>
          <div class="filter-group">
            <label>年度</label>
            <select v-model="filters.year">
              <option value="">全部</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
            </select>
          </div>
          <div class="filter-group">
            <label>科目</label>
            <select v-model="filters.subject">
              <option value="">全部</option>
              <option value="civil">民法</option>
              <option value="criminal">刑法</option>
              <option value="administrative">行政法</option>
            </select>
          </div>
          <div class="filter-group">
            <label>難度</label>
            <select v-model="filters.difficulty">
              <option value="">全部</option>
              <option value="easy">簡單</option>
              <option value="medium">中等</option>
              <option value="hard">困難</option>
            </select>
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-group" style="grid-column: 1 / -1;">
            <label>關鍵字搜尋</label>
            <input v-model="filters.keyword" type="text" placeholder="輸入關鍵字...">
          </div>
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary" @click="applyFilters">套用篩選</button>
          <button class="btn btn-secondary" @click="resetFilters">重置</button>
        </div>
      </div>

      <!-- Practice Modes -->
      <h2 class="section-title">選擇練習模式</h2>
      <div class="practice-modes">
        <div
          v-for="mode in practiceModes"
          :key="mode.key"
          class="mode-card"
        >
          <div class="mode-icon">{{ mode.icon }}</div>
          <div class="mode-title">{{ mode.title }}</div>
          <div class="mode-desc">{{ mode.description }}</div>
          <button
            class="btn-mode"
            :disabled="isLoading && selectedMode === mode.key"
            @click="startPractice(mode.key)"
          >
            <span v-if="isLoading && selectedMode === mode.key">載入中...</span>
            <span v-else>{{ mode.cta }}</span>
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Statistics -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_bank.toLocaleString() }}</div>
          <div class="stat-label">題庫數</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_answered.toLocaleString() }}</div>
          <div class="stat-label">已練習</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.accuracy }}%</div>
          <div class="stat-label">正確率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.exam_count }}</div>
          <div class="stat-label">測驗次數</div>
        </div>
      </div>

      <!-- Historical Exams Section -->
      <section class="historical-exams">
        <div class="section-header">
          <h3>歷屆考卷</h3>
          <button class="btn btn-primary" @click="router.push('/admin/exams')">前往管理</button>
        </div>
        <div v-if="loadingExams" class="table-status">載入中...</div>
        <div v-else-if="!historicalExams.length" class="table-status">目前尚無考卷</div>
        <table v-else>
          <thead>
            <tr>
              <th>名稱</th>
              <th>題數</th>
              <th>時間限制</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exam in historicalExams" :key="exam.id">
              <td>{{ exam.name }}</td>
              <td>{{ exam.question_count }}</td>
              <td>{{ exam.time_limit || '-' }}</td>
              <td><button class="btn btn-secondary" @click="viewExam(exam.id)">查看</button></td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>

  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionBankStore } from '@/stores/questionBank'
import questionService from '@/services/questionService'
import examService from '@/services/examService'
import mockExamService from '@/services/mockExamService'

const router = useRouter()
const questionBankStore = useQuestionBankStore()

const filters = reactive({
  examSeries: '',
  year: '',
  subject: '',
  difficulty: '',
  keyword: ''
})

const isLoading = ref(false)
const selectedMode = ref(null)
const errorMessage = ref('')
const stats = reactive({
  total_bank: 0,
  total_answered: 0,
  accuracy: 0,
  exam_count: 0
})

const practiceModes = [
  { key: 'historical', icon: '📚', title: '歷屆考題', description: '按年度練習歷屆考題', cta: '開始練習' },
  { key: 'simulation', icon: '📝', title: '模擬考試', description: '模擬真實考試情境', cta: '開始測驗' },
  { key: 'mixed', icon: '🔀', title: '混合練習', description: '隨機混合不同年度題目', cta: '隨機練習' },
  { key: 'bookmarked', icon: '⭐', title: '收藏題庫', description: '複習已收藏的題目', cta: '快速收藏' }
]

const filtersChanged = computed(() => {
  return Object.values(filters).some(value => value !== '')
})

const applyFilters = () => {
  console.log('Applying filters:', filters)
  alert('✅ 篩選已套用')
}

const resetFilters = () => {
  filters.examSeries = ''
  filters.year = ''
  filters.subject = ''
  filters.difficulty = ''
  filters.keyword = ''
  alert('🔄 篩選已重置')
}

const startPractice = async (mode) => {
  if (isLoading.value) return
  selectedMode.value = mode
  isLoading.value = true
  errorMessage.value = ''

  try {
    switch (mode) {
      case 'historical': {
        // Persist filters back to Pinia so downstream views stay in sync
        Object.entries(filters).forEach(([key, value]) => {
          questionBankStore.setFilter(key, value || null)
        })
        await questionBankStore.fetchQuestions(1)
        router.push({ name: 'Practice', query: { mode: 'historical' } })
        break
      }
      case 'simulation': {
        const payload = buildMockExamPayload()
        const { data } = await mockExamService.generateMockExam(payload)
        router.push({ name: 'MockExams', query: { focus: data.id } })
        break
      }
      case 'mixed': {
        const response = await questionService.getQuestions({ ...buildQuestionParams(), order: 'random' })
        questionBankStore.questions = response.data.results || response.data
        router.push({ name: 'Practice', query: { mode: 'mixed' } })
        break
      }
      case 'bookmarked': {
        const response = await questionService.getBookmarkedQuestions()
        questionBankStore.questions = response.data.results || response.data
        router.push({ name: 'Practice', query: { mode: 'bookmarked' } })
        break
      }
      default:
        throw new Error('unknown-mode')
    }
  } catch (error) {
    if (error.response?.status === 401) {
      window.dispatchEvent(new Event('show-login'))
      errorMessage.value = '請先登入後再進行練習'
    } else {
      errorMessage.value = error.response?.data?.message || '啟動練習時發生錯誤，請稍後再試。'
    }
    console.error('Failed to start practice:', error)
  } finally {
    isLoading.value = false
    selectedMode.value = null
  }
}

const buildQuestionParams = () => ({
  exam_series: filters.examSeries || undefined,
  year: filters.year || undefined,
  subject: filters.subject || undefined,
  difficulty: filters.difficulty || undefined,
  keyword: filters.keyword || undefined,
})

const mockQuestionCount = computed(() => Number(filters.keyword) || 20)

const buildMockExamPayload = () => ({
  subject_id: filters.subject || undefined,
  question_count: mockQuestionCount.value,
  difficulty: filters.difficulty || 'medium',
  reuse_question_bank: true
})

const historicalExams = ref([])
const loadingExams = ref(false)

const loadHistoricalExams = async () => {
  loadingExams.value = true
  try {
    const { data } = await examService.getExams({ ordering: '-created_at', page_size: 5 })
    historicalExams.value = Array.isArray(data) ? data : data.results ?? []
  } catch (error) {
    console.error('Failed to load exams', error)
  } finally {
    loadingExams.value = false
  }
}

const viewExam = (examId) => {
  router.push({ name: 'ExamPreview', params: { id: examId } })
}

const loadStats = async () => {
  try {
    const { data } = await examService.getExamStats()
    Object.assign(stats, data)
  } catch (error) {
    console.error('Failed to load stats', error)
  }
}

onMounted(() => {
  loadHistoricalExams()
  loadStats()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.filter-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.filter-row:last-of-type {
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  color: #555;
  margin-bottom: 8px;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  transition: border-color 0.3s;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #007bff;
}

.filter-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 24px;
}

.practice-modes {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.mode-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.mode-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.mode-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.mode-title {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
}

.mode-desc {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 20px;
}

.btn-mode {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-mode:hover {
  background: #0056b3;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px;
  border-radius: 12px;
  text-align: center;
  color: white;
}

.stat-card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card:nth-child(4) {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-value {
  font-size: 42px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.95;
}

.alert {
  margin: 0 0 24px;
  padding: 12px 16px;
  border-radius: 6px;
}

.alert-error {
  background: #fdecea;
  border: 1px solid #f5c2c0;
  color: #b42318;
}

.table-status {
  text-align: center;
  padding: 20px;
  color: #666;
}

.historical-exams {
  margin-top: 40px;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background: #f9f9f9;
  color: #333;
  font-weight: 500;
}

tr:hover {
  background: #f1f1f1;
}

@media (max-width: 768px) {
  .filter-row,
  .practice-modes,
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>

<template>
  <div class="analytics-view">
    <div class="container">
      <div class="analytics-header">
        <h2><i class="bi bi-graph-up-arrow"></i> 學習追蹤分析</h2>
        <p class="header-subtitle">追蹤您的學習進度與表現</p>
      </div>

      <div v-if="loading" class="loading">載入中...</div>

      <template v-else>
        <!-- Analytics Overview Cards -->
        <div class="overview-cards">
          <div class="overview-card">
            <div class="overview-icon blue"><i class="bi bi-clipboard-check"></i></div>
            <div class="overview-content">
              <span class="overview-value">{{ stats.total_answered || 0 }}</span>
              <span class="overview-label">已作答題數</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="overview-icon green"><i class="bi bi-bullseye"></i></div>
            <div class="overview-content">
              <span class="overview-value">{{ stats.accuracy || 0 }}%</span>
              <span class="overview-label">整體正確率</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="overview-icon purple"><i class="bi bi-journal-text"></i></div>
            <div class="overview-content">
              <span class="overview-value">{{ stats.exam_count || 0 }}</span>
              <span class="overview-label">測驗次數</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="overview-icon amber"><i class="bi bi-x-circle"></i></div>
            <div class="overview-content">
              <span class="overview-value">{{ stats.wrong_count || 0 }}</span>
              <span class="overview-label">錯題數量</span>
            </div>
          </div>
        </div>

        <!-- Accuracy Trend Card - List View -->
        <div class="analytics-card trend-card">
          <div class="card-header">
            <div class="card-title-row">
              <h3><i class="bi bi-bar-chart-line"></i> 正確率趨勢</h3>
            </div>
            <div class="card-controls">
              <!-- Search/Filter -->
              <div class="search-filter">
                <i class="bi bi-search"></i>
                <input 
                  type="text" 
                  v-model="trendSearch" 
                  placeholder="搜尋考卷名稱、年度 (如 114、113)..."
                  class="search-input"
                >
              </div>
              <!-- Sort Options -->
              <div class="sort-control">
                <label>排序：</label>
                <select v-model="trendSort">
                  <option value="date-desc">最新優先</option>
                  <option value="date-asc">最舊優先</option>
                  <option value="accuracy-desc">正確率高→低</option>
                  <option value="accuracy-asc">正確率低→高</option>
                  <option value="delta-desc">進步幅度大→小</option>
                </select>
              </div>
            </div>
          </div>
          
          <div v-if="displayedTrend.length" class="trend-list">
            <div class="trend-list-header">
              <span class="col-name">考卷名稱</span>
              <span class="col-accuracy">正確率</span>
              <span class="col-delta">與前次比較</span>
              <span class="col-date">測驗日期</span>
              <span class="col-action">操作</span>
            </div>
            <div
              v-for="(item, index) in displayedTrend"
              :key="item.key"
              class="trend-item"
              :class="{'glow-pulse': glowTarget === item.key}"
            >
              <div class="col-name">
                <span class="trend-rank">{{ (trendPage - 1) * trendPageSize + index + 1 }}</span>
                <div class="trend-info">
                  <span class="trend-title">{{ item.exam_name || '未命名考卷' }}</span>
                  <span class="trend-subject" v-if="item.subject">{{ item.subject }}</span>
                </div>
              </div>
              <div class="col-accuracy">
                <div class="accuracy-bar-container">
                  <div class="accuracy-bar" :style="{ width: item.accuracy + '%' }" :class="getAccuracyClass(item.accuracy)"></div>
                </div>
                <span class="accuracy-value" :class="getAccuracyClass(item.accuracy)">{{ item.accuracy }}%</span>
              </div>
              <div class="col-delta">
                <span v-if="item.delta !== null" :class="['delta-badge', {up: item.delta > 0, down: item.delta < 0, neutral: item.delta === 0}]">
                  <i :class="item.delta > 0 ? 'bi bi-arrow-up' : item.delta < 0 ? 'bi bi-arrow-down' : 'bi bi-dash'"></i>
                  {{ item.delta > 0 ? '+' : '' }}{{ item.delta }}%
                </span>
                <span v-else class="delta-badge new">首次</span>
              </div>
              <div class="col-date">{{ formatDate(item.date) }}</div>
              <div class="col-action">
                <button class="btn-action" @click="drillToPractice(item)" title="前往練習">
                  <i class="bi bi-arrow-right-circle"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">
            <i class="bi bi-inbox"></i>
            <p>{{ trendSearch ? '找不到符合的測驗記錄' : '尚無測驗記錄' }}</p>
          </div>
          
          <!-- Pagination for trend -->
          <div v-if="filteredTrend.length > trendPageSize" class="pagination-controls">
            <span class="pagination-info">共 {{ filteredTrend.length }} 筆記錄</span>
            <div class="pagination-buttons">
              <button class="btn-page" :disabled="trendPage === 1" @click="trendPage = 1" title="第一頁">
                <i class="bi bi-chevron-double-left"></i>
              </button>
              <button class="btn-page" :disabled="trendPage === 1" @click="trendPage--">
                <i class="bi bi-chevron-left"></i>
              </button>
              <span class="page-info">{{ trendPage }} / {{ trendTotalPages }}</span>
              <button class="btn-page" :disabled="trendPage >= trendTotalPages" @click="trendPage++">
                <i class="bi bi-chevron-right"></i>
              </button>
              <button class="btn-page" :disabled="trendPage >= trendTotalPages" @click="trendPage = trendTotalPages" title="最後一頁">
                <i class="bi bi-chevron-double-right"></i>
              </button>
            </div>
            <select v-model="trendPageSize" class="page-size-select">
              <option :value="5">5 筆/頁</option>
              <option :value="10">10 筆/頁</option>
              <option :value="20">20 筆/頁</option>
              <option :value="50">50 筆/頁</option>
            </select>
          </div>
        </div>

        <div class="analytics-grid">
          <!-- Top Wrong Items Card with Pagination -->
          <div class="analytics-card wrong-card">
            <div class="card-header">
              <div class="card-title-row">
                <h3><i class="bi bi-exclamation-triangle"></i> 常錯考卷 / 題目</h3>
              </div>
              <div class="card-controls">
                <div class="search-filter small">
                  <i class="bi bi-search"></i>
                  <input 
                    type="text" 
                    v-model="wrongSearch" 
                    placeholder="搜尋..."
                    class="search-input"
                  >
                </div>
                <div class="sort-control">
                  <select v-model="wrongSort">
                    <option value="count-desc">錯誤次數多→少</option>
                    <option value="count-asc">錯誤次數少→多</option>
                    <option value="name-asc">名稱 A-Z</option>
                  </select>
                </div>
              </div>
            </div>
            <div v-if="displayedWrong.length" class="hot-list">
              <div
                v-for="(item, index) in displayedWrong"
                :key="item.key"
                class="hot-item"
                :class="{'glow-pulse': glowTarget === item.key}"
                @click="drillToPractice(item)"
              >
                <div class="hot-left">
                  <div class="hot-rank">{{ (wrongPage - 1) * wrongPageSize + index + 1 }}</div>
                  <div class="hot-info">
                    <div class="hot-title">{{ item.label }}</div>
                    <div class="hot-tag">{{ item.tag }}</div>
                  </div>
                </div>
                <div class="hot-count">
                  <i class="bi bi-x-lg"></i> {{ item.count }} 次
                </div>
              </div>
            </div>
            <div v-else class="empty-results">
              <i class="bi bi-emoji-smile"></i>
              <p>{{ wrongSearch ? '找不到符合的錯題' : '目前沒有常錯統計' }}</p>
            </div>
            
            <!-- Pagination for wrong items -->
            <div v-if="filteredWrong.length > wrongPageSize" class="pagination-controls compact">
              <span class="pagination-info">共 {{ filteredWrong.length }} 筆</span>
              <div class="pagination-buttons">
                <button class="btn-page" :disabled="wrongPage === 1" @click="wrongPage--">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <span class="page-info">{{ wrongPage }} / {{ wrongTotalPages }}</span>
                <button class="btn-page" :disabled="wrongPage >= wrongTotalPages" @click="wrongPage++">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Recent Results Card with Tabs -->
          <div class="analytics-card results-card">
            <div class="card-header">
              <div class="card-title-row">
                <h3><i class="bi bi-clock-history"></i> 最近測驗記錄</h3>
              </div>
              <div class="results-tabs">
                <button :class="{ active: resultsTab === 'all' }" @click="resultsTab = 'all'">全部</button>
                <button :class="{ active: resultsTab === 'passed' }" @click="resultsTab = 'passed'">及格</button>
                <button :class="{ active: resultsTab === 'failed' }" @click="resultsTab = 'failed'">待加強</button>
              </div>
            </div>
            <div v-if="paginatedResults.length > 0" class="results-list">
              <div v-for="result in paginatedResults" :key="result.id" class="result-item">
                <div class="result-left">
                  <div class="result-icon" :class="result.score >= 60 ? 'pass' : 'fail'">
                    <i :class="result.score >= 60 ? 'bi bi-check-lg' : 'bi bi-x-lg'"></i>
                  </div>
                  <div class="result-info">
                    <span class="result-name">{{ result.exam_name }}</span>
                    <span class="result-date">{{ formatDate(result.completed_at) }}</span>
                  </div>
                </div>
                <div class="result-score" :class="result.score >= 60 ? 'pass' : 'fail'">
                  <span class="score-value">{{ result.score }}</span>
                  <span class="score-label">分</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-results"><i class="bi bi-journal-x"></i><p>尚無測驗記錄</p></div>
            
            <!-- Pagination for results -->
            <div v-if="filteredResults.length > resultsPageSize" class="pagination-controls compact">
              <span class="pagination-info">共 {{ filteredResults.length }} 筆</span>
              <div class="pagination-buttons">
                <button class="btn-page" :disabled="resultsPage === 1" @click="resultsPage--">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <span class="page-info">{{ resultsPage }} / {{ resultsTotalPages }}</span>
                <button class="btn-page" :disabled="resultsPage >= resultsTotalPages" @click="resultsPage++">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button class="btn btn-primary" @click="$router.push('/practice')">
            <i class="bi bi-play-fill"></i> 前往練習
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import examService from '@/services/examService'

const loading = ref(true)
const stats = ref({
  total_answered: 0, correct_answered: 0, total_bank: 0, exam_count: 0,
  average_score: 0, accuracy: 0, accuracy_trend: [], top_wrong: [], wrong_count: 0
})
const recentResults = ref([])
const glowTarget = ref(null)
const router = useRouter()

// Trend state
const trendPage = ref(1)
const trendPageSize = ref(10)
const trendSearch = ref('')
const trendSort = ref('date-desc')

// Wrong items state
const wrongPage = ref(1)
const wrongPageSize = 10
const wrongSearch = ref('')
const wrongSort = ref('count-desc')

// Results state
const resultsPage = ref(1)
const resultsPageSize = 5
const resultsTab = ref('all')

// Process trend data
const processedTrend = computed(() => {
  const trend = stats.value.accuracy_trend || []
  const map = new Map()
  trend.forEach((entry) => {
    const key = entry.exam_id || entry.exam_name || entry.id || entry.index
    if (!map.has(key)) {
      map.set(key, { ...entry, key, previous: null })
    } else {
      const current = map.get(key)
      if (current.previous === null) current.previous = current.accuracy
      current.accuracy = entry.accuracy
      current.date = entry.date || entry.completed_at || current.date
      map.set(key, current)
    }
  })
  return Array.from(map.values()).map(item => ({
    ...item,
    delta: item.previous === null ? null : Math.round((item.accuracy - item.previous) * 10) / 10
  }))
})

// Filter and sort trend
const filteredTrend = computed(() => {
  let items = [...processedTrend.value]
  
  // Search filter
  if (trendSearch.value.trim()) {
    const search = trendSearch.value.toLowerCase()
    items = items.filter(item => {
      const name = (item.exam_name || '').toLowerCase()
      const subject = (item.subject || '').toLowerCase()
      return name.includes(search) || subject.includes(search)
    })
  }
  
  // Sort
  switch (trendSort.value) {
    case 'date-asc':
      items.sort((a, b) => new Date(a.date || 0) - new Date(b.date || 0))
      break
    case 'accuracy-desc':
      items.sort((a, b) => b.accuracy - a.accuracy)
      break
    case 'accuracy-asc':
      items.sort((a, b) => a.accuracy - b.accuracy)
      break
    case 'delta-desc':
      items.sort((a, b) => (b.delta || 0) - (a.delta || 0))
      break
    default: // date-desc
      items.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
  }
  
  return items
})

const trendTotalPages = computed(() => Math.ceil(filteredTrend.value.length / trendPageSize.value) || 1)
const displayedTrend = computed(() => {
  const start = (trendPage.value - 1) * trendPageSize.value
  return filteredTrend.value.slice(start, start + trendPageSize.value)
})

// Reset page when filter/sort/pageSize changes
watch([trendSearch, trendSort, trendPageSize], () => { trendPage.value = 1 })

// Process wrong items
const allWrongItems = computed(() => {
  const list = stats.value.top_wrong || []
  return list.map((item, idx) => ({
    key: item.exam_id || item.question_id || idx,
    exam_id: item.exam_id,
    question_id: item.question_id,
    label: item.exam_name || item.question_content || '未命名',
    tag: item.question_subject || '考卷',
    count: item.wrong_count ?? item.count ?? 0
  }))
})

// Filter and sort wrong items
const filteredWrong = computed(() => {
  let items = [...allWrongItems.value]
  
  // Search filter
  if (wrongSearch.value.trim()) {
    const search = wrongSearch.value.toLowerCase()
    items = items.filter(item => {
      return item.label.toLowerCase().includes(search) || item.tag.toLowerCase().includes(search)
    })
  }
  
  // Sort
  switch (wrongSort.value) {
    case 'count-asc':
      items.sort((a, b) => a.count - b.count)
      break
    case 'name-asc':
      items.sort((a, b) => a.label.localeCompare(b.label, 'zh-TW'))
      break
    default: // count-desc
      items.sort((a, b) => b.count - a.count)
  }
  
  return items
})

const wrongTotalPages = computed(() => Math.ceil(filteredWrong.value.length / wrongPageSize) || 1)
const displayedWrong = computed(() => {
  const start = (wrongPage.value - 1) * wrongPageSize
  return filteredWrong.value.slice(start, start + wrongPageSize)
})

watch([wrongSearch, wrongSort], () => { wrongPage.value = 1 })

// Filtered and paginated results
const filteredResults = computed(() => {
  if (resultsTab.value === 'passed') return recentResults.value.filter(r => r.score >= 60)
  if (resultsTab.value === 'failed') return recentResults.value.filter(r => r.score < 60)
  return recentResults.value
})

const resultsTotalPages = computed(() => Math.ceil(filteredResults.value.length / resultsPageSize) || 1)
const paginatedResults = computed(() => {
  const start = (resultsPage.value - 1) * resultsPageSize
  return filteredResults.value.slice(start, start + resultsPageSize)
})

watch(resultsTab, () => { resultsPage.value = 1 })

// Helper for backwards compat
const topWrongItems = computed(() => displayedWrong.value)

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

const getAccuracyClass = (accuracy) => {
  if (accuracy >= 80) return 'high'
  if (accuracy >= 60) return 'medium'
  return 'low'
}

const loadData = async () => {
  loading.value = true
  try {
    const [statsRes, resultsRes] = await Promise.all([
      examService.getExamStats(),
      examService.getExamResults()
    ])
    stats.value = statsRes.data
    recentResults.value = resultsRes.data || []
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}

const triggerGlow = (key) => {
  glowTarget.value = key
  setTimeout(() => { if (glowTarget.value === key) glowTarget.value = null }, 900)
}

const drillToPractice = (item) => {
  triggerGlow(item.key)
  if (item.exam_id) {
    router.push({ name: 'ExamPreview', params: { id: item.exam_id } })
    return
  }
  router.push({ path: '/practice', query: { focus: item.question_id || item.key } })
}

onMounted(loadData)
</script>

<style scoped>
.analytics-view {
  min-height: calc(100vh - 140px);
  background: var(--bg-soft, #f8fafc);
  padding: 24px 0;
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

.analytics-header { text-align: center; margin-bottom: 32px; }
.analytics-header h2 { 
  font-size: 26px; font-weight: 800; color: var(--text-primary); 
  display: flex; align-items: center; justify-content: center; gap: 10px;
}
.analytics-header h2 i { color: var(--primary); }
.header-subtitle { color: var(--text-secondary); margin-top: 6px; font-size: 14px; }

.loading { text-align: center; padding: 60px; color: #666; }

/* Overview Cards */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.overview-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(0,0,0,0.04);
}
.overview-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: grid; place-items: center; font-size: 20px;
}
.overview-icon.blue { background: #eff6ff; color: #2563eb; }
.overview-icon.green { background: #ecfdf5; color: #059669; }
.overview-icon.purple { background: #f5f3ff; color: #7c3aed; }
.overview-icon.amber { background: #fffbeb; color: #d97706; }
.overview-content { display: flex; flex-direction: column; }
.overview-value { font-size: 24px; font-weight: 800; color: var(--text-primary); }
.overview-label { font-size: 13px; color: var(--text-secondary); }

/* Analytics Card Base */
.analytics-card {
  background: #fff;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
}

.card-header { margin-bottom: 16px; }
.card-title-row { 
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.card-header h3 { 
  font-size: 17px; font-weight: 700; color: var(--text-primary);
  display: flex; align-items: center; gap: 8px; margin: 0;
}
.card-header h3 i { color: var(--primary); font-size: 18px; }

/* Card Controls */
.card-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.search-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  flex: 1;
  min-width: 200px;
}
.search-filter.small { min-width: 120px; flex: 0; }
.search-filter i { color: #94a3b8; font-size: 14px; }
.search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 13px;
  width: 100%;
  color: var(--text-primary);
}
.search-input::placeholder { color: #94a3b8; }

.sort-control {
  display: flex;
  align-items: center;
  gap: 6px;
}
.sort-control label { font-size: 13px; color: var(--text-secondary); white-space: nowrap; }
.sort-control select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  background: #fff;
  cursor: pointer;
  color: var(--text-primary);
}

/* Trend List View */
.trend-list { margin-top: 12px; }
.trend-list-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 60px;
  gap: 12px;
  padding: 10px 16px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.trend-item {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 60px;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid #e6e8ed;
  border-radius: 10px;
  margin-bottom: 8px;
  align-items: center;
  transition: all 0.2s;
  background: #fff;
}
.trend-item:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.1);
}
.col-name { display: flex; align-items: center; gap: 12px; }
.trend-rank {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #2563eb; font-weight: 700; font-size: 12px;
  display: grid; place-items: center; flex-shrink: 0;
}
.trend-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.trend-title { 
  font-weight: 600; color: var(--text-primary); font-size: 14px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.trend-subject { font-size: 12px; color: var(--text-secondary); }

.col-accuracy { display: flex; align-items: center; gap: 10px; }
.accuracy-bar-container {
  flex: 1; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden;
}
.accuracy-bar { height: 100%; border-radius: 4px; transition: width 0.3s; }
.accuracy-bar.high { background: linear-gradient(90deg, #22c55e, #16a34a); }
.accuracy-bar.medium { background: linear-gradient(90deg, #eab308, #ca8a04); }
.accuracy-bar.low { background: linear-gradient(90deg, #ef4444, #dc2626); }
.accuracy-value { font-weight: 700; font-size: 14px; min-width: 45px; }
.accuracy-value.high { color: #16a34a; }
.accuracy-value.medium { color: #ca8a04; }
.accuracy-value.low { color: #dc2626; }

.col-delta, .col-date, .col-action { text-align: center; }
.col-date { font-size: 13px; color: var(--text-secondary); }

.delta-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;
}
.delta-badge.up { background: #ecfdf5; color: #059669; }
.delta-badge.down { background: #fef2f2; color: #dc2626; }
.delta-badge.neutral { background: #f3f4f6; color: #6b7280; }
.delta-badge.new { background: #eff6ff; color: #2563eb; }

.btn-action {
  width: 36px; height: 36px; border: 1px solid #e2e8f0;
  background: #fff; border-radius: 8px; cursor: pointer;
  display: grid; place-items: center; color: var(--primary);
  transition: all 0.2s;
}
.btn-action:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

.empty-chart, .empty-results { 
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 40px 20px; 
  color: var(--text-secondary); text-align: center;
}
.empty-chart i, .empty-results i { font-size: 36px; margin-bottom: 12px; opacity: 0.5; }

/* Pagination */
.pagination-controls {
  display: flex; justify-content: space-between; align-items: center;
  gap: 16px; margin-top: 20px; padding-top: 16px; border-top: 1px solid #e6e8ed;
  flex-wrap: wrap;
}
.pagination-controls.compact { justify-content: center; }
.pagination-info { font-size: 13px; color: var(--text-secondary); }
.pagination-buttons { display: flex; gap: 6px; align-items: center; }
.btn-page {
  width: 32px; height: 32px; border: 1px solid var(--border);
  background: #fff; border-radius: 8px; display: grid; place-items: center;
  cursor: pointer; transition: all 0.2s; color: var(--text-primary); font-size: 12px;
}
.btn-page:hover:not(:disabled) { background: var(--primary); color: #fff; border-color: var(--primary); }
.btn-page:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 13px; color: var(--text-secondary); min-width: 60px; text-align: center; }
.page-size-select {
  padding: 6px 10px; border: 1px solid #e2e8f0; border-radius: 6px;
  font-size: 12px; background: #fff; cursor: pointer;
}

/* Analytics Grid */
.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.analytics-grid .analytics-card { margin-bottom: 0; }

/* Hot List (Wrong Items) */
.hot-list { display: flex; flex-direction: column; gap: 8px; }
.hot-item { 
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 14px; border: 1px solid #e6e8ed; border-radius: 10px; 
  background: #fff; cursor: pointer; transition: all 0.2s;
}
.hot-item:hover { border-color: #fca5a5; background: #fef2f2; }
.hot-left { display: flex; align-items: center; gap: 12px; }
.hot-rank {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #dc2626; font-weight: 800; font-size: 12px;
  display: grid; place-items: center;
}
.hot-info { display: flex; flex-direction: column; gap: 2px; }
.hot-title { font-weight: 600; color: var(--text-primary); font-size: 13px; }
.hot-tag { font-size: 11px; color: var(--text-secondary); }
.hot-count { 
  font-weight: 700; color: #dc2626;
  display: flex; align-items: center; gap: 4px; font-size: 13px;
}

/* Results */
.results-tabs { display: flex; gap: 6px; }
.results-tabs button {
  padding: 6px 14px; border: 1px solid var(--border); background: #fff;
  border-radius: 20px; font-size: 12px; font-weight: 600;
  color: var(--text-secondary); cursor: pointer; transition: all 0.2s;
}
.results-tabs button:hover { background: #f8fafc; }
.results-tabs button.active { background: var(--primary); color: #fff; border-color: var(--primary); }

.results-list { display: flex; flex-direction: column; gap: 8px; }
.result-item { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 14px 16px; background: #fafbfc; border: 1px solid #e6e8ed;
  border-radius: 10px; transition: all 0.2s;
}
.result-left { display: flex; align-items: center; gap: 12px; }
.result-icon {
  width: 32px; height: 32px; border-radius: 50%;
  display: grid; place-items: center; font-size: 14px;
}
.result-icon.pass { background: #ecfdf5; color: #059669; }
.result-icon.fail { background: #fef2f2; color: #dc2626; }
.result-info { display: flex; flex-direction: column; gap: 2px; }
.result-name { font-weight: 600; color: var(--text-primary); font-size: 13px; }
.result-date { font-size: 11px; color: var(--text-secondary); }
.result-score { display: flex; align-items: baseline; gap: 2px; }
.score-value { font-size: 22px; font-weight: 800; }
.score-label { font-size: 12px; color: var(--text-secondary); }
.result-score.pass .score-value { color: #059669; }
.result-score.fail .score-value { color: #dc2626; }

/* Action Buttons */
.action-buttons { text-align: center; margin-top: 24px; }
.btn { 
  padding: 14px 32px; border: none; border-radius: 12px; 
  cursor: pointer; font-weight: 700; font-size: 15px;
  display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;
}
.btn-primary { 
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.25);
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(37, 99, 235, 0.35); }

/* Glow Animation */
.glow-pulse { position: relative; animation: glow 0.9s ease-out; }
@keyframes glow {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.35); }
  100% { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
}

/* Responsive */
@media (max-width: 1024px) {
  .overview-cards { grid-template-columns: repeat(2, 1fr); }
  .analytics-grid { grid-template-columns: 1fr; }
  .trend-list-header, .trend-item { 
    grid-template-columns: 2fr 1fr 1fr;
  }
  .trend-list-header .col-date, .trend-list-header .col-action,
  .trend-item .col-date, .trend-item .col-action { display: none; }
}

@media (max-width: 640px) {
  .overview-cards { grid-template-columns: 1fr 1fr; gap: 12px; }
  .overview-card { padding: 16px; gap: 12px; }
  .overview-icon { width: 40px; height: 40px; font-size: 18px; }
  .overview-value { font-size: 20px; }
  .analytics-card { padding: 16px; }
  .card-controls { flex-direction: column; align-items: stretch; }
  .search-filter { min-width: 100%; }
  .trend-list-header { display: none; }
  .trend-item { 
    grid-template-columns: 1fr auto;
    gap: 8px;
  }
  .trend-item .col-delta { display: none; }
  .pagination-controls { flex-direction: column; gap: 12px; }
}
</style>

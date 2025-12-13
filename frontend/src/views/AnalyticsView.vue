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

        <div class="analytics-grid">
          <!-- Accuracy Trend Card -->
          <div class="analytics-card trend-card">
            <div class="card-header">
              <div class="card-title-row">
                <h3><i class="bi bi-bar-chart-line"></i> 正確率趨勢</h3>
                <span class="card-badge">與前次比較</span>
              </div>
              <p class="card-subtitle">同一考卷重複測驗僅保留最新一次</p>
            </div>
            <div v-if="displayedTrend.length" class="trend-chart">
              <div class="trend-bars">
                <div
                  v-for="item in displayedTrend"
                  :key="item.key"
                  class="trend-bar-wrapper"
                  :class="{'glow-pulse': glowTarget === item.key}"
                  :title="trendTitle(item)"
                  @click="drillToPractice(item)"
                >
                  <div class="trend-bar" :style="{ height: Math.max(6, item.accuracy) + '%' }">
                    <span class="bar-value">{{ item.accuracy }}%</span>
                  </div>
                  <div class="trend-meta">
                    <span class="trend-name">{{ item.exam_name || '未命名考卷' }}</span>
                    <span v-if="item.delta !== null" :class="['delta-badge', {up: item.delta > 0, down: item.delta < 0, neutral: item.delta === 0}]">
                      <i :class="item.delta > 0 ? 'bi bi-arrow-up' : item.delta < 0 ? 'bi bi-arrow-down' : 'bi bi-dash'"></i>
                      {{ item.delta > 0 ? '+' : '' }}{{ item.delta }}%
                    </span>
                  </div>
                </div>
              </div>
              <!-- Pagination for trend -->
              <div v-if="processedTrend.length > trendPageSize" class="pagination-controls">
                <button class="btn-page" :disabled="trendPage === 1" @click="trendPage--">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <span class="page-info">{{ trendPage }} / {{ trendTotalPages }}</span>
                <button class="btn-page" :disabled="trendPage >= trendTotalPages" @click="trendPage++">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
            <div v-else class="empty-chart"><i class="bi bi-inbox"></i><p>尚無測驗記錄</p></div>
          </div>

          <!-- Top Wrong Items Card -->
          <div class="analytics-card wrong-card">
            <div class="card-header">
              <div class="card-title-row">
                <h3><i class="bi bi-exclamation-triangle"></i> 常錯考卷 / 題目</h3>
              </div>
              <p class="card-subtitle">點擊即可回到練習頁</p>
            </div>
            <div v-if="topWrongItems.length" class="hot-list">
              <div
                v-for="item in topWrongItems"
                :key="item.key"
                class="hot-item"
                :class="{'glow-pulse': glowTarget === item.key}"
                @click="drillToPractice(item)"
              >
                <div class="hot-left">
                  <div class="hot-rank">{{ topWrongItems.indexOf(item) + 1 }}</div>
                  <div class="hot-info">
                    <div class="hot-title">{{ item.label }}</div>
                    <div class="hot-tag">{{ item.tag }}</div>
                  </div>
                </div>
                <div class="hot-count">
                  <i class="bi bi-x-lg"></i> {{ item.count }}
                </div>
              </div>
            </div>
            <div v-else class="empty-results"><i class="bi bi-emoji-smile"></i><p>目前沒有常錯統計，先去練習幾回吧！</p></div>
          </div>
        </div>

        <!-- Recent Results Card with Tabs -->
        <div class="analytics-card results-card">
          <div class="card-header">
            <div class="card-title-row">
              <h3><i class="bi bi-clock-history"></i> 最近測驗記錄</h3>
              <div class="results-tabs">
                <button :class="{ active: resultsTab === 'all' }" @click="resultsTab = 'all'">全部</button>
                <button :class="{ active: resultsTab === 'passed' }" @click="resultsTab = 'passed'">及格</button>
                <button :class="{ active: resultsTab === 'failed' }" @click="resultsTab = 'failed'">待加強</button>
              </div>
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
          <div v-else class="empty-results"><i class="bi bi-journal-x"></i><p>尚無測驗記錄，前往練習開始吧！</p></div>
          
          <!-- Pagination for results -->
          <div v-if="filteredResults.length > resultsPageSize" class="pagination-controls">
            <button class="btn-page" :disabled="resultsPage === 1" @click="resultsPage--">
              <i class="bi bi-chevron-left"></i>
            </button>
            <span class="page-info">{{ resultsPage }} / {{ resultsTotalPages }}</span>
            <button class="btn-page" :disabled="resultsPage >= resultsTotalPages" @click="resultsPage++">
              <i class="bi bi-chevron-right"></i>
            </button>
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

// Pagination state
const trendPage = ref(1)
const trendPageSize = 6
const resultsPage = ref(1)
const resultsPageSize = 5
const resultsTab = ref('all')

// Computed: processed trend data
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
      map.set(key, current)
    }
  })
  return Array.from(map.values()).map(item => ({
    ...item,
    delta: item.previous === null ? null : Math.round((item.accuracy - item.previous) * 10) / 10
  }))
})

const trendTotalPages = computed(() => Math.ceil(processedTrend.value.length / trendPageSize) || 1)
const displayedTrend = computed(() => {
  const start = (trendPage.value - 1) * trendPageSize
  return processedTrend.value.slice(start, start + trendPageSize)
})

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

// Reset results page when tab changes
watch(resultsTab, () => { resultsPage.value = 1 })

const topWrongItems = computed(() => {
  const list = stats.value.top_wrong || []
  return list.slice(0, 5).map((item, idx) => ({
    key: item.exam_id || item.question_id || idx,
    exam_id: item.exam_id,
    question_id: item.question_id,
    label: item.exam_name || item.question_content || '未命名',
    tag: item.question_subject || '考卷',
    count: item.wrong_count ?? item.count ?? 0
  }))
})

const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('zh-TW')

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

const trendTitle = (item) => {
  if (item.delta === null) return `${item.exam_name || '考卷'}：${item.accuracy}%`
  return `${item.exam_name || '考卷'}：${item.accuracy}%（${item.delta > 0 ? '提升' : '下降'} ${Math.abs(item.delta)}%）`
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

.analytics-header { 
  text-align: center; 
  margin-bottom: 32px; 
}
.analytics-header h2 { 
  font-size: 26px; 
  font-weight: 800; 
  color: var(--text-primary); 
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
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
  transition: transform 0.2s, box-shadow 0.2s;
}
.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.1);
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 20px;
}
.overview-icon.blue { background: #eff6ff; color: #2563eb; }
.overview-icon.green { background: #ecfdf5; color: #059669; }
.overview-icon.purple { background: #f5f3ff; color: #7c3aed; }
.overview-icon.amber { background: #fffbeb; color: #d97706; }

.overview-content { display: flex; flex-direction: column; }
.overview-value { font-size: 24px; font-weight: 800; color: var(--text-primary); }
.overview-label { font-size: 13px; color: var(--text-secondary); }

/* Analytics Grid */
.analytics-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.analytics-card {
  background: #fff;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.card-header { margin-bottom: 20px; }
.card-title-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.card-header h3 { 
  font-size: 17px; 
  font-weight: 700; 
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.card-header h3 i { color: var(--primary); font-size: 18px; }
.card-subtitle { margin: 8px 0 0; color: var(--text-secondary); font-size: 13px; }
.card-badge {
  background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

/* Trend Chart */
.trend-chart { min-height: 180px; }
.trend-bars { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); 
  gap: 12px; 
}
.trend-bar-wrapper { 
  padding: 14px; 
  border: 1px solid #e6e8ed; 
  border-radius: 12px; 
  background: linear-gradient(180deg, #fafbfc 0%, #fff 100%);
  cursor: pointer; 
  transition: all 0.2s ease;
}
.trend-bar-wrapper:hover { 
  border-color: var(--primary);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}
.trend-bar { 
  width: 100%; 
  min-height: 80px;
  max-height: 120px;
  border-radius: 8px; 
  background: linear-gradient(180deg, #3b82f6 0%, #93c5fd 100%);
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 8px;
}
.bar-value {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.trend-meta { margin-top: 12px; }
.trend-name { 
  font-size: 13px; 
  color: var(--text-primary); 
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}
.delta-badge.up { background: #ecfdf5; color: #059669; }
.delta-badge.down { background: #fef2f2; color: #dc2626; }
.delta-badge.neutral { background: #f3f4f6; color: #6b7280; }

.empty-chart, .empty-results { 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px; 
  color: var(--text-secondary);
  text-align: center;
}
.empty-chart i, .empty-results i {
  font-size: 36px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* Hot List (Wrong Items) */
.hot-list { display: flex; flex-direction: column; gap: 10px; }
.hot-item { 
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px; 
  border: 1px solid #e6e8ed; 
  border-radius: 12px; 
  background: #fdfefe; 
  cursor: pointer; 
  transition: all 0.2s;
}
.hot-item:hover { 
  border-color: #fca5a5;
  background: #fef2f2;
}
.hot-left { display: flex; align-items: center; gap: 12px; }
.hot-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #dc2626;
  font-weight: 800;
  font-size: 13px;
  display: grid;
  place-items: center;
}
.hot-info { display: flex; flex-direction: column; gap: 2px; }
.hot-title { font-weight: 600; color: var(--text-primary); font-size: 14px; }
.hot-tag { font-size: 12px; color: var(--text-secondary); }
.hot-count { 
  font-weight: 700; 
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

/* Results Card */
.results-card { margin-bottom: 20px; }
.results-tabs {
  display: flex;
  gap: 6px;
}
.results-tabs button {
  padding: 6px 14px;
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.results-tabs button:hover { background: #f8fafc; }
.results-tabs button.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.results-list { display: flex; flex-direction: column; gap: 10px; }
.result-item { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 16px 18px; 
  background: linear-gradient(135deg, #fafbfc, #fff);
  border: 1px solid #e6e8ed;
  border-radius: 12px;
  transition: all 0.2s;
}
.result-item:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08);
}
.result-left { display: flex; align-items: center; gap: 14px; }
.result-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 16px;
}
.result-icon.pass { background: #ecfdf5; color: #059669; }
.result-icon.fail { background: #fef2f2; color: #dc2626; }
.result-info { display: flex; flex-direction: column; gap: 2px; }
.result-name { font-weight: 600; color: var(--text-primary); font-size: 14px; }
.result-date { font-size: 12px; color: var(--text-secondary); }
.result-score { display: flex; align-items: baseline; gap: 2px; }
.score-value { font-size: 26px; font-weight: 800; }
.score-label { font-size: 13px; color: var(--text-secondary); }
.result-score.pass .score-value { color: #059669; }
.result-score.fail .score-value { color: #dc2626; }

/* Pagination */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e6e8ed;
}
.btn-page {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 10px;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}
.btn-page:hover:not(:disabled) { 
  background: var(--primary); 
  color: #fff;
  border-color: var(--primary);
}
.btn-page:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 13px; color: var(--text-secondary); min-width: 60px; text-align: center; }

/* Action Buttons */
.action-buttons { text-align: center; margin-top: 8px; }
.btn { 
  padding: 14px 32px; 
  border: none; 
  border-radius: 12px; 
  cursor: pointer; 
  font-weight: 700; 
  font-size: 15px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-primary { 
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.25);
}
.btn-primary:hover { 
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(37, 99, 235, 0.35);
}

/* Glow Animation */
.glow-pulse {
  position: relative;
  animation: glow 0.9s ease-out;
}
@keyframes glow {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.35); }
  100% { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
}

/* Responsive */
@media (max-width: 1024px) {
  .overview-cards { grid-template-columns: repeat(2, 1fr); }
  .analytics-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .overview-cards { grid-template-columns: 1fr 1fr; gap: 12px; }
  .overview-card { padding: 16px; gap: 12px; }
  .overview-icon { width: 40px; height: 40px; font-size: 18px; }
  .overview-value { font-size: 20px; }
  .analytics-card { padding: 18px; }
  .trend-bars { grid-template-columns: 1fr 1fr; }
  .card-title-row { flex-direction: column; align-items: flex-start; }
  .results-tabs { width: 100%; }
  .results-tabs button { flex: 1; }
}
</style>

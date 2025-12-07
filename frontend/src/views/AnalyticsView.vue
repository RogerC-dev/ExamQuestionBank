<template>
  <div class="analytics-view">
    <div class="container">
      <div class="analytics-header">
        <h2>學習追蹤分析</h2>
      </div>

      <div v-if="loading" class="loading">載入中...</div>

      <template v-else>
        <div class="analytics-grid">
          <div class="analytics-card">
            <div class="card-header">
              <h3>正確率趨勢</h3>
              <p class="card-subtitle">同一考卷重複測驗僅保留最新一次，並顯示與前一次的變化</p>
            </div>
            <div v-if="processedTrend.length" class="trend-chart">
              <div class="trend-bars">
                <div
                  v-for="item in processedTrend"
                  :key="item.key"
                  class="trend-bar-wrapper"
                  :class="{'glow-pulse': glowTarget === item.key}"
                  :title="trendTitle(item)"
                  @click="drillToPractice(item)"
                >
                  <div class="trend-bar" :style="{ height: Math.max(6, item.accuracy) + '%' }"></div>
                  <div class="trend-meta">
                    <span class="trend-name">{{ item.exam_name || '未命名考卷' }}</span>
                    <span class="trend-value">
                      {{ item.accuracy }}%
                      <span v-if="item.delta !== null" :class="['delta', {up: item.delta > 0, down: item.delta < 0}]">
                        ({{ item.delta > 0 ? '+' : '' }}{{ item.delta }}%)
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-chart"><p>尚無測驗記錄</p></div>
          </div>

          <div class="analytics-card">
            <div class="card-header">
              <h3>常錯考卷 / 題目</h3>
              <p class="card-subtitle">點擊即可回到練習頁並聚焦該考卷/題目</p>
            </div>
            <div v-if="topWrongItems.length" class="hot-list">
              <div
                v-for="item in topWrongItems"
                :key="item.key"
                class="hot-item"
                :class="{'glow-pulse': glowTarget === item.key}"
                @click="drillToPractice(item)"
              >
                <div class="hot-title">{{ item.label }}</div>
                <div class="hot-meta">
                  <span>{{ item.tag }}</span>
                  <span class="hot-count">錯 {{ item.count }} 次</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-results"><p>目前沒有常錯統計，先去練習幾回吧！</p></div>
          </div>
        </div>

        <div class="analytics-card">
          <h3>最近測驗記錄</h3>
          <div v-if="recentResults.length > 0" class="results-list">
            <div v-for="result in recentResults" :key="result.id" class="result-item">
              <div class="result-info">
                <span class="result-name">{{ result.exam_name }}</span>
                <span class="result-date">{{ formatDate(result.completed_at) }}</span>
              </div>
              <div class="result-score">
                <span class="score-value">{{ result.score }}</span>
                <span class="score-label">分</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-results"><p>尚無測驗記錄，前往練習開始吧！</p></div>
        </div>

        <div class="action-buttons">
          <button class="btn btn-primary" @click="$router.push('/practice')">前往練習</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import examService from '@/services/examService'

const loading = ref(true)
const stats = ref({
  total_answered: 0, correct_answered: 0, total_bank: 0, exam_count: 0,
  average_score: 0, accuracy: 0, accuracy_trend: [], top_wrong: []
})
const recentResults = ref([])
const glowTarget = ref(null)
const router = useRouter()

const progressPercent = computed(() => {
  if (stats.value.total_bank === 0) return 0
  return Math.min(100, Math.round((stats.value.total_answered / stats.value.total_bank) * 100))
})

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

const topWrongItems = computed(() => {
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

const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('zh-TW')

const loadData = async () => {
  loading.value = true
  try {
    const [statsRes, resultsRes] = await Promise.all([
      examService.getExamStats(),
      examService.getExamResults()
    ])
    stats.value = statsRes.data
    recentResults.value = (resultsRes.data || []).slice(0, 10)
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
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.analytics-header { text-align: center; margin-bottom: 40px; }
.analytics-header h2 { font-size: 28px; font-weight: bold; color: #2c3e50; }
.loading { text-align: center; padding: 60px; color: #666; }

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.analytics-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 10px 28px rgba(15,23,42,0.06);
  border: 1px solid #e6e8ed;
}

.card-header h3 { font-size: 18px; font-weight: 800; margin-bottom: 6px; color: #1f2933; }
.card-subtitle { margin: 0 0 12px; color: #667185; font-size: 13px; }
.analytics-card h3 { font-size: 18px; font-weight: 800; margin-bottom: 12px; color: #1f2933; }

.trend-chart { min-height: 200px; }
.trend-bars { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }
.trend-bar-wrapper { padding: 12px; border: 1px solid #e6e8ed; border-radius: 12px; background: #f9fafc; cursor: pointer; transition: box-shadow 0.2s, border-color 0.2s; }
.trend-bar-wrapper:hover { border-color: rgba(47,95,144,0.35); box-shadow: 0 12px 26px rgba(15,23,42,0.08); }
.trend-bar { width: 100%; height: 110px; border-radius: 10px; background: linear-gradient(180deg, #3b82f6 0%, #c7ddff 100%); position: relative; overflow: hidden; }
.trend-meta { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; }
.trend-name { font-size: 14px; color: #1f2933; font-weight: 700; }
.trend-value { font-size: 13px; color: #4b5563; }
.delta { margin-left: 6px; font-weight: 700; }
.delta.up { color: #15803d; }
.delta.down { color: #b91c1c; }
.empty-chart { height: 150px; display: flex; align-items: center; justify-content: center; color: #999; }

.hot-list { display: flex; flex-direction: column; gap: 10px; }
.hot-item { padding: 14px; border: 1px solid #e6e8ed; border-radius: 12px; background: #fdfefe; cursor: pointer; transition: box-shadow 0.2s, border-color 0.2s; }
.hot-item:hover { border-color: rgba(47,95,144,0.35); box-shadow: 0 10px 22px rgba(15,23,42,0.08); }
.hot-title { font-weight: 700; color: #1f2933; margin-bottom: 4px; }
.hot-meta { display: flex; justify-content: space-between; color: #4b5563; font-size: 13px; }
.hot-count { font-weight: 700; color: #b91c1c; }

.results-list { display: flex; flex-direction: column; gap: 12px; }
.result-item { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #f8f9fa; border-radius: 8px; }
.result-info { display: flex; flex-direction: column; gap: 4px; }
.result-name { font-weight: 500; color: #2c3e50; }
.result-date { font-size: 13px; color: #666; }
.result-score { display: flex; align-items: baseline; gap: 2px; }
.score-value { font-size: 28px; font-weight: bold; color: #2563eb; }
.score-label { font-size: 14px; color: #666; }
.empty-results { text-align: center; padding: 40px; color: #999; }

.action-buttons { text-align: center; margin-top: 24px; }
.btn { padding: 12px 32px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 16px; }
.btn-primary { background: #2563eb; color: white; }
.btn-primary:hover { background: #1d4ed8; }

.glow-pulse {
  position: relative;
  animation: glow 0.9s ease-out;
}

@keyframes glow {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.35); }
  100% { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
}

@media (max-width: 768px) {
  .analytics-grid { grid-template-columns: 1fr; }
  .analytics-card.wide { grid-column: span 1; }
}
</style>

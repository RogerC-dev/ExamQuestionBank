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
            <h3>練習進度</h3>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }">{{ progressPercent }}%</div>
            </div>
            <p style="font-size: 14px; color: #666; margin-top: 12px;">
              已作答 {{ stats.total_answered.toLocaleString() }} / {{ stats.total_bank.toLocaleString() }} 題
            </p>
          </div>
          <div class="analytics-card">
            <h3>正確率趨勢</h3>
            <div v-if="stats.accuracy_trend.length > 0" class="trend-chart">
              <div class="trend-bars">
                <div
                  v-for="(item, index) in stats.accuracy_trend"
                  :key="index"
                  class="trend-bar-wrapper"
                  :title="`${item.exam_name}: ${item.accuracy}%`"
                >
                  <div class="trend-bar" :style="{ height: item.accuracy + '%' }"></div>
                  <span class="trend-label">{{ item.accuracy }}%</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-chart">
              <p>尚無測驗記錄</p>
            </div>
          </div>
        </div>

        <div class="stats-summary">
          <div class="stat-item">
            <span class="stat-value">{{ stats.exam_count }}</span>
            <span class="stat-label">測驗次數</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.average_score }}</span>
            <span class="stat-label">平均分數</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.accuracy }}%</span>
            <span class="stat-label">總正確率</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.correct_answered }}</span>
            <span class="stat-label">答對題數</span>
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
          <div v-else class="empty-results">
            <p>尚無測驗記錄，開始練習吧！</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import examService from '@/services/examService'

const loading = ref(true)
const stats = ref({
  total_answered: 0,
  correct_answered: 0,
  total_bank: 0,
  exam_count: 0,
  average_score: 0,
  accuracy: 0,
  accuracy_trend: []
})
const recentResults = ref([])

const progressPercent = computed(() => {
  if (stats.value.total_bank === 0) return 0
  return Math.min(100, Math.round((stats.value.total_answered / stats.value.total_bank) * 100))
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

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

onMounted(loadData)
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.analytics-header {
  text-align: center;
  margin-bottom: 40px;
}

.analytics-header h2 {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #666;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.analytics-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}

.analytics-card h3 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2c3e50;
}

.progress-bar {
  background: #e0e0e0;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  color: white;
  font-size: 12px;
  font-weight: bold;
  transition: width 0.3s ease;
  min-width: 40px;
}

.trend-chart {
  height: 150px;
  display: flex;
  align-items: flex-end;
}

.trend-bars {
  display: flex;
  gap: 8px;
  width: 100%;
  height: 100%;
  align-items: flex-end;
}

.trend-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.trend-bar {
  width: 100%;
  max-width: 40px;
  background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
}

.trend-label {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.empty-chart {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-item .stat-value {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #2563eb;
}

.stat-item .stat-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-name {
  font-weight: 500;
  color: #2c3e50;
}

.result-date {
  font-size: 13px;
  color: #666;
}

.result-score {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.score-value {
  font-size: 28px;
  font-weight: bold;
  color: #2563eb;
}

.score-label {
  font-size: 14px;
  color: #666;
}

.empty-results {
  text-align: center;
  padding: 40px;
  color: #999;
}

@media (max-width: 768px) {
  .analytics-grid,
  .stats-summary {
    grid-template-columns: 1fr;
  }
}
</style>

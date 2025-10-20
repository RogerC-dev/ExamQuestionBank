<template>
  <div class="analytics-view">
    <div class="container">
      <div class="analytics-header">
        <h2>學習追蹤分析</h2>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <h3>練習進度</h3>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: '65%' }">65%</div>
          </div>
          <p style="font-size: 14px; color: #666; margin-top: 12px;">已作答 1,582 / 2,435 題</p>
        </div>
        <div class="analytics-card">
          <h3>正確率趨勢</h3>
          <div style="text-align: center; padding: 40px; color: #cbd5e0;">
            📊 圖表區域
          </div>
        </div>
      </div>

      <div class="analytics-card">
        <h3>科目分析</h3>
        <div class="subject-stats">
          <div v-for="subject in subjects" :key="subject.name" class="subject-item">
            <div style="flex: 1;">
              <div class="subject-name">{{ subject.name }}</div>
              <div class="subject-bar">
                <div class="subject-bar-fill" :style="{ width: subject.accuracy + '%' }"></div>
              </div>
            </div>
            <div class="subject-progress">
              練習題數: {{ subject.practiced }}<br>
              正確率: {{ subject.accuracy }}%
            </div>
          </div>
        </div>
      </div>

      <div class="analytics-card">
        <h3>錯題本</h3>
        <div class="card-list">
          <div v-for="error in errorQuestions" :key="error.id" class="card-item">
            <div>
              <div class="card-title">{{ error.question }}</div>
              <div class="card-meta">
                <span class="card-badge error">高錯</span>
                <span>錯誤次數: {{ error.errorCount }}次</span>
                <span>最後答題: {{ error.lastAttempt }}</span>
              </div>
            </div>
            <button class="btn btn-primary" @click="retryQuestion(error.id)">重新練習</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const subjects = ref([
  { name: '民法', practiced: 456, accuracy: 76 },
  { name: '刑法', practiced: 389, accuracy: 71 },
  { name: '行政法', practiced: 342, accuracy: 65 }
])

const errorQuestions = ref([
  {
    id: 1,
    question: '關於公司法中有關董事會之決議？',
    errorCount: 3,
    lastAttempt: '2024.03.15'
  }
])

const retryQuestion = (id) => {
  alert(`重新練習題目 ${id}`)
}
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

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
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
}

.subject-stats {
  display: grid;
  gap: 16px;
}

.subject-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.subject-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subject-progress {
  font-size: 14px;
  color: #666;
  text-align: right;
}

.subject-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.subject-bar-fill {
  height: 100%;
  background: #007bff;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.card-list {
  display: grid;
  gap: 12px;
}

.card-item {
  background: white;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 15px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.card-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 13px;
  color: #7f8c8d;
}

.card-badge {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.card-badge.error {
  background: #ffebee;
  color: #c62828;
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

@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}
</style>

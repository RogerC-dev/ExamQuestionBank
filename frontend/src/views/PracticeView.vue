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
        <div class="mode-card">
          <div class="mode-icon">📚</div>
          <div class="mode-title">歷屆考題</div>
          <div class="mode-desc">按年度練習歷屆考題</div>
          <button class="btn-mode" @click="startPractice('historical')">開始練習</button>
        </div>
        <div class="mode-card">
          <div class="mode-icon">📝</div>
          <div class="mode-title">模擬考試</div>
          <div class="mode-desc">模擬真實考試情境</div>
          <button class="btn-mode" @click="startPractice('simulation')">開始測驗</button>
        </div>
        <div class="mode-card">
          <div class="mode-icon">🔀</div>
          <div class="mode-title">混合練習</div>
          <div class="mode-desc">隨機混合不同年度題目</div>
          <button class="btn-mode" @click="startPractice('mixed')">隨機練習</button>
        </div>
        <div class="mode-card">
          <div class="mode-icon">⭐</div>
          <div class="mode-title">收藏題庫</div>
          <div class="mode-desc">複習已收藏的題目</div>
          <button class="btn-mode" @click="startPractice('bookmarked')">快速收藏</button>
        </div>
      </div>

      <!-- Statistics -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-value">3,247</div>
          <div class="stat-label">題庫數</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">1,582</div>
          <div class="stat-label">已練習</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">73%</div>
          <div class="stat-label">正確率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">156</div>
          <div class="stat-label">待複習</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { reactive } from 'vue'

const filters = reactive({
  examSeries: '',
  year: '',
  subject: '',
  difficulty: '',
  keyword: ''
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

const startPractice = () => {
  alert('開始練習 - 實際需載入題目')
}
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

@media (max-width: 768px) {
  .filter-row,
  .practice-modes,
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>

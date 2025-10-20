<template>
  <div class="flashcard-view">
    <div class="container">
      <div class="flashcard-header">
        <h2>快閃卡複習系統</h2>
        <p>使用間隔重複演算法，提升記憶效果</p>
      </div>

      <!-- Flashcard Review Boxes -->
      <div class="flashcard-boxes">
        <div class="flashcard-box today">
          <div class="flashcard-indicator"></div>
          <div class="flashcard-content">
            <div class="flashcard-label">今日待複習</div>
            <div class="flashcard-count">24 張卡片</div>
          </div>
          <button class="flashcard-action" @click="startReview('today')">立即複習</button>
        </div>
        <div class="flashcard-box tomorrow">
          <div class="flashcard-indicator"></div>
          <div class="flashcard-content">
            <div class="flashcard-label">明日預定</div>
            <div class="flashcard-count">18 張卡片</div>
          </div>
          <button class="flashcard-action" @click="viewDetails('tomorrow')">查看詳情</button>
        </div>
        <div class="flashcard-box week">
          <div class="flashcard-indicator"></div>
          <div class="flashcard-content">
            <div class="flashcard-label">本週預定</div>
            <div class="flashcard-count">67 張卡片</div>
          </div>
          <button class="flashcard-action" @click="viewDetails('week')">查看詳情</button>
        </div>
      </div>

      <!-- Flashcard Management -->
      <div class="flashcard-management">
        <h3 class="section-title">快閃卡管理</h3>
        <div class="management-actions">
          <button class="btn btn-primary" @click="createCard">建立新卡片</button>
          <button class="btn btn-secondary" @click="batchImport">批次匯入</button>
          <select v-model="filterStatus" class="btn" style="background: white; border: 1px solid #ddd;">
            <option value="">全部卡片</option>
            <option value="learning">學習中</option>
            <option value="mastered">已掌握</option>
          </select>
        </div>
        <div class="card-list">
          <div class="card-item">
            <div>
              <div class="card-title">民法第 184 條第 1 項規定之侵權行為構成要件為何？</div>
              <div class="card-meta">
                <span class="card-badge">民法</span>
                <span class="card-badge learning">學習中</span>
                <span>下次複習: 2天後</span>
              </div>
            </div>
            <div class="card-actions">
              <button class="icon-btn" @click="editCard(1)">✏️</button>
              <button class="icon-btn" @click="deleteCard(1)">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const filterStatus = ref('')

const startReview = (period) => {
  alert(`🎴 開始${period === 'today' ? '今日' : ''}複習`)
}

const viewDetails = (period) => {
  alert(`查看${period === 'tomorrow' ? '明日' : '本週'}卡片詳情`)
}

const createCard = () => {
  alert('建立新卡片')
}

const batchImport = () => {
  alert('批次匯入卡片')
}

const editCard = (id) => {
  alert(`編輯卡片 ${id}`)
}

const deleteCard = (id) => {
  if (confirm('確定要刪除此卡片嗎？')) {
    alert(`卡片 ${id} 已刪除`)
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.flashcard-header {
  text-align: center;
  margin-bottom: 40px;
}

.flashcard-header h2 {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #2c3e50;
}

.flashcard-header p {
  color: #7f8c8d;
  font-size: 14px;
}

.flashcard-boxes {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.flashcard-box {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.flashcard-box.today {
  border-color: #ff6b6b;
  background: #fff5f5;
}

.flashcard-box.tomorrow {
  border-color: #ffd43b;
  background: #fffbeb;
}

.flashcard-box.week {
  border-color: #51cf66;
  background: #f4fdf6;
}

.flashcard-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.flashcard-box.today .flashcard-indicator {
  background: #ff6b6b;
}

.flashcard-box.tomorrow .flashcard-indicator {
  background: #ffd43b;
}

.flashcard-box.week .flashcard-indicator {
  background: #51cf66;
}

.flashcard-content {
  flex: 1;
}

.flashcard-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.flashcard-count {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.flashcard-action {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.flashcard-action:hover {
  background: #0056b3;
}

.flashcard-management {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 24px;
}

.management-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
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

.card-badge.learning {
  background: #fff3e0;
  color: #f57c00;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: #666;
  padding: 8px;
  transition: color 0.3s;
}

.icon-btn:hover {
  color: #007bff;
}

@media (max-width: 768px) {
  .flashcard-boxes {
    grid-template-columns: 1fr;
  }
}
</style>

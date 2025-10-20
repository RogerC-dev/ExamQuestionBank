<template>
  <div class="admin-view">
    <div class="container">
      <div class="admin-header">
        <h2 class="section-title">題庫管理後台</h2>
        <div class="admin-actions">
          <button class="btn btn-primary" @click="addQuestion">新增題目</button>
          <button class="btn btn-primary" @click="batchImport">批次匯入</button>
          <button class="btn btn-secondary" @click="exportQuestions">匯出題庫</button>
          <button class="btn btn-secondary" @click="viewLogs">查看日誌</button>
        </div>
      </div>

      <!-- Upload Area -->
      <div class="upload-area" @click="handleUpload">
        <div class="upload-icon">📁</div>
        <div class="upload-text">拖放檔案至此或點擊上傳</div>
        <div class="upload-hint">支援格式: JSON, CSV, PDF</div>
      </div>

      <!-- Question Table -->
      <div class="question-table">
        <table>
          <thead>
            <tr>
              <th>題號</th>
              <th>題目內容</th>
              <th>考試別</th>
              <th>年度</th>
              <th>科目</th>
              <th>狀態</th>
              <th>最後更新時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="question in questions" :key="question.id">
              <td>{{ question.id }}</td>
              <td>{{ question.content }}</td>
              <td>{{ question.examType }}</td>
              <td>{{ question.year }}</td>
              <td>{{ question.subject }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="question.status"
                >
                  {{ question.status === 'published' ? '已發布' : '草稿' }}
                </span>
              </td>
              <td>{{ question.updatedAt }}</td>
              <td>
                <button class="icon-btn" @click="editQuestion(question.id)">✏️</button>
                <button class="icon-btn" @click="viewQuestion(question.id)">👁️</button>
                <button class="icon-btn" @click="deleteQuestion(question.id)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Activity Log -->
      <div class="activity-log">
        <h3 class="section-title">操作紀錄</h3>
        <div v-for="activity in activities" :key="activity.id" class="activity-item">
          <div class="activity-icon">{{ activity.icon }}</div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-meta">{{ activity.meta }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const questions = ref([
  {
    id: '#2024-001',
    content: '關於民法第 184 條第1項規定之為侵...',
    examType: '司法官',
    year: '2024',
    subject: '民法',
    status: 'published',
    updatedAt: '2024.03.20'
  },
  {
    id: '#2024-002',
    content: '刑法共犯規定中，關於幫助犯之...',
    examType: '律師',
    year: '2024',
    subject: '刑法',
    status: 'draft',
    updatedAt: '2024.03.19'
  }
])

const activities = ref([
  {
    id: 1,
    icon: '✏️',
    title: '題目 #2024-001 已更新',
    meta: '管理員 admin@example.com | 2024.03.20 14:30'
  },
  {
    id: 2,
    icon: '📤',
    title: '批次匯入 50 題成功',
    meta: '管理員 admin@example.com | 2024.03.20 10:15'
  }
])

const addQuestion = () => {
  alert('新增題目')
}

const batchImport = () => {
  alert('批次匯入')
}

const exportQuestions = () => {
  alert('匯出題庫')
}

const viewLogs = () => {
  alert('查看日誌')
}

const handleUpload = () => {
  alert('📁 檔案上傳功能 - 實際需實作檔案選擇')
}

const editQuestion = (id) => {
  alert(`編輯題目 ${id}`)
}

const viewQuestion = (id) => {
  alert(`查看題目 ${id}`)
}

const deleteQuestion = (id) => {
  if (confirm('確定要刪除此題目嗎？')) {
    alert(`題目 ${id} 已刪除`)
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.admin-actions {
  display: flex;
  gap: 12px;
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

.upload-area {
  background: white;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 60px;
  text-align: center;
  margin-bottom: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.upload-icon {
  font-size: 64px;
  color: #cbd5e0;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 14px;
  color: #999;
}

.question-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  border-bottom: 2px solid #e0e0e0;
}

td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

tr:hover {
  background: #f8f9fa;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.published {
  background: #d4edda;
  color: #155724;
}

.status-badge.draft {
  background: #fff3cd;
  color: #856404;
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

.activity-log {
  background: white;
  padding: 24px;
  border-radius: 8px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-left: 3px solid #007bff;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 12px;
}

.activity-icon {
  font-size: 20px;
  color: #007bff;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.activity-meta {
  font-size: 13px;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .admin-actions {
    flex-wrap: wrap;
  }
}
</style>

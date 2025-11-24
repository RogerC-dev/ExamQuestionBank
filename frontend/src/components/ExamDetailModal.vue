<template>
  <div v-if="visible" class="modal-overlay" @click.self="emitClose">
    <div class="modal-content" role="dialog" aria-modal="true" aria-label="考卷詳細資訊">
      <div class="modal-header">
        <h3>考卷詳細資訊</h3>
        <button class="close-btn" type="button" @click="emitClose" aria-label="關閉">
          ✕
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="detail-status">考卷內容載入中...</div>
        <div v-else-if="error" class="detail-error">{{ error }}</div>
        <div v-else-if="exam" class="detail-content">
          <div class="meta-grid">
            <div class="meta-item">
              <span class="label">考卷名稱</span>
              <p class="value">{{ exam.name }}</p>
            </div>
            <div class="meta-item">
              <span class="label">考試說明</span>
              <p class="value">{{ exam.description }}</p>
            </div>
            <div class="meta-item">
              <span class="label">考試時間限制</span>
              <p class="value">{{ exam.timeLimit != null ? `${exam.timeLimit} 分鐘` : '未設定' }}</p>
            </div>
            <div class="meta-item">
              <span class="label">建立時間</span>
              <p class="value">{{ exam.createdAt }}</p>
            </div>
            <div class="meta-item">
              <span class="label">更新時間</span>
              <p class="value">{{ exam.updatedAt }}</p>
            </div>
            <div class="meta-item">
              <span class="label">題目數量</span>
              <p class="value">{{ questionCount }} 題</p>
            </div>
          </div>

          <div class="question-list">
            <div class="question-list-header">
              <h4>題目列表</h4>
              <span class="question-count">共 {{ questionCount }} 題</span>
            </div>

            <div v-if="questionCount === 0" class="detail-status">尚未加入題目</div>
            <div v-else class="question-table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>順序</th>
                    <th>題目內容</th>
                    <th>科目</th>
                    <th>題型</th>
                    <th>配分</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="question in exam.examQuestions" :key="question.id">
                    <td>{{ question.order }}</td>
                    <td>{{ question.questionContent }}</td>
                    <td>{{ question.questionSubject || '—' }}</td>
                    <td>{{ question.questionCategory || '—' }}</td>
                    <td>{{ question.points != null ? question.points : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="detail-status">找不到考卷資料</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  exam: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const emitClose = () => {
  emit('close')
}

const questionCount = computed(() => props.exam?.examQuestions?.length ?? 0)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 16px;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  width: min(960px, 100%);
  max-height: calc(100vh - 80px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
}

.detail-status {
  text-align: center;
  color: #6b7280;
  padding: 24px 0;
}

.detail-error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 12px 16px;
  border-radius: 8px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.meta-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.label {
  font-size: 12px;
  color: #6b7280;
}

.value {
  margin: 6px 0 0;
  font-weight: 600;
  color: #1f2937;
}

.question-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-count {
  font-size: 14px;
  color: #6b7280;
}

.question-table-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.question-table-wrapper table {
  width: 100%;
  border-collapse: collapse;
}

.question-table-wrapper th,
.question-table-wrapper td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  text-align: left;
}

.question-table-wrapper th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.question-table-wrapper tr:last-child td {
  border-bottom: none;
}

@media (max-width: 640px) {
  .modal-content {
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>

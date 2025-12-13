<template>
  <div class="essay-analysis-view">
    <div class="container">
      <div class="page-header">
        <h2>AI 申論解析</h2>
        <p class="subtitle">貼上申論題目，AI 幫你分析可能涉及的法條、學說與實務見解</p>
      </div>

      <div class="chat-tabs">
        <button :class="{ active: currentTab === 'analyze' }" @click="currentTab = 'analyze'">解析題目</button>
        <button :class="{ active: currentTab === 'history' }" @click="loadHistory(); currentTab = 'history'">歷史記錄</button>
      </div>

      <div v-if="currentTab === 'analyze'" class="analyze-panel">
        <div class="messages-area" ref="messagesContainer">
          <div v-if="!messages.length" class="empty-state">
            <div class="empty-icon"><i class="bi bi-file-earmark-text"></i></div>
            <p>貼上一道申論題，AI 會幫你分析：</p>
            <ul>
              <li>可能涉及的法條</li>
              <li>學說與實務見解</li>
              <li>答題架構參考</li>
            </ul>
          </div>
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
          <div v-if="isLoading" class="message assistant">
            <div class="message-content">
              <div class="message-text typing"><span></span><span></span><span></span></div>
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

        <div class="input-area">
          <textarea
            v-model="inputText"
            @keydown.enter.ctrl.prevent="handleAnalyze"
            placeholder="貼上申論題目內容...（Ctrl+Enter 送出）"
            rows="4"
            :disabled="isLoading"
          ></textarea>
          <button @click="handleAnalyze" :disabled="!inputText.trim() || isLoading" class="btn-analyze">
            分析題目
          </button>
        </div>
      </div>

      <div v-else class="history-panel">
        <div v-if="isHistoryLoading" class="loading">載入中...</div>
        <div v-else-if="!historyItems.length" class="empty-state">尚無解析記錄</div>
        <div v-else class="history-list">
          <div v-for="item in historyItems" :key="item.id" class="history-item">
            <div class="history-question"><strong>題目：</strong>{{ truncate(item.question_text, 100) }}</div>
            <div class="history-analysis" v-html="formatMessage(item.analysis_response)"></div>
            <div class="history-meta">{{ formatDate(item.created_at) }}</div>
            <button class="btn-reuse" @click="reuseQuestion(item)">重新分析此題</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useEssayAnalysisStore } from '@/stores/essayAnalysisStore'

const store = useEssayAnalysisStore()
const { messages, historyItems, isLoading, isHistoryLoading, errorMessage } = storeToRefs(store)

const inputText = ref('')
const currentTab = ref('analyze')
const messagesContainer = ref(null)

const handleAnalyze = async () => {
  if (!inputText.value.trim() || isLoading.value) return
  const text = inputText.value.trim()
  inputText.value = ''
  store.clearError()
  try {
    await store.analyze(text)
    nextTick(() => scrollToBottom())
  } catch (e) {
    console.error(e)
  }
}

const loadHistory = () => {
  store.loadHistory()
}

const reuseQuestion = (item) => {
  inputText.value = item.question_text
  currentTab.value = 'analyze'
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (text = '') => text.replace(/\n/g, '<br>')
const formatTime = (date) => date ? new Date(date).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) : ''
const formatDate = (date) => date ? new Date(date).toLocaleString('zh-TW') : ''
const truncate = (str, len) => str && str.length > len ? str.slice(0, len) + '...' : str

onMounted(() => {
  store.loadHistory()
})
</script>

<style scoped>
.essay-analysis-view {
  min-height: calc(100vh - 200px);
  padding: 24px 0;
}
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}
.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}
.chat-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.chat-tabs button {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 500;
}
.chat-tabs button.active {
  background: var(--primary-soft);
  color: var(--primary);
  border-color: var(--primary);
}
.analyze-panel, .history-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.messages-area {
  min-height: 300px;
  max-height: 450px;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-page);
}
.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 20px;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--primary);
  opacity: 0.7;
}
.empty-state ul {
  list-style: none;
  padding: 0;
  margin-top: 12px;
}
.empty-state li {
  margin: 6px 0;
}
.message {
  display: flex;
  max-width: 85%;
  margin-bottom: 16px;
}
.message.user {
  margin-left: auto;
}
.message-content {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}
.message.user .message-content {
  background: var(--primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.message.assistant .message-content {
  background: #fff;
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}
.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}
.typing {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}
.typing span {
  width: 6px;
  height: 6px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}
.error-message {
  padding: 12px 20px;
  background: #fee;
  color: #c33;
  font-size: 14px;
}
.input-area {
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.input-area textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}
.input-area textarea:focus {
  outline: none;
  border-color: var(--primary);
}
.btn-analyze {
  padding: 12px 24px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-analyze:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.history-panel {
  padding: 20px;
}
.loading {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.history-item {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  background: var(--bg-page);
}
.history-question {
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--text-primary);
}
.history-analysis {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
}
.history-meta {
  font-size: 12px;
  color: var(--text-secondary);
}
.btn-reuse {
  margin-top: 12px;
  padding: 8px 16px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .container { padding: 0 12px; }
  .messages-area { min-height: 250px; max-height: 350px; padding: 12px; }
  .message { max-width: 95%; }
}
</style>

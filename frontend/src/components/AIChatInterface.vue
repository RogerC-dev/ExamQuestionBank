<template>
  <div class="ai-chat-interface">
    <!-- Remove the duplicate header since it's now handled by the parent component -->
    <div class="chat-tabs">
      <button :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">即時對話</button>
      <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">歷史記錄</button>
    </div>

    <div v-if="activeTab === 'chat'" class="chat-panel">
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
        <div v-if="isLoading" class="message assistant">
          <div class="message-content">
            <div class="message-text typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
        <button v-if="errorMessage.includes('使用限制')" @click="goToSubscription" class="btn-upgrade">
          升級至進階版
        </button>
      </div>

      <div class="chat-input-container">
        <textarea
          ref="chatInputRef"
          v-model="inputMessage"
          @keydown.enter.exact.prevent="handleSend"
          @keydown.enter.shift.exact="inputMessage += '\n'"
          placeholder="輸入您的問題..."
          class="chat-input"
          rows="3"
          :disabled="isLoading"
        ></textarea>
        <button
          @click="handleSend"
          class="btn-send"
          :disabled="!inputMessage.trim() || isLoading"
        >
          發送
        </button>
      </div>
    </div>

    <div v-else class="history-panel">
      <div class="history-toolbar">
        <button class="btn-refresh" @click="refreshHistory" :disabled="isHistoryLoading">
          重新整理
        </button>
      </div>
      <div v-if="isHistoryLoading" class="history-placeholder">載入中...</div>
      <div v-else-if="!historyItems.length" class="history-placeholder">尚無對話記錄</div>
      <div v-else class="history-list">
        <div v-for="item in historyItems" :key="item.id" class="history-item">
          <div class="history-question">
            <strong>Q</strong>
            <span v-html="formatMessage(item.message)"></span>
          </div>
          <div v-if="item.response" class="history-answer">
            <strong>A</strong>
            <span v-html="formatMessage(item.response)"></span>
          </div>
          <div class="history-meta">{{ formatTime(item.created_at) }}</div>
          <button class="history-reuse" @click="reuseHistory(item)">引用此題</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import aiService from '@/services/aiService'

const router = useRouter()
const props = defineProps({
  prefill: {
    type: Object,
    default: () => ({ text: '', stamp: 0 })
  }
})

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const messagesContainer = ref(null)
const chatInputRef = ref(null)
const activeTab = ref('chat')
const historyItems = ref([])
const isHistoryLoading = ref(false)

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

watch(() => props.prefill?.stamp, () => {
  if (!props.prefill) return
  inputMessage.value = props.prefill.text || ''
  activeTab.value = 'chat'
  nextTick(() => {
    if (chatInputRef.value) {
      const length = inputMessage.value.length
      chatInputRef.value.focus()
      chatInputRef.value.setSelectionRange(length, length)
    }
  })
})

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  errorMessage.value = ''

  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  isLoading.value = true

  try {
    const response = await aiService.sendMessage(userMessage)
    messages.value.push({
      role: 'assistant',
      content: response.response,
      timestamp: new Date()
    })
  } catch (error) {
    errorMessage.value = error.message || '發送訊息時發生錯誤'
    console.error('AI chat error:', error)
  } finally {
    isLoading.value = false
  }
}

const clearChat = () => {
  if (confirm('確定要清除所有對話記錄嗎？')) {
    messages.value = []
    errorMessage.value = ''
  }
}

const formatMessage = (text = '') => text.replace(/\n/g, '<br>')

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

const goToSubscription = () => {
  router.push('/subscription')
}

const reuseHistory = (entry) => {
  inputMessage.value = entry.message || ''
  activeTab.value = 'chat'
  nextTick(() => {
    chatInputRef.value?.focus()
  })
}

const refreshHistory = () => {
  loadHistory()
}

const loadHistory = async () => {
  isHistoryLoading.value = true
  try {
    const data = await aiService.getHistory(20, 0)
    historyItems.value = data.results || []
    messages.value = historyItems.value.flatMap(item => ([
      { role: 'user', content: item.message, timestamp: new Date(item.created_at) },
      { role: 'assistant', content: item.response, timestamp: new Date(item.created_at) }
    ]))
  } catch (error) {
    console.error('Failed to load chat history:', error)
  } finally {
    isHistoryLoading.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ai-chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  color: #2c3e50;
  border-radius: 0;
  box-shadow: none;
}

/* Removed .chat-header styles since we removed the header */

.chat-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}

.chat-tabs button {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.chat-tabs button.active {
  background: var(--surface-muted);
  color: var(--primary);
  font-weight: 600;
}

.chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--bg-page);
}

.message {
  display: flex;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  margin-left: auto;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  padding: 14px 18px;
  border-radius: 18px;
  position: relative;
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.message.user .message-content {
  background: var(--primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: #fff;
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
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
  opacity: 0.5;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.error-message {
  padding: 12px 20px;
  background: #fee;
  color: #c33;
  border-top: 1px solid #fcc;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.btn-upgrade {
  padding: 6px 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
}

.btn-upgrade:hover {
  background: var(--primary-hover);
}

.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  background: #ffffff;
  border-radius: 0;
}

.chat-input {
  flex: 1;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all 0.2s;
  background: var(--surface);
  color: var(--text-primary);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
}

.chat-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-soft);
}

.chat-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  color: #666;
}

.btn-send {
  padding: 12px 24px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-send:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.history-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  gap: 12px;
  background: var(--bg-page);
  color: var(--text-primary);
}

.history-toolbar {
  display: flex;
  justify-content: flex-end;
}

.btn-refresh {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  color: #2c3e50;
  cursor: pointer;
}

.history-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 40px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.history-item {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  background: var(--surface);
}

.history-question,
.history-answer {
  display: flex;
  gap: 8px;
  line-height: 1.5;
  color: #1f2937;
}

.history-answer {
  margin-top: 8px;
}

.history-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

.history-reuse {
  margin-top: 12px;
  padding: 6px 10px;
  border: none;
  background: var(--primary);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
}

.chat-messages::-webkit-scrollbar,
.history-list::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet 平板 */
@media (max-width: 1024px) {
  .chat-messages {
    padding: 20px;
  }
  .message {
    max-width: 85%;
  }
  .chat-input-container {
    padding: 14px 16px;
  }
  .history-panel {
    padding: 14px 16px;
  }
}

/* Mobile 手機 */
@media (max-width: 768px) {
  .chat-tabs {
    padding: 10px 12px;
    gap: 6px;
  }
  
  .chat-tabs button {
    padding: 8px 10px;
    font-size: 14px;
  }
  
  .chat-messages {
    padding: 16px 12px;
    gap: 16px;
  }
  
  .message {
    max-width: 90%;
  }
  
  .message-content {
    padding: 12px 16px;
    font-size: 14px;
    border-radius: 16px;
  }
  
  .message.user .message-content {
    border-bottom-right-radius: 4px;
  }
  
  .message.assistant .message-content {
    border-bottom-left-radius: 4px;
  }
  
  .message-time {
    font-size: 10px;
  }
  
  .error-message {
    padding: 10px 12px;
    font-size: 13px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .btn-upgrade {
    width: 100%;
    padding: 8px 12px;
  }
  
  .chat-input-container {
    padding: 12px;
    gap: 8px;
    flex-direction: column;
  }
  
  .chat-input {
    padding: 12px;
    font-size: 14px;
    min-height: 80px;
  }
  
  .btn-send {
    width: 100%;
    padding: 12px 20px;
    font-size: 15px;
  }
  
  .history-panel {
    padding: 12px;
  }
  
  .history-toolbar {
    justify-content: center;
  }
  
  .btn-refresh {
    width: 100%;
    padding: 8px 16px;
    font-size: 14px;
  }
  
  .history-item {
    padding: 12px;
  }
  
  .history-question,
  .history-answer {
    font-size: 14px;
    flex-direction: column;
    gap: 6px;
  }
  
  .history-question strong,
  .history-answer strong {
    font-size: 12px;
    color: var(--primary);
  }
  
  .history-meta {
    font-size: 11px;
  }
  
  .history-reuse {
    width: 100%;
    padding: 8px 12px;
    font-size: 14px;
  }
  
  .chat-messages::-webkit-scrollbar,
  .history-list::-webkit-scrollbar {
    width: 4px;
  }
}

/* Small Mobile 小螢幕手機 */
@media (max-width: 480px) {
  .chat-tabs {
    padding: 8px 10px;
  }
  
  .chat-tabs button {
    padding: 6px 8px;
    font-size: 13px;
  }
  
  .chat-messages {
    padding: 12px 8px;
  }
  
  .message {
    max-width: 95%;
  }
  
  .message-content {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .chat-input-container {
    padding: 10px;
  }
  
  .chat-input {
    padding: 10px;
    font-size: 13px;
    min-height: 70px;
  }
  
  .btn-send {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .history-panel {
    padding: 10px 8px;
  }
  
  .history-item {
    padding: 10px;
  }
  
  .history-question,
  .history-answer {
    font-size: 13px;
  }
}

/* Landscape Mobile 橫向手機 */
@media (max-width: 768px) and (orientation: landscape) {
  .chat-input-container {
    flex-direction: row;
  }
  
  .chat-input {
    min-height: 60px;
  }
  
  .btn-send {
    width: auto;
    min-width: 80px;
  }
}
</style>

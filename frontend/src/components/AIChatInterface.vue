<template>
  <div class="ai-chat-interface">
    <div class="chat-header">
      <h3>AI 法律助手</h3>
      <button class="btn-clear" @click="clearChat" v-if="messages.length > 0">
        清除對話
      </button>
    </div>

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
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import aiService from '@/services/aiService'

const router = useRouter()

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const messagesContainer = ref(null)

// 監聽 messages 變化，自動滾動到底部
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

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

  // 加入使用者訊息
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  isLoading.value = true

  try {
    const response = await aiService.sendMessage(userMessage)
    
    // 加入 AI 回應
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

const formatMessage = (text) => {
  // 簡單的格式化：將換行轉為 <br>
  return text.replace(/\n/g, '<br>')
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

const goToSubscription = () => {
  router.push('/subscription')
}

// 載入歷史記錄
const loadHistory = async () => {
  try {
    const data = await aiService.getHistory(20, 0)
    messages.value = data.results.map(item => ({
      role: 'user',
      content: item.message,
      timestamp: new Date(item.created_at)
    })).concat(
      data.results.map(item => ({
        role: 'assistant',
        content: item.response,
        timestamp: new Date(item.created_at)
      }))
    ).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

// 組件掛載時載入歷史記錄
import { onMounted } from 'vue'
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ai-chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.btn-clear {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: #e0e0e0;
  color: #333;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.message.user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: #f0f0f0;
  color: #333;
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
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
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
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
}

.btn-upgrade:hover {
  background: #5568d3;
}

.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.chat-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #667eea;
}

.chat-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-send {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-1px);
}

.btn-send:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

/* 滾動條樣式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>


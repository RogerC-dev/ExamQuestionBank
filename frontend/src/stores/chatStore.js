import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import aiService from '@/services/aiService'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([])
  const historyItems = ref([])
  const isLoading = ref(false)
  const isHistoryLoading = ref(false)
  const errorMessage = ref('')
  const isInitialized = ref(false)

  // Getters
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1] || null)

  // Actions
  const sendMessage = async (userMessage) => {
    if (!userMessage.trim() || isLoading.value) return

    errorMessage.value = ''

    messages.value.push({
      role: 'user',
      content: userMessage.trim(),
      timestamp: new Date()
    })

    isLoading.value = true

    try {
      const response = await aiService.sendMessage(userMessage.trim())
      messages.value.push({
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      })
      return response
    } catch (error) {
      errorMessage.value = error.message || '發送訊息時發生錯誤'
      console.error('AI chat error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const loadHistory = async () => {
    isHistoryLoading.value = true
    try {
      const data = await aiService.getHistory(20, 0)
      historyItems.value = data.results || []
      
      // Only update messages if we haven't had any conversation yet in this session
      if (!isInitialized.value) {
        messages.value = historyItems.value.flatMap(item => ([
          { role: 'user', content: item.message, timestamp: new Date(item.created_at) },
          { role: 'assistant', content: item.response, timestamp: new Date(item.created_at) }
        ]))
        isInitialized.value = true
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    } finally {
      isHistoryLoading.value = false
    }
  }

  const refreshHistory = async () => {
    await loadHistory()
  }

  const clearMessages = () => {
    messages.value = []
    errorMessage.value = ''
  }

  const clearError = () => {
    errorMessage.value = ''
  }

  // Initialize store (called once when store is first used)
  const initialize = async () => {
    if (!isInitialized.value) {
      await loadHistory()
    }
  }

  return {
    // State
    messages,
    historyItems,
    isLoading,
    isHistoryLoading,
    errorMessage,
    isInitialized,
    
    // Getters
    hasMessages,
    lastMessage,
    
    // Actions
    sendMessage,
    loadHistory,
    refreshHistory,
    clearMessages,
    clearError,
    initialize
  }
})

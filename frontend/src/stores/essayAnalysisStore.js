import { defineStore } from 'pinia'
import { ref } from 'vue'
import essayAnalysisService from '@/services/essayAnalysisService'

export const useEssayAnalysisStore = defineStore('essayAnalysis', () => {
  const messages = ref([])
  const historyItems = ref([])
  const isLoading = ref(false)
  const isHistoryLoading = ref(false)
  const errorMessage = ref('')

  const analyze = async (questionText) => {
    if (!questionText.trim() || isLoading.value) return
    errorMessage.value = ''

    messages.value.push({
      role: 'user',
      content: questionText.trim(),
      timestamp: new Date()
    })

    isLoading.value = true
    try {
      const response = await essayAnalysisService.analyze(questionText.trim())
      messages.value.push({
        role: 'assistant',
        content: response.analysis,
        timestamp: new Date()
      })
      return response
    } catch (error) {
      errorMessage.value = error.message || '分析時發生錯誤'
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const loadHistory = async () => {
    isHistoryLoading.value = true
    try {
      const data = await essayAnalysisService.getHistory(20, 0)
      historyItems.value = data.results || []
    } catch (error) {
      console.error('Failed to load essay analysis history:', error)
    } finally {
      isHistoryLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
    errorMessage.value = ''
  }

  const clearError = () => {
    errorMessage.value = ''
  }

  return {
    messages,
    historyItems,
    isLoading,
    isHistoryLoading,
    errorMessage,
    analyze,
    loadHistory,
    clearMessages,
    clearError
  }
})

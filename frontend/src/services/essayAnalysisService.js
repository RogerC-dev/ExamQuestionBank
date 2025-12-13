import api from './api'

const essayAnalysisService = {
  async analyze(questionText) {
    try {
      const response = await api.post('/essay-analysis/analyze/', {
        question_text: questionText
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        window.dispatchEvent(new Event('show-login'))
        throw new Error('請先登入以使用申論解析功能')
      }
      if (error.response?.status === 429) {
        throw new Error(error.response.data.error || '已達到每日使用限制')
      }
      throw error
    }
  },

  async getHistory(limit = 20, offset = 0) {
    try {
      const response = await api.get('/essay-analysis/history/', {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        window.dispatchEvent(new Event('show-login'))
        throw new Error('請先登入以查看歷史記錄')
      }
      throw error
    }
  }
}

export default essayAnalysisService

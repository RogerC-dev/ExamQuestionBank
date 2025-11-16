import api from './api'

const aiService = {
  /**
   * 發送訊息給 AI
   * @param {string} message - 使用者訊息
   * @param {string} contextType - 上下文類型（如：'question', 'case'）
   * @param {number} contextId - 上下文ID（如題目ID）
   * @returns {Promise} AI 回應
   */
  async sendMessage(message, contextType = null, contextId = null) {
    try {
      const response = await api.post('/ai/chat/', {
        message,
        context_type: contextType,
        context_id: contextId
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 429) {
        throw new Error(error.response.data.error || '已達到每日使用限制')
      }
      throw error
    }
  },

  /**
   * 取得聊天記錄
   * @param {number} limit - 返回記錄數量
   * @param {number} offset - 偏移量
   * @returns {Promise} 聊天記錄列表
   */
  async getHistory(limit = 20, offset = 0) {
    try {
      const response = await api.get('/ai/history/', {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * 分析案例
   * @param {string} caseText - 案例文字
   * @returns {Promise} 分析結果
   */
  async analyzeCase(caseText) {
    try {
      const response = await api.post('/ai/analyze-case/', {
        case_text: caseText
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 429) {
        throw new Error(error.response.data.error || '已達到每日使用限制')
      }
      throw error
    }
  }
}

export default aiService


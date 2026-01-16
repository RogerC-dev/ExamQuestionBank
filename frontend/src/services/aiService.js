/**
 * AI Service - Supabase Edge Function
 * Uses Edge Function for AI chat (requires external API calls)
 */
import { supabase } from '@/lib/supabase'

const aiService = {
  /**
   * Send message to AI
   * @param {string} message - User message
   * @param {string} contextType - Context type (e.g., 'question', 'case')
   * @param {number} contextId - Context ID (e.g., question ID)
   * @returns {Promise} AI response
   */
  async sendMessage(message, contextType = null, contextId = null) {
    const { data, error } = await supabase.functions.invoke('ai-chat', {
      body: {
        message,
        context_type: contextType,
        context_id: contextId
      }
    })

    if (error) {
      if (error.message?.includes('401')) {
        window.dispatchEvent(new Event('show-login'))
        throw new Error('請先登入以使用 AI 功能')
      }
      throw new Error(error.message)
    }

    return data
  },

  /**
   * Get chat history from conversation table
   * @param {number} limit - Number of records to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise} Chat history list
   */
  async getHistory(limit = 20, offset = 0) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      window.dispatchEvent(new Event('show-login'))
      throw new Error('請先登入以查看歷史記錄')
    }

    const { data, error } = await supabase.from('conversation')
      .select('*, conversation_message(*)')
      .eq('user_id', user.id)
      .order('updated_at', { ascending: false })
      .range(offset, offset + limit - 1)

    if (error) throw new Error(error.message)
    return data || []
  },

  /**
   * Analyze case text
   * @param {string} caseText - Case text to analyze
   * @returns {Promise} Analysis result
   */
  async analyzeCase(caseText) {
    const { data, error } = await supabase.functions.invoke('ai-analyze', {
      body: {
        case_text: caseText
      }
    })

    if (error) {
      if (error.message?.includes('401')) {
        window.dispatchEvent(new Event('show-login'))
        throw new Error('請先登入以使用案例分析功能')
      }
      throw new Error(error.message)
    }

    return data
  }
}

export default aiService

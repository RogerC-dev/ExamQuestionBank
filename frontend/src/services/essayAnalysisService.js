/**
 * Essay Analysis Service - Supabase Edge Function
 * Uses Edge Function for essay/case analysis (requires external AI API)
 */
import { supabase } from '@/lib/supabase'

const essayAnalysisService = {
  /**
   * Analyze essay text
   * @param {string} essayText - Essay text to analyze
   * @returns {Promise} Analysis result
   */
  async analyzeEssay(essayText) {
    // Note: This requires the ai-analyze Edge Function to be deployed
    // For now, return a placeholder until the Edge Function is ready
    try {
      const { data, error } = await supabase.functions.invoke('ai-analyze', {
        body: {
          case_text: essayText,
          analysis_type: 'essay'
        }
      })

      if (error) {
        if (error.message?.includes('401')) {
          window.dispatchEvent(new Event('show-login'))
          throw new Error('請先登入以使用分析功能')
        }
        throw new Error(error.message)
      }

      return data
    } catch (error) {
      // If Edge Function doesn't exist yet, return a helpful message
      if (error.message?.includes('Function not found')) {
        throw new Error('AI 分析功能尚未部署，請稍後再試')
      }
      throw error
    }
  },

  /**
   * Get analysis history - returns empty for now since conversation table
   * doesn't have context_type column yet
   * @returns {Promise} Analysis history
   */
  async getHistory() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      window.dispatchEvent(new Event('show-login'))
      throw new Error('請先登入以查看歷史記錄')
    }

    // Return empty array for now - conversation table needs context_type column
    // TODO: Add context_type column to conversation table or create separate essay_analysis table
    return []
  }
}

export default essayAnalysisService

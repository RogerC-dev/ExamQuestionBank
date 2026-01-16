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
  },

  /**
   * Get analysis history
   * @returns {Promise} Analysis history
   */
  async getHistory() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      window.dispatchEvent(new Event('show-login'))
      throw new Error('請先登入以查看歷史記錄')
    }

    const { data, error } = await supabase.from('conversation')
      .select('*')
      .eq('user_id', user.id)
      .eq('context_type', 'essay')
      .order('updated_at', { ascending: false })

    if (error) throw new Error(error.message)
    return data || []
  }
}

export default essayAnalysisService

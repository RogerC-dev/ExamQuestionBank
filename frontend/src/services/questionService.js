/**
 * Question Service - Supabase RPC Only
 * No Django fallback - uses RPC functions exclusively
 */
import { supabase } from '@/lib/supabase'

const questionService = {
  // Get questions with filters
  async getQuestions(params = {}) {
    const { data, error } = await supabase.rpc('get_questions', {
      p_subject: params.subject || null,
      p_difficulty: params.difficulty || null,
      p_type: params.type || null,
      p_year: params.year ? parseInt(params.year) : null,
      p_keyword: params.keyword || null,
      p_page: params.page || 1,
      p_page_size: params.page_size || 20
    })
    if (error) throw new Error(error.message)
    return { data }
  },

  // Get single question detail
  async getQuestion(id) {
    const { data, error } = await supabase.rpc('get_question_detail', {
      p_id: parseInt(id)
    })
    if (error) throw new Error(error.message)
    return { data }
  },

  // Toggle bookmark for a question
  async bookmarkQuestion(questionId) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('請先登入')

    // Check if already bookmarked
    const { data: existing } = await supabase.from('bookmark')
      .select('id')
      .match({ user_id: user.id, question_id: questionId })
      .maybeSingle()

    if (existing) {
      // Remove bookmark
      await supabase.from('bookmark').delete().eq('id', existing.id)
      return { data: { bookmarked: false } }
    } else {
      // Add bookmark
      await supabase.from('bookmark').insert({ user_id: user.id, question_id: questionId })
      return { data: { bookmarked: true } }
    }
  },

  // Get user's bookmarked questions
  async getBookmarkedQuestions() {
    const { data, error } = await supabase.rpc('get_bookmarks')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Update a question (admin only)
  async updateQuestion(questionId, questionData) {
    const { data, error } = await supabase.from('question')
      .update(questionData)
      .eq('id', questionId)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Create a new question (admin only)
  async createQuestion(questionData) {
    const { data, error } = await supabase.from('question')
      .insert(questionData)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Delete a question (admin only)
  async deleteQuestion(questionId) {
    const { error } = await supabase.from('question').delete().eq('id', questionId)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Get question options
  async getQuestionOptions(questionId) {
    const res = await this.getQuestion(questionId)
    return { data: res.data?.options || [] }
  },

  // Bulk create questions (admin only)
  async bulkCreateQuestions(questions) {
    const { data, error } = await supabase.from('question')
      .insert(questions)
      .select()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Get next question (random from pool)
  async getNextQuestion(params = {}) {
    const result = await this.getQuestions({ ...params, page_size: 1 })
    const questions = result.data?.results || []
    return { data: questions[0] || null }
  },

  // Submit attempt (currently just returns success - can be enhanced later)
  async submitAttempt(questionId, attemptData) {
    // For now, we don't track individual attempts in Supabase
    // This can be added later with a question_attempt table
    return { data: { success: true, question_id: questionId } }
  },

  // Get attempts (placeholder - needs table)
  async getAttempts() {
    return { data: [] }
  }
}

export default questionService

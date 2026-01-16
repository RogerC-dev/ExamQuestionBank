/**
 * Question Service
 * Automatically switches between Supabase RPC and Django API
 */
import api from './api'
import { supabase } from '@/lib/supabase'

const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'
const BASE_PREFIX = '/question_bank/questions'

export default {
  /**
   * Get questions with filters
   * @param {Object} params - Filter parameters (examSeries, year, subject, difficulty, keyword)
   */
  async getQuestions(params = {}) {
    if (USE_SUPABASE) {
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
    }
    return api.get(`${BASE_PREFIX}/`, { params })
  },

  /**
   * Get single question detail
   * @param {number} id - Question ID
   */
  async getQuestion(id) {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_question_detail', {
        p_id: parseInt(id)
      })
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get(`${BASE_PREFIX}/${id}/`)
  },

  /**
   * Submit an answer attempt (Django only for now)
   * @param {number} questionId - Question ID
   * @param {Object} data - Answer data (selected_options, answer_text, time_spent)
   */
  submitAttempt(questionId, data) {
    return api.post(`${BASE_PREFIX}/${questionId}/attempt/`, data)
  },

  /**
   * Toggle bookmark for a question
   * @param {number} questionId - Question ID
   */
  async bookmarkQuestion(questionId) {
    if (USE_SUPABASE) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Authentication required')

      // Check if already bookmarked
      const { data: existing } = await supabase.from('bookmark')
        .select('id')
        .match({ user_id: user.id, question_id: questionId })
        .single()

      if (existing) {
        // Remove bookmark
        await supabase.from('bookmark').delete().eq('id', existing.id)
        return { data: { bookmarked: false } }
      } else {
        // Add bookmark
        await supabase.from('bookmark').insert({ user_id: user.id, question_id: questionId })
        return { data: { bookmarked: true } }
      }
    }
    return api.post(`${BASE_PREFIX}/${questionId}/bookmark/`)
  },

  /**
   * Get next question based on preferences (Django only)
   * @param {Object} params - Filter parameters
   */
  getNextQuestion(params = {}) {
    return api.get(`${BASE_PREFIX}/next/`, { params })
  },

  /**
   * Get user's bookmarked questions
   */
  async getBookmarkedQuestions() {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_bookmarks')
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get(`${BASE_PREFIX}/bookmarks/`)
  },

  /**
   * Get question attempts history (Django only)
   * @param {Object} params - Filter parameters
   */
  getAttempts(params = {}) {
    return api.get(`${BASE_PREFIX}/attempts/`, { params })
  },

  /**
   * Update a question
   * @param {number} questionId - Question ID
   * @param {Object} data - Question data
   */
  async updateQuestion(questionId, data) {
    if (USE_SUPABASE) {
      const { data: result, error } = await supabase.from('question')
        .update(data)
        .eq('id', questionId)
        .select()
        .single()
      if (error) throw new Error(error.message)
      return { data: result }
    }
    return api.patch(`${BASE_PREFIX}/${questionId}/`, data)
  },

  /**
   * Create a new question
   * @param {Object} data - Question data
   */
  async createQuestion(data) {
    if (USE_SUPABASE) {
      const { data: result, error } = await supabase.from('question')
        .insert(data)
        .select()
        .single()
      if (error) throw new Error(error.message)
      return { data: result }
    }
    return api.post(`${BASE_PREFIX}/`, data)
  },

  /**
   * Bulk create multiple questions (Django only)
   * @param {Array} payload - Array of question objects
   */
  bulkCreateQuestions(payload) {
    return api.post(`${BASE_PREFIX}/bulk-create/`, payload)
  },

  /**
   * Bulk update multiple questions (Django only)
   * @param {Array} payload - Array of question objects with id
   * @param {boolean} partial - If true, will run partial update for each question
   */
  bulkUpdateQuestions(payload, partial = true) {
    const url = `${BASE_PREFIX}/bulk-update/?partial=${partial}`
    return api.patch(url, payload)
  },

  /**
   * Bulk get multiple questions by IDs (Django only)
   * @param {Array<number>} ids - Array of question IDs (max 500)
   * @returns {Promise<{count: number, questions: Array, missing_ids?: Array}>}
   */
  bulkGetQuestions(ids) {
    return api.post(`${BASE_PREFIX}/bulk-get/`, { ids })
  },

  /**
   * Delete a question
   * @param {number} questionId - Question ID
   */
  async deleteQuestion(questionId) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('question').delete().eq('id', questionId)
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.delete(`${BASE_PREFIX}/${questionId}/`)
  },

  /**
   * Get question options (choices) for a question
   * Uses the detail endpoint which returns options
   * @param {number} questionId - Question ID
   */
  async getQuestionOptions(questionId) {
    const res = await this.getQuestion(questionId)
    // The detail endpoint returns options in the response
    return { data: res.data?.options || [] }
  }
}


import api from './api'

const BASE_PREFIX = '/question_bank/questions'

export default {
  /**
   * Get questions with filters
   * @param {Object} params - Filter parameters (examSeries, year, subject, difficulty, keyword)
   */
  getQuestions(params = {}) {
    return api.get(`${BASE_PREFIX}/`, { params })
  },

  /**
   * Get single question detail
   * @param {number} id - Question ID
   */
  getQuestion(id) {
    return api.get(`${BASE_PREFIX}/${id}/`)
  },

  /**
   * Submit an answer attempt
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
  bookmarkQuestion(questionId) {
    return api.post(`${BASE_PREFIX}/${questionId}/bookmark/`)
  },

  /**
   * Get next question based on preferences
   * @param {Object} params - Filter parameters
   */
  getNextQuestion(params = {}) {
    return api.get(`${BASE_PREFIX}/next/`, { params })
  },

  /**
   * Get user's bookmarked questions
   */
  getBookmarkedQuestions() {
    return api.get(`${BASE_PREFIX}/bookmarks/`)
  },

  /**
   * Get question attempts history
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
  updateQuestion(questionId, data) {
    return api.patch(`${BASE_PREFIX}/${questionId}/`, data)
  },

  /**
   * Create a new question
   * @param {Object} data - Question data
   */
  createQuestion(data) {
    return api.post(`${BASE_PREFIX}/`, data)
  },

  /**
   * Bulk create multiple questions
   * @param {Array} payload - Array of question objects
   */
  bulkCreateQuestions(payload) {
    return api.post(`${BASE_PREFIX}/bulk-create/`, payload)
  },

  /**
   * Bulk update multiple questions
   * @param {Array} payload - Array of question objects with id
   * @param {boolean} partial - If true, will run partial update for each question
   */
  bulkUpdateQuestions(payload, partial = true) {
    const url = `${BASE_PREFIX}/bulk-update/?partial=${partial}`
    return api.patch(url, payload)
  },

  /**
   * Bulk get multiple questions by IDs
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
  deleteQuestion(questionId) {
    return api.delete(`${BASE_PREFIX}/${questionId}/`)
  },

  /**
   * Get question options (choices) for a question
   * Uses the detail endpoint which returns options
   * @param {number} questionId - Question ID
   */
  async getQuestionOptions(questionId) {
    const res = await api.get(`${BASE_PREFIX}/${questionId}/`)
    // The detail endpoint returns options in the response
    return { data: res.data.options || [] }
  }
}

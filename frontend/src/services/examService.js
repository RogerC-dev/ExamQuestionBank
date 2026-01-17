/**
 * Exam Service - Django API only
 */
import api from './api'

const handle401 = (error) => {
  if (error.response?.status === 401) {
    window.dispatchEvent(new Event('show-login'))
  }
  throw error
}

const examService = {
  async getExams(params = {}) {
    return api.get('/exams/', { params }).catch(handle401)
  },

  async getExam(examId) {
    return api.get(`/exams/${examId}/`).catch(handle401)
  },

  async createExam(examData) {
    return api.post('/exams/', examData).catch(handle401)
  },

  async updateExam(examId, examData) {
    return api.patch(`/exams/${examId}/`, examData).catch(handle401)
  },

  async deleteExam(examId) {
    return api.delete(`/exams/${examId}/`).catch(handle401)
  },

  async addQuestionToExam(examId, data) {
    return api.post(`/exams/${examId}/add_question/`, data).catch(handle401)
  },

  async removeQuestionFromExam(examId, examQuestionId) {
    return api.delete(`/exams/${examId}/remove_question/?exam_question_id=${examQuestionId}`).catch(handle401)
  },

  updateExamQuestion(examId, data) {
    // Django only for now
    return api.patch(`/exams/${examId}/update_question/`, data).catch(handle401)
  },

  getHistoricalExams(params = {}) {
    // Django only for now - historical is a special collection
    return api.get('/exams/historical/', { params }).catch(handle401)
  },

  async getPracticeExams(params = {}) {
    return api.get('/exams/practice-list/', { params }).catch(handle401)
  },

  startExam(examId) {
    // Can just return exam detail for Supabase
    return this.getExam(examId)
  },

  getExamsByQuestion(questionId) {
    // Django only for now
    return api.get('/exams/by_question/', { params: { question_id: questionId } }).catch(handle401)
  },

  getExamsByQuestions(questionIds) {
    // Django only for now
    const questionIdsStr = Array.isArray(questionIds) ? questionIds.join(',') : questionIds
    return api.get('/exams/by_questions/', { params: { question_ids: questionIdsStr } }).catch(handle401)
  },

  async saveExamResult(resultData) {
    return api.post('/exam-results/', resultData).catch(handle401)
  },

  async getExamResults() {
    return api.get('/exam-results/').catch(handle401)
  },

  getExamStats() {
    // Django only for now
    return api.get('/exam-stats/').catch(handle401)
  },

  getTrends(params = {}) {
    // Django only for now
    return api.get('/analytics/trends/', { params }).catch(handle401)
  },

  async getWrongQuestions() {
    return api.get('/wrong-questions/').catch(handle401)
  },

  async markWrongQuestionReviewed(id, reviewed = true) {
    return api.patch(`/wrong-questions/${id}/`, { reviewed }).catch(handle401)
  },

  async deleteWrongQuestion(id) {
    return api.delete(`/wrong-questions/${id}/`).catch(handle401)
  },

  async getBookmarks() {
    return api.get('/bookmarks/').catch(handle401)
  },

  async addBookmark(questionIds) {
    return api.post('/bookmarks/', { question_ids: questionIds }).catch(handle401)
  },

  async removeBookmark(questionId) {
    return api.delete(`/bookmarks/${questionId}/`).catch(handle401)
  },

  async createCustomExam({ name, questionIds, timeLimit } = {}) {
    return api.post('/exams/custom/', {
      name,
      question_ids: questionIds,
      time_limit: timeLimit
    }).catch(handle401)
  }
}

export default examService


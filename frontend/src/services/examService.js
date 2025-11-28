import api from './api'

const examService = {
  getExams(params = {}) {
    return api.get('/exams/', { params })
  },

  getExam(examId) {
    return api.get(`/exams/${examId}/`)
  },

  createExam(examData) {
    return api.post('/exams/', examData)
  },

  updateExam(examId, examData) {
    return api.patch(`/exams/${examId}/`, examData)
  },

  deleteExam(examId) {
    return api.delete(`/exams/${examId}/`)
  },

  addQuestionToExam(examId, data) {
    return api.post(`/exams/${examId}/add_question/`, data)
  },

  removeQuestionFromExam(examId, examQuestionId) {
    return api.delete(`/exams/${examId}/remove_question/?exam_question_id=${examQuestionId}`)
  },

  updateExamQuestion(examId, data) {
    return api.patch(`/exams/${examId}/update_question/`, data)
  },

  getHistoricalExams(params = {}) {
    return api.get('/exams/historical/', { params })
  },

  startExam(examId) {
    return api.post(`/exams/${examId}/start/`)
  },

  saveExamResult(resultData) {
    return api.post('/exam-results/', resultData)
  },

  getExamResults() {
    return api.get('/exam-results/')
  },

  getExamStats() {
    return api.get('/exam-stats/')
  }
}

export default examService

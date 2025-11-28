import api from './api'

const handle401 = (error) => {
  if (error.response?.status === 401) {
    window.dispatchEvent(new Event('show-login'))
  }
  throw error
}

const examService = {
  getExams(params = {}) {
    return api.get('/exams/', { params }).catch(handle401)
  },
  getExam(examId) {
    return api.get(`/exams/${examId}/`).catch(handle401)
  },
  createExam(examData) {
    return api.post('/exams/', examData).catch(handle401)
  },
  updateExam(examId, examData) {
    return api.patch(`/exams/${examId}/`, examData).catch(handle401)
  },
  deleteExam(examId) {
    return api.delete(`/exams/${examId}/`).catch(handle401)
  },
  addQuestionToExam(examId, data) {
    return api.post(`/exams/${examId}/add_question/`, data).catch(handle401)
  },
  removeQuestionFromExam(examId, examQuestionId) {
    return api.delete(`/exams/${examId}/remove_question/?exam_question_id=${examQuestionId}`).catch(handle401)
  },
  updateExamQuestion(examId, data) {
    return api.patch(`/exams/${examId}/update_question/`, data).catch(handle401)
  },
  getHistoricalExams(params = {}) {
    return api.get('/exams/historical/', { params }).catch(handle401)
  },
  startExam(examId) {
    return api.post(`/exams/${examId}/start/`).catch(handle401)
  },
  saveExamResult(resultData) {
    return api.post('/exam-results/', resultData).catch(handle401)
  },
  getExamResults() {
    return api.get('/exam-results/').catch(handle401)
  },
  getExamStats() {
    return api.get('/exam-stats/').catch(handle401)
  },
  getWrongQuestions() {
    return api.get('/wrong-questions/').catch(handle401)
  },
  markWrongQuestionReviewed(id, reviewed = true) {
    return api.patch(`/wrong-questions/${id}/`, { reviewed }).catch(handle401)
  },
  deleteWrongQuestion(id) {
    return api.delete(`/wrong-questions/${id}/`).catch(handle401)
  },
  getBookmarks() {
    return api.get('/bookmarks/').catch(handle401)
  },
  addBookmark(questionIds) {
    return api.post('/bookmarks/', { question_ids: questionIds }).catch(handle401)
  },
  removeBookmark(questionId) {
    return api.delete(`/bookmarks/${questionId}/`).catch(handle401)
  }
}

export default examService

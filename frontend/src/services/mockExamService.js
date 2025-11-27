import api from './api'

const mockExamService = {
  generateMockExam(payload) {
    return api.post('/mock-exams/', payload)
  },
  getMockExams(params = {}) {
    return api.get('/mock-exams/', { params })
  },
  getMockExam(id) {
    return api.get(`/mock-exams/${id}/`)
  }
}

export default mockExamService


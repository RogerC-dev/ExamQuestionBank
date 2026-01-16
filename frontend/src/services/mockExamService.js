/**
 * Mock Exam Service - Uses examService
 * Mock exams use the same RPC functions as regular exams
 */
import examService from './examService'

const mockExamService = {
  // Get mock exams (same as practice exams)
  async getMockExams() {
    return examService.getExams()
  },

  // Get mock exam detail
  async getMockExam(examId) {
    return examService.getExam(examId)
  },

  // Start mock exam
  async startMockExam(examId) {
    return examService.startExam(examId)
  },

  // Submit mock exam result
  async submitMockResult(resultData) {
    return examService.saveExamResult(resultData)
  }
}

export default mockExamService

import api from './api'

const examService = {
  /**
   * 取得考卷列表
   * @returns {Promise} 考卷列表
   */
  getExams(params = {}) {
    return api.get('/exams/', { params })
  },

  /**
   * 取得單一考卷詳細資訊（包含所有題目）
   * @param {number} examId - 考卷 ID
   * @returns {Promise} 考卷詳細資訊
   */
  getExam(examId) {
    return api.get(`/exams/${examId}/`)
  },

  /**
   * 建立新考卷
   * @param {Object} examData - 考卷資料 {name, description, time_limit}
   * @returns {Promise} 建立的考卷
   */
  createExam(examData) {
    return api.post('/exams/', examData)
  },

  /**
   * 更新考卷
   * @param {number} examId - 考卷 ID
   * @param {Object} examData - 考卷資料
   * @returns {Promise} 更新後的考卷
   */
  updateExam(examId, examData) {
    return api.patch(`/exams/${examId}/`, examData)
  },

  /**
   * 刪除考卷
   * @param {number} examId - 考卷 ID
   * @returns {Promise}
   */
  deleteExam(examId) {
    return api.delete(`/exams/${examId}/`)
  },

  /**
   * 新增題目到考卷
   * @param {number} examId - 考卷 ID
   * @param {Object} data - {question: questionId, order: number, points: number}
   * @returns {Promise} 新增的考卷題目關聯
   */
  addQuestionToExam(examId, data) {
    return api.post(`/exams/${examId}/add_question/`, data)
  },

  /**
   * 從考卷移除題目
   * @param {number} examId - 考卷 ID
   * @param {number} examQuestionId - 考卷題目關聯 ID
   * @returns {Promise}
   */
  removeQuestionFromExam(examId, examQuestionId) {
    return api.delete(`/exams/${examId}/remove_question/?exam_question_id=${examQuestionId}`)
  },

  /**
   * 更新考卷中的題目資訊（順序、配分）
   * @param {number} examId - 考卷 ID
   * @param {Object} data - {exam_question_id, order?, points?}
   * @returns {Promise} 更新後的考卷題目關聯
   */
  updateExamQuestion(examId, data) {
    return api.patch(`/exams/${examId}/update_question/`, data)
  }
}

export default examService

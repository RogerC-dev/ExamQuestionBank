/**
 * Exam Service
 * Automatically switches between Supabase RPC and Django API
 */
import api from './api'
import { supabase } from '@/lib/supabase'

const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'

const handle401 = (error) => {
  if (error.response?.status === 401) {
    window.dispatchEvent(new Event('show-login'))
  }
  throw error
}

const examService = {
  async getExams(params = {}) {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_practice_exams')
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get('/exams/', { params }).catch(handle401)
  },

  async getExam(examId) {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_exam_detail', {
        p_id: parseInt(examId)
      })
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get(`/exams/${examId}/`).catch(handle401)
  },

  async createExam(examData) {
    if (USE_SUPABASE) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Authentication required')
      const { data, error } = await supabase.from('exam').insert({
        ...examData,
        creator: user.id
      }).select().single()
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.post('/exams/', examData).catch(handle401)
  },

  async updateExam(examId, examData) {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.from('exam')
        .update(examData)
        .eq('id', examId)
        .select()
        .single()
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.patch(`/exams/${examId}/`, examData).catch(handle401)
  },

  async deleteExam(examId) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('exam').delete().eq('id', examId)
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.delete(`/exams/${examId}/`).catch(handle401)
  },

  async addQuestionToExam(examId, data) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('exam_question').insert({
        exam_id: examId,
        question_id: data.question_id,
        order: data.order || 1,
        points: data.points || 1
      })
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.post(`/exams/${examId}/add_question/`, data).catch(handle401)
  },

  async removeQuestionFromExam(examId, examQuestionId) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('exam_question')
        .delete()
        .eq('id', examQuestionId)
      if (error) throw new Error(error.message)
      return { success: true }
    }
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
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_practice_exams')
      if (error) throw new Error(error.message)
      return { data }
    }
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
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('save_exam_result', {
        p_exam_id: resultData.exam_id || null,
        p_exam_name: resultData.exam_name || '',
        p_score: resultData.score || 0,
        p_correct_count: resultData.correct_count || 0,
        p_total_count: resultData.total_count || 0,
        p_duration_seconds: resultData.duration_seconds || null,
        p_answers_json: resultData.answers || null,
        p_wrong_question_ids: resultData.wrong_question_ids || null
      })
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.post('/exam-results/', resultData).catch(handle401)
  },

  async getExamResults() {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_exam_results')
      if (error) throw new Error(error.message)
      return { data }
    }
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
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_wrong_questions')
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get('/wrong-questions/').catch(handle401)
  },

  async markWrongQuestionReviewed(id, reviewed = true) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('wrong_question')
        .update({ reviewed })
        .eq('id', id)
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.patch(`/wrong-questions/${id}/`, { reviewed }).catch(handle401)
  },

  async deleteWrongQuestion(id) {
    if (USE_SUPABASE) {
      const { error } = await supabase.from('wrong_question').delete().eq('id', id)
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.delete(`/wrong-questions/${id}/`).catch(handle401)
  },

  async getBookmarks() {
    if (USE_SUPABASE) {
      const { data, error } = await supabase.rpc('get_bookmarks')
      if (error) throw new Error(error.message)
      return { data }
    }
    return api.get('/bookmarks/').catch(handle401)
  },

  async addBookmark(questionIds) {
    if (USE_SUPABASE) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Authentication required')
      const ids = Array.isArray(questionIds) ? questionIds : [questionIds]
      const inserts = ids.map(qId => ({ user_id: user.id, question_id: qId }))
      const { error } = await supabase.from('bookmark').insert(inserts)
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.post('/bookmarks/', { question_ids: questionIds }).catch(handle401)
  },

  async removeBookmark(questionId) {
    if (USE_SUPABASE) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Authentication required')
      const { error } = await supabase.from('bookmark')
        .delete()
        .match({ user_id: user.id, question_id: questionId })
      if (error) throw new Error(error.message)
      return { success: true }
    }
    return api.delete(`/bookmarks/${questionId}/`).catch(handle401)
  },

  async createCustomExam({ name, questionIds, timeLimit } = {}) {
    if (USE_SUPABASE) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Authentication required')

      // Create exam
      const { data: exam, error: examError } = await supabase.from('exam').insert({
        name,
        time_limit: timeLimit,
        creator: user.id,
        publish: false
      }).select().single()
      if (examError) throw new Error(examError.message)

      // Add questions
      const inserts = questionIds.map((qId, idx) => ({
        exam_id: exam.id,
        question_id: qId,
        order: idx + 1,
        points: 1
      }))
      const { error: qError } = await supabase.from('exam_question').insert(inserts)
      if (qError) throw new Error(qError.message)

      return { data: exam }
    }
    return api.post('/exams/custom/', {
      name,
      question_ids: questionIds,
      time_limit: timeLimit
    }).catch(handle401)
  }
}

export default examService


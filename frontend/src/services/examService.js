/**
 * Exam Service - Supabase RPC Only
 * No Django fallback - uses RPC functions exclusively
 */
import { supabase } from '@/lib/supabase'

const examService = {
  // Get all available exams (published + user's own)
  async getExams() {
    const { data, error } = await supabase.rpc('get_practice_exams')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Get user's own exams only
  async getUserExams() {
    const { data, error } = await supabase.rpc('get_user_exams')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Get exam detail with questions
  async getExam(examId) {
    const { data, error } = await supabase.rpc('get_exam_detail', {
      p_id: parseInt(examId)
    })
    if (error) throw new Error(error.message)
    return { data }
  },

  // Create new exam
  async createExam(examData) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('請先登入')

    const { data, error } = await supabase.from('exam').insert({
      name: examData.name,
      description: examData.description || '',
      time_limit: examData.time_limit || null,
      publish: examData.publish || false,
      creator: user.id
    }).select().single()

    if (error) throw new Error(error.message)
    return { data }
  },

  // Update exam
  async updateExam(examId, examData) {
    const { data, error } = await supabase.from('exam')
      .update(examData)
      .eq('id', examId)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Delete exam
  async deleteExam(examId) {
    const { error } = await supabase.from('exam').delete().eq('id', examId)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Add question to exam
  async addQuestionToExam(examId, data) {
    const { error } = await supabase.from('exam_question').insert({
      exam_id: examId,
      question_id: data.question_id,
      order: data.order || 1,
      points: data.points || 1
    })
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Remove question from exam
  async removeQuestionFromExam(examId, examQuestionId) {
    const { error } = await supabase.from('exam_question')
      .delete()
      .eq('id', examQuestionId)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Get practice exams (same as getExams)
  async getPracticeExams() {
    return this.getExams()
  },

  // Get historical exams (published exams by year)
  async getHistoricalExams(params = {}) {
    let query = supabase.from('exam')
      .select('*, exam_question(count)')
      .eq('publish', true)
      .order('created_at', { ascending: false })

    if (params.year) {
      query = query.eq('year', params.year)
    }

    const { data, error } = await query
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Start exam (returns exam detail)
  async startExam(examId) {
    return this.getExam(examId)
  },

  // Save exam result
  async saveExamResult(resultData) {
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
  },

  // Get exam results
  async getExamResults() {
    const { data, error } = await supabase.rpc('get_exam_results')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Get exam stats (aggregated from results)
  async getExamStats() {
    const { data, error } = await supabase.rpc('get_user_analytics')
    if (error) throw new Error(error.message)
    return { data }
  },

  // Get wrong questions
  async getWrongQuestions() {
    const { data, error } = await supabase.rpc('get_wrong_questions')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Mark wrong question as reviewed
  async markWrongQuestionReviewed(id, reviewed = true) {
    const { error } = await supabase.from('wrong_question')
      .update({ reviewed })
      .eq('id', id)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Delete wrong question record
  async deleteWrongQuestion(id) {
    const { error } = await supabase.from('wrong_question').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Get bookmarks
  async getBookmarks() {
    const { data, error } = await supabase.rpc('get_bookmarks')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Add bookmark
  async addBookmark(questionIds) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('請先登入')

    const ids = Array.isArray(questionIds) ? questionIds : [questionIds]
    const inserts = ids.map(qId => ({ user_id: user.id, question_id: qId }))

    const { error } = await supabase.from('bookmark').insert(inserts)
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Remove bookmark
  async removeBookmark(questionId) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('請先登入')

    const { error } = await supabase.from('bookmark')
      .delete()
      .match({ user_id: user.id, question_id: questionId })
    if (error) throw new Error(error.message)
    return { success: true }
  },

  // Create custom exam from question list
  async createCustomExam({ name, questionIds, timeLimit } = {}) {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('請先登入')

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
  },

  // Get trends (from exam results)
  async getTrends() {
    const { data, error } = await supabase.rpc('get_exam_results')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  }
}

export default examService

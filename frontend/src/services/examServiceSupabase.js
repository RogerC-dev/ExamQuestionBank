/**
 * Exam Service - Supabase RPC Version
 * Uses PostgreSQL RPC functions for efficient data retrieval
 */
import { supabase } from '@/lib/supabase'

const examService = {
    /**
     * Get all exams (published + user's own)
     */
    async getExams() {
        const { data, error } = await supabase.rpc('get_practice_exams')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get user's own exams
     */
    async getUserExams() {
        const { data, error } = await supabase.rpc('get_user_exams')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get exam detail with questions
     */
    async getExam(id) {
        const { data, error } = await supabase.rpc('get_exam_detail', {
            p_id: parseInt(id)
        })
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Create new exam
     */
    async createExam(examData) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Authentication required')

        const { data, error } = await supabase.from('exam').insert({
            ...examData,
            creator: user.id
        }).select().single()

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Update exam
     */
    async updateExam(id, examData) {
        const { data, error } = await supabase.from('exam')
            .update(examData)
            .eq('id', id)
            .select()
            .single()

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Delete exam
     */
    async deleteExam(id) {
        const { error } = await supabase.from('exam').delete().eq('id', id)
        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Add questions to exam
     */
    async addQuestionsToExam(examId, questionIds) {
        const inserts = questionIds.map((qId, idx) => ({
            exam_id: examId,
            question_id: qId,
            order: idx + 1,
            points: 1
        }))

        const { error } = await supabase.from('exam_question').insert(inserts)
        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Remove question from exam
     */
    async removeQuestionFromExam(examId, questionId) {
        const { error } = await supabase.from('exam_question')
            .delete()
            .match({ exam_id: examId, question_id: questionId })

        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Save exam result with wrong question tracking
     */
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

    /**
     * Get exam results
     */
    async getExamResults() {
        const { data, error } = await supabase.rpc('get_exam_results')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get wrong questions list
     */
    async getWrongQuestions() {
        const { data, error } = await supabase.rpc('get_wrong_questions')
        if (error) throw new Error(error.message)
        return { data }
    }
}

export default examService

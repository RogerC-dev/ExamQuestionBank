/**
 * Question Service - Supabase RPC Version
 * Uses PostgreSQL RPC functions for efficient data retrieval
 */
import { supabase } from '@/lib/supabase'

const questionService = {
    /**
     * Get questions with filters and pagination
     */
    async getQuestions(params = {}) {
        const { data, error } = await supabase.rpc('get_questions', {
            p_subject: params.subject || null,
            p_difficulty: params.difficulty || null,
            p_type: params.type || null,
            p_year: params.year || null,
            p_keyword: params.keyword || null,
            p_page: params.page || 1,
            p_page_size: params.page_size || 20
        })

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get single question with details
     */
    async getQuestion(id) {
        const { data, error } = await supabase.rpc('get_question_detail', {
            p_id: parseInt(id)
        })

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get bookmarked questions
     */
    async getBookmarks() {
        const { data, error } = await supabase.rpc('get_bookmarks')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Add bookmark
     */
    async addBookmark(questionId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Authentication required')

        const { error } = await supabase.from('bookmark').insert({
            user_id: user.id,
            question_id: questionId
        })

        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Remove bookmark
     */
    async removeBookmark(questionId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Authentication required')

        const { error } = await supabase.from('bookmark').delete().match({
            user_id: user.id,
            question_id: questionId
        })

        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Get wrong questions
     */
    async getWrongQuestions() {
        const { data, error } = await supabase.rpc('get_wrong_questions')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Mark wrong question as reviewed
     */
    async markWrongQuestionReviewed(questionId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Authentication required')

        const { error } = await supabase.from('wrong_question')
            .update({ reviewed: true })
            .match({ user_id: user.id, question_id: questionId })

        if (error) throw new Error(error.message)
        return { success: true }
    },

    /**
     * Create question (admin only)
     */
    async createQuestion(questionData) {
        const { data, error } = await supabase.from('question').insert(questionData).select().single()
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Update question (admin only)
     */
    async updateQuestion(id, questionData) {
        const { data, error } = await supabase.from('question').update(questionData).eq('id', id).select().single()
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Delete question (admin only)
     */
    async deleteQuestion(id) {
        const { error } = await supabase.from('question').delete().eq('id', id)
        if (error) throw new Error(error.message)
        return { success: true }
    }
}

export default questionService

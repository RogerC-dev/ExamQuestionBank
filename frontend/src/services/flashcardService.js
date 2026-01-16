/**
 * Flashcard Service - Supabase RPC Only
 * No Django fallback - uses RPC functions exclusively
 */
import { supabase } from '@/lib/supabase'

const flashcardService = {
    // Get all flashcards for current user
    async getFlashcards() {
        const { data, error } = await supabase.rpc('get_flashcards')
        if (error) throw new Error(error.message)
        return data || []
    },

    // Get due flashcards for review
    async getDueFlashcards() {
        const { data, error } = await supabase.rpc('get_due_flashcards', { p_limit: 20 })
        if (error) throw new Error(error.message)
        return data || []
    },

    // Get flashcard statistics
    async getStatistics() {
        const { data, error } = await supabase.rpc('get_flashcard_stats')
        if (error) throw new Error(error.message)
        return data || { total: 0, due: 0, mastered: 0, learning: 0 }
    },

    // Get flashcard history (placeholder)
    async getHistory() {
        // Supabase doesn't have a review history table yet
        return []
    },

    // Create flashcard from question
    async createFlashcard(payload) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入後再使用快閃卡功能')

        const { data, error } = await supabase.from('flashcard').insert({
            user_id: user.id,
            question_id: payload.question_id,
            status: 'learning',
            ease_factor: 2.5,
            interval_days: 1,
            repetition: 0,
            review_count: 0,
            next_review_date: new Date().toISOString().split('T')[0]
        }).select().single()

        if (error) throw new Error(error.message)
        return data
    },

    // Review flashcard with SM2 rating (0=Again, 1=Hard, 2=Good, 3=Easy)
    async reviewFlashcard(flashcardId, rating) {
        const { data, error } = await supabase.rpc('review_flashcard', {
            p_flashcard_id: flashcardId,
            p_rating: rating
        })
        if (error) throw new Error(error.message)
        return data
    },

    // Delete flashcard
    async deleteFlashcard(flashcardId) {
        const { error } = await supabase.from('flashcard').delete().eq('id', flashcardId)
        if (error) throw new Error(error.message)
        return { success: true }
    }
}

export default flashcardService

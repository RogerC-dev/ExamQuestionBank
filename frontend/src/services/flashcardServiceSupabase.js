/**
 * Flashcard Service - Supabase RPC Version
 * Uses PostgreSQL RPC functions with SM2 algorithm
 */
import { supabase } from '@/lib/supabase'

const flashcardService = {
    /**
     * Get all flashcards for current user
     */
    async getFlashcards() {
        const { data, error } = await supabase.rpc('get_flashcards')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get due flashcards for review
     */
    async getDueFlashcards(limit = 20) {
        const { data, error } = await supabase.rpc('get_due_flashcards', {
            p_limit: limit
        })
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get flashcard statistics
     */
    async getStats() {
        const { data, error } = await supabase.rpc('get_flashcard_stats')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Review flashcard with SM2 rating
     * @param {number} flashcardId 
     * @param {number} rating - 0=Again, 1=Hard, 2=Good, 3=Easy
     */
    async reviewFlashcard(flashcardId, rating) {
        const { data, error } = await supabase.rpc('review_flashcard', {
            p_flashcard_id: flashcardId,
            p_rating: rating
        })
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Create flashcard from question
     */
    async createFlashcard(questionId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Authentication required')

        const { data, error } = await supabase.from('flashcard').insert({
            user_id: user.id,
            question_id: questionId,
            status: 'learning',
            ease_factor: 2.5,
            interval_days: 1,
            repetition: 0,
            review_count: 0,
            next_review_date: new Date().toISOString().split('T')[0]
        }).select().single()

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Delete flashcard
     */
    async deleteFlashcard(flashcardId) {
        const { error } = await supabase.from('flashcard').delete().eq('id', flashcardId)
        if (error) throw new Error(error.message)
        return { success: true }
    }
}

export default flashcardService

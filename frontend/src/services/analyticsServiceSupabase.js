/**
 * Analytics Service - Supabase RPC Version
 * Uses PostgreSQL RPC functions for user statistics
 */
import { supabase } from '@/lib/supabase'

const analyticsServiceSupabase = {
    /**
     * Get user analytics/statistics
     */
    async getUserAnalytics() {
        const { data, error } = await supabase.rpc('get_user_analytics')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get exam results for trends
     */
    async getExamResults() {
        const { data, error } = await supabase.rpc('get_exam_results')
        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Get wrong questions statistics
     */
    async getWrongQuestions() {
        const { data, error } = await supabase.rpc('get_wrong_questions')
        if (error) throw new Error(error.message)
        return { data }
    }
}

export default analyticsServiceSupabase

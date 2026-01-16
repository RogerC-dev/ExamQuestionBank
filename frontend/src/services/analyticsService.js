/**
 * Analytics Service - Supabase RPC Only
 * No Django fallback - uses RPC functions exclusively
 */
import { supabase } from '@/lib/supabase'

const analyticsService = {
    // Get user analytics/statistics
    async getUserAnalytics() {
        const { data, error } = await supabase.rpc('get_user_analytics')
        if (error) throw new Error(error.message)
        return { data }
    },

    // Get exam results for trends
    async getExamResults() {
        const { data, error } = await supabase.rpc('get_exam_results')
        if (error) throw new Error(error.message)
        return { data: data || [] }
    },

    // Get wrong questions stats
    async getWrongQuestions() {
        const { data, error } = await supabase.rpc('get_wrong_questions')
        if (error) throw new Error(error.message)
        return { data: data || [] }
    },

    // Get trends (returns exam results for chart display)
    async getTrends() {
        const { data, error } = await supabase.rpc('get_exam_results')
        if (error) throw new Error(error.message)
        return { data: data || [] }
    }
}

export default analyticsService

/**
 * Gamification Service - Placeholder for Supabase
 * Gamification features not yet implemented in Supabase
 */
import { supabase } from '@/lib/supabase'

const gamificationService = {
    // Get user points (placeholder)
    async getPoints() {
        return { data: { points: 0, level: 1 } }
    },

    // Get achievements (placeholder)
    async getAchievements() {
        return { data: [] }
    },

    // Get leaderboard (placeholder)
    async getLeaderboard() {
        return { data: [] }
    }
}

export default gamificationService

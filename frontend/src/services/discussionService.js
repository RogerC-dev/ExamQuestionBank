/**
 * Discussion MVP Service - Supabase RPC Only
 * Handles all discussion forum API calls
 */
import { supabase } from '@/lib/supabase'

const discussionService = {
    /**
     * Get paginated list of discussions
     */
    async getDiscussions(limit = 20, offset = 0) {
        const { data, error } = await supabase.rpc('get_discussions_mvp', {
            p_limit: limit,
            p_offset: offset
        })
        if (error) throw new Error(error.message)
        return data || []
    },

    /**
     * Get discussion detail with answers
     */
    async getDiscussion(discussionId) {
        const { data: { user } } = await supabase.auth.getUser()
        const { data, error } = await supabase.rpc('get_discussion_detail_mvp', {
            p_discussion_id: discussionId,
            p_user_id: user?.id || null
        })
        if (error) throw new Error(error.message)
        return data
    },

    /**
     * Create new discussion
     */
    async createDiscussion(title, body) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入')

        // Validate input
        if (!title || title.length < 10) {
            throw new Error('標題至少需要 10 個字元')
        }
        if (!body || body.length < 20) {
            throw new Error('內容至少需要 20 個字元')
        }

        const { data, error } = await supabase
            .from('discussions_mvp')
            .insert({
                user_id: user.id,
                title,
                body
            })
            .select()
            .single()

        if (error) throw new Error(error.message)
        return data
    },

    /**
     * Submit answer to a discussion
     */
    async submitAnswer(discussionId, body) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入')

        // Validate input
        if (!body || body.length < 50) {
            throw new Error('回答至少需要 50 個字元')
        }

        const { data, error } = await supabase
            .from('answers_mvp')
            .insert({
                user_id: user.id,
                discussion_id: discussionId,
                body
            })
            .select()
            .single()

        if (error) throw new Error(error.message)
        return data
    },

    /**
     * Unlock answer with credits
     */
    async unlockAnswer(answerId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入')

        const { data, error } = await supabase.rpc('unlock_answer_mvp', {
            p_user_id: user.id,
            p_answer_id: answerId
        })
        if (error) throw new Error(error.message)

        if (!data.success) {
            throw new Error(data.error || '解鎖失敗')
        }
        return data
    },

    /**
     * Cast vote on answer
     */
    async castVote(answerId, voteValue) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入')

        if (voteValue !== 1 && voteValue !== -1) {
            throw new Error('無效的投票值')
        }

        const { data, error } = await supabase.rpc('cast_vote_mvp', {
            p_user_id: user.id,
            p_answer_id: answerId,
            p_vote_value: voteValue
        })
        if (error) throw new Error(error.message)

        if (!data.success) {
            throw new Error(data.error || '投票失敗')
        }
        return data
    },

    /**
     * Get user credits info
     */
    async getCredits() {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) return { credits: 0, can_claim_daily: false }

        const { data, error } = await supabase.rpc('get_user_credits_mvp', {
            p_user_id: user.id
        })
        if (error) throw new Error(error.message)
        return data
    },

    /**
     * Claim daily credits
     */
    async claimDailyCredits() {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('請先登入')

        const { data, error } = await supabase.rpc('claim_daily_credits_mvp', {
            p_user_id: user.id
        })
        if (error) throw new Error(error.message)

        if (!data.success) {
            throw new Error(data.error || '領取失敗')
        }
        return data
    },

    /**
     * Check if user can post (rate limiting)
     */
    async canCreateDiscussion() {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) return false

        // Check discussions created today
        const today = new Date()
        today.setHours(0, 0, 0, 0)

        const { count, error } = await supabase
            .from('discussions_mvp')
            .select('*', { count: 'exact', head: true })
            .eq('user_id', user.id)
            .gte('created_at', today.toISOString())

        if (error) return true // Allow on error, let backend handle
        return count < 5 // Max 5 discussions per day
    },

    /**
     * Check if user can submit answer (rate limiting)
     */
    async canSubmitAnswer() {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) return false

        // Check answers submitted today
        const today = new Date()
        today.setHours(0, 0, 0, 0)

        const { count, error } = await supabase
            .from('answers_mvp')
            .select('*', { count: 'exact', head: true })
            .eq('user_id', user.id)
            .gte('created_at', today.toISOString())

        if (error) return true // Allow on error, let backend handle
        return count < 10 // Max 10 answers per day
    }
}

export default discussionService

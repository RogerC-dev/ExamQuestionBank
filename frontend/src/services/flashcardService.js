/**
 * Flashcard Service
 * Automatically switches between Supabase RPC and Django API
 */
import api from './api'
import { supabase } from '@/lib/supabase'

const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'

const normalizeError = (error, fallbackMessage = '快閃卡服務目前無法使用，請稍後再試。') => {
    if (error.response?.status === 401) {
        window.dispatchEvent(new Event('show-login'))
        throw new Error('請先登入後再使用快閃卡功能')
    }

    const responseData = error.response?.data
    let message = fallbackMessage

    if (typeof responseData === 'string') {
        message = responseData
    } else if (responseData?.detail) {
        message = responseData.detail
    } else if (responseData?.message) {
        message = responseData.message
    } else if (responseData && typeof responseData === 'object') {
        const firstKey = Object.keys(responseData)[0]
        if (firstKey) {
            const value = responseData[firstKey]
            message = Array.isArray(value) ? value[0] : value
        }
    }

    throw new Error(message)
}

export default {
    async getFlashcards(params = {}) {
        if (USE_SUPABASE) {
            const { data, error } = await supabase.rpc('get_flashcards')
            if (error) throw new Error(error.message)
            return data || []
        }
        try {
            const { data } = await api.get('/flashcards/', { params })
            if (Array.isArray(data)) {
                return data
            }
            if (data?.results) {
                return data.results
            }
            return []
        } catch (error) {
            normalizeError(error)
        }
    },

    async getDueFlashcards() {
        if (USE_SUPABASE) {
            const { data, error } = await supabase.rpc('get_due_flashcards', { p_limit: 20 })
            if (error) throw new Error(error.message)
            return data || []
        }
        try {
            const { data } = await api.get('/flashcards/due/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async getStatistics() {
        if (USE_SUPABASE) {
            const { data, error } = await supabase.rpc('get_flashcard_stats')
            if (error) throw new Error(error.message)
            return data || { total: 0, due: 0, mastered: 0, learning: 0 }
        }
        try {
            const { data } = await api.get('/flashcards/stats/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async getHistory() {
        // Django only for now - Supabase doesn't have review history table
        try {
            const { data } = await api.get('/flashcards/history/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async createFlashcard(payload) {
        if (USE_SUPABASE) {
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
        }
        try {
            const { data } = await api.post('/flashcards/', payload)
            return data
        } catch (error) {
            normalizeError(error, '建立快閃卡失敗，請確認資料是否完整。')
        }
    },

    async reviewFlashcard(flashcardId, rating) {
        if (USE_SUPABASE) {
            const { data, error } = await supabase.rpc('review_flashcard', {
                p_flashcard_id: flashcardId,
                p_rating: rating
            })
            if (error) throw new Error(error.message)
            return data
        }
        try {
            const { data } = await api.post(`/flashcards/${flashcardId}/review/`, { rating })
            return data
        } catch (error) {
            normalizeError(error, '複習回報失敗，請再試一次。')
        }
    },

    async deleteFlashcard(flashcardId) {
        if (USE_SUPABASE) {
            const { error } = await supabase.from('flashcard').delete().eq('id', flashcardId)
            if (error) throw new Error(error.message)
            return { success: true }
        }
        try {
            await api.delete(`/flashcards/${flashcardId}/`)
        } catch (error) {
            normalizeError(error, '刪除快閃卡時發生錯誤。')
        }
    }
}


import api from './api'

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
        try {
            const { data } = await api.get('/flashcards/', { params })
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async getDueFlashcards() {
        try {
            const { data } = await api.get('/flashcards/due/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async getStatistics() {
        try {
            const { data } = await api.get('/flashcards/stats/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async getHistory() {
        try {
            const { data } = await api.get('/flashcards/history/')
            return data
        } catch (error) {
            normalizeError(error)
        }
    },

    async createFlashcard(payload) {
        try {
            const { data } = await api.post('/flashcards/', payload)
            return data
        } catch (error) {
            normalizeError(error, '建立快閃卡失敗，請確認資料是否完整。')
        }
    },

    async reviewFlashcard(flashcardId, rating) {
        try {
            const { data } = await api.post(`/flashcards/${flashcardId}/review/`, { rating })
            return data
        } catch (error) {
            normalizeError(error, '複習回報失敗，請再試一次。')
        }
    },

    async deleteFlashcard(flashcardId) {
        try {
            await api.delete(`/flashcards/${flashcardId}/`)
        } catch (error) {
            normalizeError(error, '刪除快閃卡時發生錯誤。')
        }
    }
}

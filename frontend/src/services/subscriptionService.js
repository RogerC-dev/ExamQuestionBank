import api from './api'

const subscriptionService = {
  /**
   * 取得訂閱狀態
   * @returns {Promise} 訂閱狀態
   */
  async getStatus() {
    try {
      const response = await api.get('/subscription/status/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * 建立訂閱
   * @param {string} tier - 訂閱等級
   * @param {string} paymentIntentId - Stripe Payment Intent ID
   * @returns {Promise} 訂閱資訊
   */
  async createSubscription(tier, paymentIntentId) {
    try {
      const response = await api.post('/subscription/create/', {
        tier,
        payment_intent_id: paymentIntentId
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * 取消訂閱
   * @returns {Promise} 取消結果
   */
  async cancelSubscription() {
    try {
      const response = await api.post('/subscription/cancel/')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default subscriptionService


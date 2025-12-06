import api from './api'

const BASE_PREFIX = '/question_bank/tags'

export default {
  /**
   * Get all tags
   */
  getTags(params = {}) {
    return api.get(`${BASE_PREFIX}/`, { params })
  }
  ,
  /**
   * Create a tag with given name
   * @param {Object} data - { name: string }
   */
  createTag(data) {
    return api.post(`${BASE_PREFIX}/`, data)
  }
}

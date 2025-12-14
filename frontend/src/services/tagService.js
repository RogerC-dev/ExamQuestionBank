import api from './api'

const BASE_PREFIX = '/question_bank/tags'

export default {
  /**
   * Get all tags
   */
  getTags(params = {}) {
    return api.get(`${BASE_PREFIX}/`, { params })
  },

  /**
   * Create a tag with given name
   * @param {Object} data - { name: string }
   */
  createTag(data) {
    return api.post(`${BASE_PREFIX}/`, data)
  },

  /**
   * Update a tag
   * @param {number} id - Tag ID
   * @param {Object} data - { name: string }
   */
  updateTag(id, data) {
    return api.patch(`${BASE_PREFIX}/${id}/`, data)
  },

  /**
   * Delete a tag
   * @param {number} id - Tag ID
   */
  deleteTag(id) {
    return api.delete(`${BASE_PREFIX}/${id}/`)
  }
}

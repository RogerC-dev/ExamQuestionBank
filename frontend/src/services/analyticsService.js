import api from './api'

export const fetchMetrics = () => api.get('/analytics/metrics/')
export const fetchRecommendations = () => api.get('/analytics/recommendations/')
export const fetchMockPerformance = () => api.get('/analytics/mock-performance/')


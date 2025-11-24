import { defineStore } from 'pinia'
import { fetchMetrics, fetchRecommendations } from '@/services/analyticsService'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    metrics: [],
    recommendations: [],
    loading: false,
  }),
  actions: {
    async loadAnalytics() {
      this.loading = true
      try {
        const [metrics, recommendations] = await Promise.all([
          fetchMetrics(),
          fetchRecommendations()
        ])
        this.metrics = metrics.data
        this.recommendations = recommendations.data
      } finally {
        this.loading = false
      }
    }
  }
})


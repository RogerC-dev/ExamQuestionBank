import { defineStore } from 'pinia'
import { fetchNotifications, scheduleNotification } from '@/services/gamificationService'

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    loading: false,
  }),
  actions: {
    async loadNotifications() {
      this.loading = true
      try {
        const { data } = await fetchNotifications()
        this.notifications = data
      } finally {
        this.loading = false
      }
    },
    async schedule(payload) {
      await scheduleNotification(payload)
      await this.loadNotifications()
    }
  }
})


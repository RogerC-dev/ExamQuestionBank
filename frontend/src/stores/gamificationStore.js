import { defineStore } from 'pinia'
import {
  fetchBadges,
  fetchUserBadges,
  fetchUserXP,
  fetchUserTotalXP,
  fetchStudyGroups,
  createStudyGroup,
  joinStudyGroup,
  leaveStudyGroup,
} from '@/services/gamificationService'

export const useGamificationStore = defineStore('gamification', {
  state: () => ({
    badges: [],
    userBadges: [],
    xpLogs: [],
    totalXP: 0,
    studyGroups: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadDashboard() {
      this.loading = true
      try {
        const [badges, userBadges, xpLogs, totalXP, studyGroups] = await Promise.all([
          fetchBadges(),
          fetchUserBadges(),
          fetchUserXP(),
          fetchUserTotalXP(),
          fetchStudyGroups(),
        ])
        this.badges = badges.data
        this.userBadges = userBadges.data
        this.xpLogs = xpLogs.data
        this.totalXP = totalXP.data.total_xp
        this.studyGroups = studyGroups.data
      } catch (err) {
        this.error = err
      } finally {
        this.loading = false
      }
    },
    async createGroup(payload) {
      const response = await createStudyGroup(payload)
      this.studyGroups.push(response.data)
      return response.data
    },
    async joinGroup(groupId) {
      await joinStudyGroup(groupId)
    },
    async leaveGroup(groupId) {
      await leaveStudyGroup(groupId)
      this.studyGroups = this.studyGroups.filter((g) => g.id !== groupId)
    },
  },
})


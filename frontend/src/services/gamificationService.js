import api from './api'

export const fetchBadges = () => api.get('/gamification/badges/')
export const fetchUserBadges = () => api.get('/gamification/user-badges/')
export const fetchUserXP = () => api.get('/gamification/user-xp/')
export const fetchUserTotalXP = () => api.get('/gamification/user-xp/total/')

export const createStudyGroup = (payload) => api.post('/study-groups/', payload)
export const fetchStudyGroups = (params = {}) => api.get('/study-groups/', { params })
export const joinStudyGroup = (groupId) => api.post(`/study-groups/${groupId}/join/`)
export const leaveStudyGroup = (groupId) => api.post(`/study-groups/${groupId}/leave/`)

export const fetchNotifications = () => api.get('/notifications/')
export const scheduleNotification = (payload) => api.post('/notifications/', payload)


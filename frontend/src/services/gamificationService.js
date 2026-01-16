/**
 * Gamification Service - Placeholder for Supabase
 * Gamification features not yet implemented in Supabase
 */
const fetchBadges = async () => ({ data: [] })
const fetchUserBadges = async () => ({ data: [] })
const fetchUserXP = async () => ({ data: [] })
const fetchUserTotalXP = async () => ({ data: { total_xp: 0 } })
const fetchStudyGroups = async () => ({ data: [] })
const createStudyGroup = async () => ({ data: null })
const joinStudyGroup = async () => ({ data: null })
const leaveStudyGroup = async () => ({ data: null })
const fetchNotifications = async () => ({ data: [] })
const scheduleNotification = async () => ({ data: null })

const gamificationService = {
  fetchBadges,
  fetchUserBadges,
  fetchUserXP,
  fetchUserTotalXP,
  fetchStudyGroups,
  createStudyGroup,
  joinStudyGroup,
  leaveStudyGroup,
  fetchNotifications,
  scheduleNotification
}

export {
  fetchBadges,
  fetchUserBadges,
  fetchUserXP,
  fetchUserTotalXP,
  fetchStudyGroups,
  createStudyGroup,
  joinStudyGroup,
  leaveStudyGroup,
  fetchNotifications,
  scheduleNotification
}

export default gamificationService

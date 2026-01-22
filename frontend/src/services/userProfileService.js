/**
 * User Profile Service
 * Handles user profile operations including display name management
 */
import { supabase } from '@/lib/supabase'

const userProfileService = {
    /**
     * Get user profile data
     * @param {string} userId - User UUID
     * @returns {Promise<Object>} User profile data
     */
    async getProfile(userId) {
        const { data, error } = await supabase.rpc('get_user_profile', {
            p_user_id: userId
        })

        if (error) {
            console.error('Error fetching profile:', error)
            throw new Error(error.message)
        }

        return data
    },

    /**
     * Update user display name
     * @param {string} userId - User UUID
     * @param {string} displayName - New display name
     * @returns {Promise<Object>} Result with success status
     */
    async updateDisplayName(userId, displayName) {
        const { data, error } = await supabase.rpc('update_user_display_name', {
            p_user_id: userId,
            p_display_name: displayName
        })

        if (error) {
            console.error('Error updating display name:', error)
            throw new Error(error.message)
        }

        return data
    },

    /**
     * Validate display name
     * @param {string} name - Display name to validate
     * @returns {Object} Validation result with isValid and error message
     */
    validateDisplayName(name) {
        if (!name || name.trim().length === 0) {
            return { isValid: false, error: '名稱不能為空' }
        }

        const trimmed = name.trim()

        if (trimmed.length < 2) {
            return { isValid: false, error: '名稱至少需要 2 個字元' }
        }

        if (trimmed.length > 50) {
            return { isValid: false, error: '名稱不能超過 50 個字元' }
        }

        // Basic character validation (allow letters, numbers, spaces, common punctuation)
        const validPattern = /^[\p{L}\p{N}\s\-_.]+$/u
        if (!validPattern.test(trimmed)) {
            return { isValid: false, error: '名稱包含無效字元' }
        }

        return { isValid: true, error: null }
    },

    /**
     * Get effective display name for current user
     * @returns {Promise<string>} The display name that will be shown
     */
    async getEffectiveDisplayName() {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session?.user) return null

        try {
            const profile = await this.getProfile(session.user.id)
            return profile?.effective_display_name || session.user.email?.split('@')[0] || 'User'
        } catch (e) {
            // Fallback to Google name or email prefix
            return session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'User'
        }
    }
}

export default userProfileService

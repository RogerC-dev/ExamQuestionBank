import { supabase, getSession, getUser } from '@/lib/supabase'

/**
 * Supabase Authentication Service
 * Supports Google OAuth and email/password authentication
 */
const authService = {
    /**
     * Sign in with Google
     * Redirects to Google OAuth flow
     */
    async loginWithGoogle() {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/auth/callback`,
                queryParams: {
                    access_type: 'offline',
                    prompt: 'consent'
                }
            }
        })

        if (error) {
            console.error('Google login error:', error)
            throw new Error(error.message)
        }

        return data
    },

    /**
     * Sign in with email and password
     * @param {Object} credentials - {email, password}
     */
    async login(credentials) {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: credentials.email || credentials.username,
            password: credentials.password
        })

        if (error) {
            throw new Error(error.message)
        }

        return {
            data: {
                access: data.session.access_token,
                refresh: data.session.refresh_token,
                user: this._formatUser(data.user)
            }
        }
    },

    /**
     * Register new user with email
     * @param {Object} userData - {email, password, username}
     */
    async register(userData) {
        const { data, error } = await supabase.auth.signUp({
            email: userData.email,
            password: userData.password,
            options: {
                data: {
                    username: userData.username,
                    full_name: userData.username
                }
            }
        })

        if (error) {
            throw new Error(error.message)
        }

        return {
            data: {
                user: this._formatUser(data.user),
                session: data.session
            }
        }
    },

    /**
     * Logout current user
     */
    async logout() {
        const { error } = await supabase.auth.signOut()

        // Clear any localStorage remnants from old auth
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_id')
        localStorage.removeItem('username')
        localStorage.removeItem('user_role')

        if (error) {
            console.error('Logout error:', error)
        }
    },

    /**
     * Check if user is authenticated
     */
    async isAuthenticated() {
        const session = await getSession()
        return !!session
    },

    /**
     * Get current user info
     */
    async getCurrentUser() {
        const user = await getUser()
        if (!user) return null
        return this._formatUser(user)
    },

    /**
     * Get current session
     */
    async getSession() {
        return await getSession()
    },

    /**
     * Listen for auth state changes
     * @param {Function} callback - Called when auth state changes
     */
    onAuthStateChange(callback) {
        return supabase.auth.onAuthStateChange((event, session) => {
            callback(event, session)
        })
    },

    /**
     * Format user object for app consumption
     * @private
     */
    _formatUser(user) {
        if (!user) return null

        return {
            id: user.id,
            email: user.email,
            username: user.user_metadata?.username || user.email?.split('@')[0] || 'User',
            avatar: user.user_metadata?.avatar_url || null,
            isAdmin: user.user_metadata?.is_admin || false,
            role: user.user_metadata?.is_admin ? 'admin' : 'user',
            provider: user.app_metadata?.provider || 'email'
        }
    },

    /**
     * Refresh token (handled automatically by Supabase)
     * This is here for API compatibility with old authService
     */
    async refreshToken() {
        const { data, error } = await supabase.auth.refreshSession()
        if (error) throw error
        return { data: { access: data.session?.access_token } }
    }
}

export default authService

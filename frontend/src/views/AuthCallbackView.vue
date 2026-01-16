<template>
  <div class="auth-callback">
    <div class="loading-container">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-3">正在完成登入...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/lib/supabase'

const router = useRouter()

onMounted(async () => {
  try {
    // Check if there's a hash with access_token (OAuth implicit flow)
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    const accessToken = hashParams.get('access_token')
    
    if (accessToken) {
      // Supabase should auto-detect and set session from URL hash
      // Wait a moment for Supabase to process the hash
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // Get the session (Supabase will have parsed the hash by now)
    const { data, error } = await supabase.auth.getSession()
    
    if (error) {
      console.error('Auth callback error:', error)
      router.push('/')
      return
    }

    if (data.session) {
      console.log('Login successful:', data.session.user.email)
      
      // Store user info for compatibility with existing code
      const user = data.session.user
      localStorage.setItem('user_id', user.id)
      localStorage.setItem('username', user.user_metadata?.full_name || user.email?.split('@')[0] || 'User')
      localStorage.setItem('user_role', user.user_metadata?.is_admin ? 'admin' : 'user')
      
      // Check for intended path
      const intendedPath = sessionStorage.getItem('intended_path')
      sessionStorage.removeItem('intended_path')
      
      // Clear the hash from URL
      if (window.location.hash) {
        window.history.replaceState(null, '', window.location.pathname)
      }
      
      // Redirect to intended path or practice page
      router.push(intendedPath || '/practice')
    } else {
      // No session, redirect to home
      console.log('No session found after OAuth callback')
      router.push('/')
    }
  } catch (err) {
    console.error('Auth callback error:', err)
    router.push('/')
  }
})
</script>

<style scoped>
.auth-callback {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--bg-primary, #f5f5f5);
}

.loading-container {
  text-align: center;
  padding: 2rem;
  background: var(--bg-secondary, white);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.loading-container p {
  color: var(--text-secondary, #666);
  margin-bottom: 0;
}
</style>

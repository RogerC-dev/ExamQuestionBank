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

const router = useRouter()

onMounted(async () => {
  // Django auth - OAuth callback not used
  // This route is for Supabase OAuth, but we're using Django
  // Just redirect to home page
  router.push('/')
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

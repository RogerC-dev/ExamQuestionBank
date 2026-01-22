<template>
  <div class="profile-view">
    <div class="profile-container">
      <h1 class="page-title">
        <i class="bi bi-person-circle"></i>
        個人資料
      </h1>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>
      
      <div v-else class="profile-content">
        <!-- Display Name Section -->
        <div class="profile-card">
          <h2 class="section-title">顯示名稱</h2>
          <p class="section-desc">
            此名稱將在討論區的發文和回答中顯示，取代你的 Google 名稱。
          </p>
          
          <div class="form-group">
            <label for="displayName">顯示名稱</label>
            <input
              id="displayName"
              v-model="displayName"
              type="text"
              placeholder="輸入您想顯示的名稱"
              :class="{ error: nameError }"
              maxlength="50"
              @input="clearError"
            />
            <span class="char-count" :class="{ warning: displayName.length < 2 }">
              {{ displayName.length }}/50
            </span>
            <span v-if="nameError" class="error-msg">{{ nameError }}</span>
          </div>
          
          <div class="preview-box">
            <span class="preview-label">預覽效果:</span>
            <span class="preview-name">
              <i class="bi bi-person-fill"></i>
              {{ effectiveDisplayName || '匿名用戶' }}
            </span>
          </div>
          
          <button 
            class="btn-save"
            :disabled="saving || !hasChanges"
            @click="saveDisplayName"
          >
            <span v-if="saving" class="loading-spinner"></span>
            <span v-else>
              儲存變更
            </span>
          </button>
          
          <div v-if="successMessage" class="success-msg">
            <i class="bi bi-check-circle-fill"></i>
            {{ successMessage }}
          </div>
        </div>
        
        <!-- Account Info Section -->
        <div class="profile-card">
          <h2 class="section-title">帳號資訊</h2>
          
          <div class="info-row">
            <span class="info-label">已連結 Google 帳號</span>
            <span class="info-value">
              {{ profile?.email || '-' }}
              <span v-if="profile?.google_name" class="google-name">({{ profile.google_name }})</span>
            </span>
          </div>
        </div>
        
        <!-- Credits Section -->
        <div class="profile-card">
          <h2 class="section-title">點數與聲望</h2>
          
          <div class="stats-grid">
            <div class="stat-item">
              <i class="bi bi-gem stat-icon credits"></i>
              <div class="stat-info">
                <span class="stat-value">{{ profile?.credits || 0 }}</span>
                <span class="stat-label">目前點數</span>
              </div>
            </div>
            
            <div class="stat-item">
              <i class="bi bi-mortarboard-fill stat-icon reputation"></i>
              <div class="stat-info">
                <span class="stat-value">{{ profile?.reputation || 0 }}</span>
                <span class="stat-label">聲望值</span>
              </div>
            </div>
            
            <div class="stat-item">
              <i class="bi bi-graph-up-arrow stat-icon earned"></i>
              <div class="stat-info">
                <span class="stat-value">{{ profile?.total_earned || 0 }}</span>
                <span class="stat-label">累計獲得</span>
              </div>
            </div>
            
            <div class="stat-item">
              <i class="bi bi-cart-dash stat-icon spent"></i>
              <div class="stat-info">
                <span class="stat-value">{{ profile?.total_spent || 0 }}</span>
                <span class="stat-label">累計花費</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supabase } from '@/lib/supabase'
import userProfileService from '@/services/userProfileService'

const loading = ref(true)
const saving = ref(false)
const profile = ref(null)
const displayName = ref('')
const originalDisplayName = ref('')
const nameError = ref('')
const successMessage = ref('')

const hasChanges = computed(() => {
  return displayName.value.trim() !== originalDisplayName.value
})

const effectiveDisplayName = computed(() => {
  const name = displayName.value.trim()
  if (name.length >= 2) {
    return name
  }
  return profile.value?.google_name || profile.value?.email?.split('@')[0] || ''
})

async function loadProfile() {
  loading.value = true
  
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.user) {
      return
    }
    
    const data = await userProfileService.getProfile(session.user.id)
    profile.value = data
    displayName.value = data?.display_name || ''
    originalDisplayName.value = data?.display_name || ''
  } catch (e) {
    console.error('Failed to load profile:', e)
  } finally {
    loading.value = false
  }
}

function clearError() {
  nameError.value = ''
  successMessage.value = ''
}

async function saveDisplayName() {
  // Validate
  const validation = userProfileService.validateDisplayName(displayName.value)
  if (!validation.isValid) {
    nameError.value = validation.error
    return
  }
  
  saving.value = true
  nameError.value = ''
  successMessage.value = ''
  
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.user) {
      nameError.value = '請先登入'
      return
    }
    
    const result = await userProfileService.updateDisplayName(
      session.user.id,
      displayName.value.trim()
    )
    
    if (result.success) {
      originalDisplayName.value = result.display_name
      displayName.value = result.display_name
      successMessage.value = result.message
      
      // Update localStorage for immediate effect in header
      localStorage.setItem('username', result.display_name)
    } else {
      nameError.value = result.error
    }
  } catch (e) {
    nameError.value = '儲存失敗，請稍後再試'
    console.error('Save error:', e)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-view {
  min-height: calc(100vh - 140px);
  background: var(--bg-page);
  padding: 2rem 1rem;
}

.profile-container {
  max-width: 700px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-title i {
  color: var(--primary);
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}

.dark .profile-card {
  background: var(--surface);
  border-color: var(--border);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.section-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 1.25rem 0;
  line-height: 1.5;
}

.form-group {
  position: relative;
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-primary);
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.dark .form-group input {
  background: var(--surface-muted);
  border-color: var(--border);
  color: var(--text-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.15);
}

.form-group input.error {
  border-color: var(--destructive);
}

.char-count {
  position: absolute;
  right: 0.75rem;
  top: 2.75rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.char-count.warning {
  color: var(--warning);
}

.error-msg {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--destructive);
}

.success-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: var(--success-soft);
  color: var(--success);
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
}

.preview-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--primary-soft);
  border-radius: 8px;
  margin-bottom: 1.25rem;
}

.preview-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.preview-name {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-weight: 600;
  color: var(--primary);
}

.preview-name i {
  font-size: 0.875rem;
}

.google-name {
  color: var(--text-secondary);
  font-weight: 400;
  margin-left: 0.5rem;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.4);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-page);
  border-radius: 8px;
}

.dark .stat-item {
  background: var(--surface-muted);
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-icon.credits {
  color: var(--icon-blue-fg);
}

.stat-icon.reputation {
  color: var(--icon-amber-fg);
}

.stat-icon.earned {
  color: var(--icon-green-fg);
}

.stat-icon.spent {
  color: var(--icon-orange-fg);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .profile-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .profile-card {
    padding: 1.25rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

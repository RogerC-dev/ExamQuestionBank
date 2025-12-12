<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
        <div class="modal-header">
        <h2>{{ isRegisterMode ? '註冊' : '登入' }}</h2>
        <button class="btn-close" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <!-- 切換 Tab -->
        <div class="auth-tabs">
          <button
            :class="['tab-btn', { active: !isRegisterMode }]"
            @click="switchMode(false)"
          >
            登入
          </button>
          <button
            :class="['tab-btn', { active: isRegisterMode }]"
            @click="switchMode(true)"
          >
            註冊
          </button>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- 錯誤訊息 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <!-- 成功訊息 -->
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>

          <!-- 使用者名稱 -->
          <div class="form-group">
            <label for="username">使用者名稱</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              placeholder="請輸入使用者名稱"
              class="form-input"
              :disabled="loading"
            />
          </div>

          <!-- 電子郵件（僅註冊時顯示） -->
          <div v-if="isRegisterMode" class="form-group">
            <label for="email">電子郵件</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="請輸入電子郵件"
              class="form-input"
              :disabled="loading"
            />
          </div>

          <!-- 密碼 -->
          <div class="form-group">
            <label for="password">密碼</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              placeholder="請輸入密碼"
              class="form-input"
              :disabled="loading"
            />
            <small v-if="isRegisterMode" class="form-hint">
              密碼至少需要 8 個字元，不可為純數字
            </small>
          </div>

          <!-- 確認密碼（僅註冊時顯示） -->
          <div v-if="isRegisterMode" class="form-group">
            <label for="password_confirm">確認密碼</label>
            <input
              id="password_confirm"
              v-model="formData.password_confirm"
              type="password"
              required
              placeholder="請再次輸入密碼"
              class="form-input"
              :disabled="loading"
            />
          </div>

          <!-- 按鈕 -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="loading"
            >
              {{ loading ? (isRegisterMode ? '註冊中...' : '登入中...') : (isRegisterMode ? '註冊' : '登入') }}
            </button>
          </div>
        </form>

        <!-- 切換提示 -->
        <div class="switch-hint">
          <span v-if="!isRegisterMode">
            還沒有帳號？
            <button class="switch-link" type="button" @click="switchMode(true)">立即註冊</button>
          </span>
          <span v-else>
            已有帳號？
            <button class="switch-link" type="button" @click="switchMode(false)">返回登入</button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import authService from '../services/authService'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'success'])

const isVisible = ref(props.visible)
const isRegisterMode = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formData = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: ''
})

// 監聽 visible prop 的變化
watch(() => props.visible, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    // 重置表單
    resetForm()
  }
})

const resetForm = () => {
  formData.value = {
    username: '',
    email: '',
    password: '',
    password_confirm: ''
  }
  errorMessage.value = ''
  successMessage.value = ''
}

const switchMode = (registerMode) => {
  isRegisterMode.value = registerMode
  resetForm()
}

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isRegisterMode.value) {
      // 前端驗證
      if (formData.value.password !== formData.value.password_confirm) {
        errorMessage.value = '兩次輸入的密碼不一致'
        loading.value = false
        return
      }

      if (formData.value.password.length < 8) {
        errorMessage.value = '密碼至少需要 8 個字元'
        loading.value = false
        return
      }

      // 註冊
      await authService.register({
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password,
        password_confirm: formData.value.password_confirm
      })

      // 註冊成功
      emit('success')
      handleClose()
    } else {
      // 登入
      await authService.login({
        username: formData.value.username,
        password: formData.value.password
      })

      // 登入成功
      emit('success')
      handleClose()
    }
  } catch (error) {
    console.error(isRegisterMode.value ? '註冊失敗:' : '登入失敗:', error)

    // 處理錯誤訊息
    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      if (status === 401) {
        errorMessage.value = '帳號或密碼錯誤'
      } else if (status === 400) {
        // 處理驗證錯誤
        if (data.username) {
          errorMessage.value = data.username[0]
        } else if (data.email) {
          errorMessage.value = data.email[0]
        } else if (data.password) {
          errorMessage.value = data.password[0]
        } else if (data.password_confirm) {
          errorMessage.value = data.password_confirm[0]
        } else if (data.non_field_errors) {
          errorMessage.value = data.non_field_errors[0]
        } else if (data.detail) {
          errorMessage.value = data.detail
        } else {
          errorMessage.value = '輸入資料有誤，請檢查後重試'
        }
      } else if (data.detail) {
        errorMessage.value = data.detail
      } else if (data.message) {
        errorMessage.value = data.message
      } else {
        errorMessage.value = isRegisterMode.value ? '註冊失敗，請稍後再試' : '登入失敗，請稍後再試'
      }
    } else {
      errorMessage.value = '網路錯誤，請檢查連線'
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  // Do not close while loading
  if (loading.value) return
  isVisible.value = false
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 32px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 50%;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
}

/* Auth Tabs */
.auth-tabs {
  display: flex;
  margin-bottom: 24px;
  border-radius: 8px;
  background: #f5f5f5;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #333;
}

.tab-btn.active {
  background: white;
  color: #476996;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  padding: 12px 16px;
  margin-bottom: 20px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c62828;
}

.success-message {
  padding: 12px 16px;
  margin-bottom: 20px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #2e7d32;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #476996;
  box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.form-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #888;
}

.form-actions {
  margin-top: 24px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #476996 0%, #35527a 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(71, 105, 150, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(71, 105, 150, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-block {
  width: 100%;
}

.switch-hint {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.switch-hint a {
  color: #476996;
  text-decoration: none;
  font-weight: 500;
}

.switch-hint a:hover {
  text-decoration: underline;
}

.switch-hint .switch-link {
  background: none;
  border: none;
  padding: 0;
  color: #476996;
  font-weight: 500;
  cursor: pointer;
}

.switch-hint .switch-link:hover {
  text-decoration: underline;
}
</style>

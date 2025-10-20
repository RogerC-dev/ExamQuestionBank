<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <h2>登入</h2>
        <button class="btn-close" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- 錯誤訊息 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
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
          </div>

          <!-- 按鈕 -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="loading"
            >
              {{ loading ? '登入中...' : '登入' }}
            </button>
          </div>
        </form>

        <!-- 開發提示 -->
        <div class="dev-hint">
          <p><strong>開發提示：</strong></p>
          <p>預設管理員帳號：admin / admin123</p>
          <p>或在 Django 後端建立超級使用者：</p>
          <code>python manage.py createsuperuser</code>
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
const loading = ref(false)
const errorMessage = ref('')

const formData = ref({
  username: '',
  password: ''
})

// 監聽 visible prop 的變化
watch(() => props.visible, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    // 重置表單
    formData.value = {
      username: '',
      password: ''
    }
    errorMessage.value = ''
  }
})

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''

  console.log('開始登入...')

  try {
    const result = await authService.login(formData.value)
    console.log('登入API成功，結果:', result)

    // 登入成功
    console.log('準備觸發 success 事件')
    emit('success')
    console.log('準備關閉彈窗')
    handleClose()
    console.log('登入流程完成')
  } catch (error) {
    console.error('登入失敗:', error)

    // 處理錯誤訊息
    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      if (status === 401) {
        errorMessage.value = '帳號或密碼錯誤'
      } else if (data.detail) {
        errorMessage.value = data.detail
      } else if (data.message) {
        errorMessage.value = data.message
      } else {
        errorMessage.value = '登入失敗，請稍後再試'
      }
    } else {
      errorMessage.value = '網路錯誤，請檢查連線'
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  if (!loading.value) {
    isVisible.value = false
    emit('close')
  }
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

.error-message {
  padding: 12px 16px;
  margin-bottom: 20px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c62828;
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
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.form-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
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
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-block {
  width: 100%;
}

.dev-hint {
  margin-top: 24px;
  padding: 16px;
  background: #f0f7ff;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.dev-hint p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #555;
}

.dev-hint p:last-child {
  margin-bottom: 0;
}

.dev-hint strong {
  color: #2196f3;
}

.dev-hint code {
  display: block;
  margin-top: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #333;
  border: 1px solid #e3f2fd;
}
</style>

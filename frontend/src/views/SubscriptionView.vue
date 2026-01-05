<template>
  <div class="subscription-view">
    <div class="container">
      <h1 class="page-title">選擇方案</h1>
      <p class="page-subtitle">選擇最適合您的學習方案</p>

      <div class="pricing-grid">
        <!-- Free Tier -->
        <div class="pricing-card">
          <div class="card-header">
            <h3>免費版</h3>
            <div class="price">
              <span class="amount">NT$ 0</span>
            </div>
          </div>
          <ul class="features-list">
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>基礎題庫存取</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>AI 聊天（每日 10 次）</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>基礎快閃卡</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>擴充功能基礎功能</span></li>
          </ul>
          <button 
            class="btn btn-outline" 
            @click="handleStartFree"
            :disabled="subscriptionStatus?.tier === 'free'"
          >
            {{ subscriptionStatus?.tier === 'free' ? '當前方案' : '開始使用' }}
          </button>
        </div>

        <!-- Premium Tier -->
        <div class="pricing-card featured">
          <div class="badge badge-popular">推薦</div>
          <div class="card-header">
            <h3>進階版</h3>
            <div class="price">
              <span class="amount">NT$ 500</span>
              <span class="period">/月</span>
            </div>
          </div>
          <ul class="features-list">
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>無限題庫存取</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>無限 AI 聊天</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>AI 申論批改</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>進階分析報表</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>優先客服支援</span></li>
            <li><div class="check-circle"><i class="bi bi-check2"></i></div><span>擴充功能進階功能</span></li>
          </ul>
          <button 
            class="btn btn-primary" 
            @click="handleSubscribe"
            :disabled="subscriptionStatus?.tier === 'premium' && subscriptionStatus?.is_active"
          >
            {{ subscriptionStatus?.tier === 'premium' && subscriptionStatus?.is_active ? '當前方案' : '立即升級' }}
          </button>
          <div v-if="subscriptionStatus?.tier === 'premium' && subscriptionStatus?.is_active" class="subscription-info">
            <p>到期日：{{ formatDate(subscriptionStatus.expires_at) }}</p>
            <button class="btn-cancel" @click="handleCancel">取消訂閱</button>
          </div>
        </div>
      </div>

      <!-- Payment Modal -->
      <div v-if="showPaymentModal" class="modal-overlay" @click="showPaymentModal = false">
        <div class="modal-content" @click.stop>
          <h3>完成付款</h3>
          <p>請完成 Stripe 付款以啟用進階版功能</p>
          <div class="payment-form">
            <div id="stripe-card-element"></div>
            <button class="btn btn-primary" @click="handlePayment" :disabled="processing">
              {{ processing ? '處理中...' : '確認付款' }}
            </button>
            <button class="btn btn-outline" @click="showPaymentModal = false">取消</button>
          </div>
        </div>
      </div>

      <!-- Current Subscription Info -->
      <div v-if="subscriptionStatus && subscriptionStatus.is_active" class="current-subscription">
        <h3>當前訂閱資訊</h3>
        <div class="subscription-details">
          <p><strong>方案：</strong>{{ subscriptionStatus.tier === 'premium' ? '進階版' : '免費版' }}</p>
          <p v-if="subscriptionStatus.expires_at">
            <strong>到期日：</strong>{{ formatDate(subscriptionStatus.expires_at) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import subscriptionService from '@/services/subscriptionService'
import authService from '@/services/authService'

const router = useRouter()

const subscriptionStatus = ref(null)
const showPaymentModal = ref(false)
const processing = ref(false)

onMounted(async () => {
  if (authService.isAuthenticated()) {
    await loadSubscriptionStatus()
  }
})

const loadSubscriptionStatus = async () => {
  try {
    subscriptionStatus.value = await subscriptionService.getStatus()
  } catch (error) {
    console.error('Failed to load subscription status:', error)
  }
}

const handleStartFree = () => {
  if (!authService.isAuthenticated()) {
    window.dispatchEvent(new Event('show-login'))
  } else {
    router.push('/practice')
  }
}

const handleSubscribe = () => {
  if (!authService.isAuthenticated()) {
    window.dispatchEvent(new Event('show-login'))
    return
  }

  // TODO: 整合 Stripe 付款流程
  // 目前先顯示提示訊息
  alert('Stripe 付款整合功能開發中。請聯繫管理員手動啟用進階版功能。')
  
  // 實際實作時應該：
  // 1. 初始化 Stripe
  // 2. 建立 Payment Intent
  // 3. 顯示付款表單
  // 4. 完成付款後呼叫 createSubscription
}

const handlePayment = async () => {
  processing.value = true
  try {
    // TODO: 實際的 Stripe 付款處理
    // const paymentIntent = await createPaymentIntent()
    // const result = await confirmPayment(paymentIntent)
    // await subscriptionService.createSubscription('premium', result.paymentIntent.id)
    
    alert('付款功能開發中')
    showPaymentModal.value = false
    await loadSubscriptionStatus()
  } catch (error) {
    alert('付款失敗：' + (error.message || '未知錯誤'))
  } finally {
    processing.value = false
  }
}

const handleCancel = async () => {
  if (!confirm('確定要取消訂閱嗎？取消後將無法使用進階版功能。')) {
    return
  }

  try {
    await subscriptionService.cancelSubscription()
    alert('訂閱已取消')
    await loadSubscriptionStatus()
  } catch (error) {
    alert('取消訂閱失敗：' + (error.message || '未知錯誤'))
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}
</script>

<style scoped>
.subscription-view {
  min-height: calc(100vh - 200px);
  padding: 40px 0;
  background: var(--bg-page);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.page-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 48px;
  font-size: 18px;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  margin-bottom: 48px;
}

.pricing-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 40px 32px;
  text-align: center;
  border: 2px solid var(--border);
  transition: all 0.3s;
  position: relative;
}

.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

.pricing-card.featured {
  border-color: var(--primary);
  box-shadow: 0 8px 24px rgba(71, 105, 150, 0.2);
  transform: scale(1.05);
}

.badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--primary);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.card-header {
  margin-bottom: 32px;
}

.card-header h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.amount {
  font-size: 48px;
  font-weight: bold;
  color: var(--primary);
}

.period {
  font-size: 20px;
  color: var(--text-secondary);
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
  text-align: left;
}

.features-list li {
  padding: 12px 0;
  font-size: 16px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
}

.features-list li:last-child {
  border-bottom: none;
}

.btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: var(--primary);
  border: 2px solid var(--primary);
}

.btn-outline:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.btn:disabled {
  background: var(--surface-muted);
  color: var(--text-secondary);
  cursor: not-allowed;
  border-color: var(--border);
}

.subscription-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.subscription-info p {
  margin: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.btn-cancel {
  margin-top: 8px;
  padding: 8px 16px;
  background: transparent;
  color: var(--destructive);
  border: 1px solid var(--destructive);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: var(--destructive-soft);
}

.current-subscription {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  margin-top: 32px;
}

.current-subscription h3 {
  margin-bottom: 16px;
  color: var(--text-primary);
}

.subscription-details p {
  margin: 8px 0;
  color: var(--text-secondary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--surface);
  border-radius: 12px;
  padding: 32px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  margin-bottom: 16px;
  color: var(--text-primary);
}

.payment-form {
  margin-top: 24px;
}

.payment-form button {
  margin-top: 16px;
}

#stripe-card-element {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .pricing-card.featured {
    transform: scale(1);
  }

  .pricing-grid {
    grid-template-columns: 1fr;
  }
}
</style>


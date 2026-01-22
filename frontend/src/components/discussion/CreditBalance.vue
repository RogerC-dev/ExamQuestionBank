<template>
  <div class="credit-balance-mvp">
    <div class="credit-info">
      <i class="bi bi-gem credit-icon"></i>
      <span class="credit-amount">{{ credits }}</span>
      <span class="credit-label">點數</span>
    </div>
    
    <button 
      v-if="canClaim"
      class="claim-btn"
      :disabled="loading"
      @click="handleClaim"
    >
      <span v-if="loading" class="loading-spinner"></span>
      <span v-else>+20 每日獎勵</span>
    </button>
    
    <div v-if="reputation !== undefined" class="reputation-info">
      <i class="bi bi-mortarboard-fill reputation-icon"></i>
      <span class="reputation-amount">{{ reputation }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  credits: {
    type: Number,
    default: 0
  },
  canClaim: {
    type: Boolean,
    default: false
  },
  reputation: {
    type: Number,
    default: undefined
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['claim'])

function handleClaim() {
  emit('claim')
}
</script>

<style scoped>
.credit-balance-mvp {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 12px;
  flex-wrap: wrap;
}

.dark .credit-balance-mvp {
  background: var(--bg-tertiary, #374151);
}

.credit-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.credit-icon {
  font-size: 1.25rem;
  color: var(--icon-blue-fg);
}

.credit-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.credit-label {
  color: var(--text-secondary, #6b7280);
  font-size: 0.875rem;
}

.claim-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.claim-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.claim-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reputation-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  background: var(--bg-primary, white);
  border-radius: 8px;
  border: 1px solid var(--border, #e5e7eb);
}

.dark .reputation-info {
  background: var(--bg-secondary, #1f2937);
  border-color: var(--border, #374151);
}

.reputation-icon {
  font-size: 1rem;
  color: var(--icon-amber-fg);
}

.reputation-amount {
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .credit-balance-mvp {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }
  
  .reputation-info {
    margin-left: 0;
  }
}
</style>

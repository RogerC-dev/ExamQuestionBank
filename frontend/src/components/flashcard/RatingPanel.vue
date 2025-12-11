<template>
  <div v-if="visible" class="rating-section">
    <p class="rating-prompt">你記得這題嗎？</p>
    <div class="rating-buttons">
      <button 
        class="rating-btn again" 
        @click="$emit('rate', 1)" 
        :disabled="disabled"
        data-testid="rating-btn-1"
      >
        <span class="rating-icon"><i class="bi bi-emoji-frown"></i></span>
        <span class="rating-text">完全忘記</span>
        <span class="rating-interval">{{ calculateInterval(1) }}天後</span>
      </button>
      <button 
        class="rating-btn hard" 
        @click="$emit('rate', 2)" 
        :disabled="disabled"
        data-testid="rating-btn-2"
      >
        <span class="rating-icon"><i class="bi bi-emoji-neutral"></i></span>
        <span class="rating-text">很難想起</span>
        <span class="rating-interval">{{ calculateInterval(2) }}天後</span>
      </button>
      <button 
        class="rating-btn good" 
        @click="$emit('rate', 3)" 
        :disabled="disabled"
        data-testid="rating-btn-3"
      >
        <span class="rating-icon"><i class="bi bi-emoji-expressionless"></i></span>
        <span class="rating-text">想了一下</span>
        <span class="rating-interval">{{ calculateInterval(3) }}天後</span>
      </button>
      <button 
        class="rating-btn easy" 
        @click="$emit('rate', 4)" 
        :disabled="disabled"
        data-testid="rating-btn-4"
      >
        <span class="rating-icon"><i class="bi bi-emoji-smile"></i></span>
        <span class="rating-text">還記得</span>
        <span class="rating-interval">{{ calculateInterval(4) }}天後</span>
      </button>
      <button 
        class="rating-btn perfect" 
        @click="$emit('rate', 5)" 
        :disabled="disabled"
        data-testid="rating-btn-5"
      >
        <span class="rating-icon"><i class="bi bi-emoji-laughing"></i></span>
        <span class="rating-text">非常熟悉</span>
        <span class="rating-interval">{{ calculateInterval(5) }}天後</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  visible?: boolean
  disabled?: boolean
  currentInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  disabled: false,
  currentInterval: 1
})

defineEmits<{
  (e: 'rate', rating: number): void
}>()

/**
 * Calculate expected next review interval based on rating
 * Rating 1-2: Reset to 1 day (forgot)
 * Rating 3: Keep current interval
 * Rating 4: Multiply by 1.5
 * Rating 5: Multiply by 2
 */
function calculateInterval(rating: number): number {
  if (rating <= 2) {
    return 1
  } else if (rating === 3) {
    return props.currentInterval
  } else if (rating === 4) {
    return Math.round(props.currentInterval * 1.5)
  } else {
    return Math.round(props.currentInterval * 2)
  }
}
</script>

<style scoped>
/* Rating Section */
.rating-section {
  text-align: center;
}

.rating-prompt {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.rating-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
  font-weight: 600;
}

.rating-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.rating-icon {
  font-size: 28px;
}

.rating-text {
  font-size: 13px;
  font-weight: 600;
}

.rating-interval {
  font-size: 11px;
  opacity: 0.7;
}

/* Rating button color variants */
.rating-btn.again {
  background: #fdf1f1;
  color: #9a1b1b;
  border: 1px solid #f3d6d6;
}

.rating-btn.hard {
  background: #fef9e7;
  color: #92400e;
  border: 1px solid #fbe8c3;
}

.rating-btn.good {
  background: #eff5fc;
  color: #0369a1;
  border: 1px solid #dce7f4;
}

.rating-btn.easy {
  background: #ecf8f1;
  color: #1f6a3b;
  border: 1px solid #cef3e8;
}

.rating-btn.perfect {
  background: #f4f1fb;
  color: #5b21b6;
  border: 1px solid #e8dff8;
}

.rating-btn:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Tablet */
@media (max-width: 1024px) {
  .rating-buttons {
    gap: 10px;
  }
  
  .rating-btn {
    min-width: 90px;
    padding: 14px 16px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .rating-prompt {
    font-size: 16px;
    margin-bottom: 16px;
  }
  
  .rating-buttons {
    flex-direction: column;
    gap: 8px;
    width: 100%;
  }
  
  .rating-btn {
    width: 100%;
    min-width: auto;
    flex-direction: row;
    justify-content: space-between;
    padding: 12px 16px;
  }
  
  .rating-icon {
    font-size: 24px;
  }
  
  .rating-text {
    font-size: 14px;
  }
  
  .rating-interval {
    font-size: 12px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .rating-btn {
    padding: 10px 14px;
  }
}

/* Landscape Mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .rating-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .rating-btn {
    flex: 1;
    min-width: calc(50% - 4px);
  }
}
</style>

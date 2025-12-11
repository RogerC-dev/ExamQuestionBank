<template>
  <div 
    class="timer-component" 
    :class="timerClass"
    role="timer"
    :aria-label="`Time remaining: ${formattedTime}`"
    :aria-live="timerClass === 'danger' ? 'assertive' : 'polite'"
    aria-atomic="true"
  >
    <span class="timer-label" id="timer-label">Time Remaining:</span>
    <span 
      class="timer-value" 
      aria-labelledby="timer-label"
      :aria-description="timerDescription"
    >
      {{ formattedTime }}
    </span>
    <span class="sr-only" v-if="timerClass === 'warning'">Warning: Less than 5 minutes remaining</span>
    <span class="sr-only" v-if="timerClass === 'danger'">Critical: Less than 1 minute remaining</span>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

/**
 * TimerComponent
 * Displays countdown timer with visual feedback based on remaining time
 * Handles auto-submission when timer expires
 */

const props = defineProps({
  timeLimit: {
    type: Number,
    required: true // in seconds
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['time-warning', 'time-critical', 'time-expired'])

const timeLeft = ref(props.timeLimit)
let intervalId = null

const formattedTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
  const seconds = (timeLeft.value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})

const timerClass = computed(() => {
  if (timeLeft.value <= 60) return 'danger'
  if (timeLeft.value <= 300) return 'warning'
  return 'normal'
})

const timerDescription = computed(() => {
  if (timeLeft.value <= 60) return 'Critical: Less than 1 minute remaining'
  if (timeLeft.value <= 300) return 'Warning: Less than 5 minutes remaining'
  return 'Normal time remaining'
})

const startTimer = () => {
  if (intervalId) {
    clearInterval(intervalId)
  }
  
  intervalId = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
      
      // Emit warning events
      if (timeLeft.value === 300) { // 5 minutes
        emit('time-warning', timeLeft.value)
      } else if (timeLeft.value === 60) { // 1 minute
        emit('time-critical', timeLeft.value)
      } else if (timeLeft.value === 0) {
        emit('time-expired')
        stopTimer()
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}

const resetTimer = () => {
  stopTimer()
  timeLeft.value = props.timeLimit
}

// Watch for prop changes
watch(() => props.timeLimit, (newTimeLimit) => {
  timeLeft.value = newTimeLimit
})

watch(() => props.isActive, (isActive) => {
  if (isActive) {
    startTimer()
  } else {
    stopTimer()
  }
})

// Start timer if active on mount
onMounted(() => {
  if (props.isActive) {
    startTimer()
  }
})

// Cleanup on unmount
onUnmounted(() => {
  stopTimer()
})

// Expose methods for parent component
defineExpose({
  startTimer,
  stopTimer,
  resetTimer,
  timeLeft: computed(() => timeLeft.value)
})
</script>

<style scoped>
.timer-component {
  font-weight: bold;
  font-size: 18px;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.timer-component.normal {
  color: #2563eb;
  background: #eff6ff;
}

.timer-component.warning {
  color: #d97706;
  background: #fef3c7;
}

.timer-component.danger {
  color: #dc2626;
  background: #fee2e2;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.timer-label {
  margin-right: 8px;
}

.timer-value {
  font-family: 'Courier New', monospace;
  font-size: 20px;
}

/* Screen reader only class for accessibility */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Focus styles for accessibility */
.timer-component:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .timer-component.normal {
    border: 2px solid #2563eb;
  }
  
  .timer-component.warning {
    border: 2px solid #d97706;
  }
  
  .timer-component.danger {
    border: 2px solid #dc2626;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .timer-component.danger {
    animation: none;
  }
}

/* Tablet breakpoint */
@media (max-width: 768px) {
  .timer-component {
    font-size: 16px;
    padding: 8px 14px;
  }
  
  .timer-value {
    font-size: 18px;
  }
}

/* Mobile breakpoint */
@media (max-width: 480px) {
  .timer-component {
    font-size: 14px;
    padding: 6px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }
  
  .timer-label {
    margin-right: 0;
    font-size: 12px;
  }
  
  .timer-value {
    font-size: 20px;
  }
}

/* Extra small screens - compact mode */
@media (max-width: 360px) {
  .timer-component {
    padding: 4px 10px;
  }
  
  .timer-label {
    display: none;
  }
  
  .timer-value {
    font-size: 18px;
  }
}
</style>
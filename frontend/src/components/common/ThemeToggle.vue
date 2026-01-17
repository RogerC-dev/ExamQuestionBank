<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Tooltip } from 'bootstrap'

const theme = ref('light')

const tooltipRef = ref(null)
let tooltipInstance = null

// Computed tooltip text that changes based on current theme
const tooltipText = computed(() => {
  return theme.value === 'light' ? '切換深色模式' : '切換淺色模式'
})

const initTooltip = () => {
  if (!tooltipRef.value) return
  if (tooltipInstance) {
    tooltipInstance.dispose()
  }
  tooltipInstance = new Tooltip(tooltipRef.value, {
    title: tooltipText.value
  })
}

const updateTooltipContent = () => {
  if (tooltipInstance) {
    // Hide the tooltip first if it's showing
    tooltipInstance.hide()
    // Update the tooltip content using Bootstrap's API
    tooltipInstance.setContent({ '.tooltip-inner': tooltipText.value })
  }
}

const applyTheme = (value) => {
  document.documentElement.classList.toggle('dark', value === 'dark')
  document.documentElement.setAttribute('data-bs-theme', value)
}

onMounted(() => {
  // Check localStorage first, then system preference
  const stored = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const initial = stored || (prefersDark ? 'dark' : 'light')
  
  theme.value = initial
  applyTheme(initial)
  nextTick(initTooltip)
})

watch(theme, async () => {
  await nextTick()
  updateTooltipContent()
})

onBeforeUnmount(() => {
  if (tooltipInstance) {
    tooltipInstance.dispose()
    tooltipInstance = null
  }
})

const toggleTheme = () => {
  const next = theme.value === 'light' ? 'dark' : 'light'
  theme.value = next
  localStorage.setItem('theme', next)
  applyTheme(next)
}
</script>

<template>
  <button
    class="theme-toggle"
    ref="tooltipRef"
    data-bs-toggle="tooltip"
    data-bs-placement="bottom"
    @click="toggleTheme"
    :aria-label="theme === 'light' ? '切換深色模式' : '切換淺色模式'"
    :title="theme === 'light' ? '切換深色模式' : '切換淺色模式'"
  >
    <!-- Sun icon (light mode) -->
    <i v-if="theme === 'light'" class="bi bi-sun-fill"></i>
    <!-- Moon icon (dark mode) -->
    <i v-else class="bi bi-moon-fill"></i>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: var(--surface-muted);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: var(--primary-soft);
  color: var(--primary);
  transform: scale(1.05);
}

.theme-toggle i {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.theme-toggle:hover i {
  transform: rotate(15deg);
}
</style>

<style>
/* Global tooltip z-index override to appear above nav bar */
.tooltip {
  z-index: 2100 !important;
}
</style>


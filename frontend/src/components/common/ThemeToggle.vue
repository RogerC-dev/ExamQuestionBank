<script setup>
import { ref, onMounted } from 'vue'

const theme = ref('light')

onMounted(() => {
  // Check localStorage first, then system preference
  const stored = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const initial = stored || (prefersDark ? 'dark' : 'light')
  
  theme.value = initial
  document.documentElement.classList.toggle('dark', initial === 'dark')
})

const toggleTheme = () => {
  const next = theme.value === 'light' ? 'dark' : 'light'
  theme.value = next
  localStorage.setItem('theme', next)
  document.documentElement.classList.toggle('dark', next === 'dark')
}
</script>

<template>
  <button
    class="theme-toggle"
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

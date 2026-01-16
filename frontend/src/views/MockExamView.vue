<template>
  <div class="mock-exam-view">
    <h1>模擬測驗</h1>
    <div class="coming-soon">
      <p>AI 模擬測驗功能即將推出！</p>
      <p>此功能需要 AI Edge Function 支援，目前正在開發中。</p>
      <p style="margin-top: 1rem;">
        <router-link to="/exams" class="btn">前往一般考卷</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
// Mock exam feature requires AI Edge Function
</script>

<style scoped>
.mock-exam-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.coming-soon {
  text-align: center;
  padding: 3rem;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 8px;
  color: var(--text-secondary, #6b7280);
}
.btn {
  display: inline-block;
  padding: 10px 20px;
  background: var(--primary, #476996);
  color: white;
  border-radius: 6px;
  text-decoration: none;
}
</style>

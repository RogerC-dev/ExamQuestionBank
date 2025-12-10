<template>
  <div class="ai-chat-view">
    <div class="container">
      <div class="chat-container">
        <AIChatInterface />
      </div>
    </div>
  </div>
</template>

<script setup>
import AIChatInterface from '@/components/AIChatInterface.vue'
</script>

<style scoped>
.ai-chat-view {
  min-height: calc(100vh - 200px);
  padding: 24px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
}

.chat-container {
  height: 700px;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Tablet 平板 */
@media (max-width: 1024px) {
  .container {
    padding: 0 16px;
  }
  .chat-container {
    height: 650px;
  }
}

/* Mobile 手機 */
@media (max-width: 768px) {
  .ai-chat-view {
    padding: 12px 0;
  }
  .container {
    padding: 0 8px;
  }
  .chat-container {
    height: calc(100vh - 200px);
    border-radius: 8px;
  }
}

/* Small Mobile 小螢幕手機 */
@media (max-width: 480px) {
  .ai-chat-view {
    padding: 8px 0;
  }
  .container {
    padding: 0;
  }
  .chat-container {
    height: calc(100vh - 180px);
    border-radius: 0;
  }
}
</style>


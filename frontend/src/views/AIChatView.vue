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
}

@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 250px);
  }
}
</style>


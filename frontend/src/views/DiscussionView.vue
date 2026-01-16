<template>
  <div class="discussion-view">
    <h1>討論區</h1>
    <div class="coming-soon">
      <p>討論區功能即將推出！</p>
      <p>此功能需要後端支援，目前正在開發中。</p>
    </div>
  </div>
</template>

<script setup>
// Discussion feature is coming soon - needs backend implementation
</script>

<style scoped>
.discussion-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}
.coming-soon {
  text-align: center;
  padding: 3rem;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 8px;
  color: var(--text-secondary, #6b7280);
}
</style>

<template>
  <div class="gamification-dashboard">
    <h1>Gamification Dashboard</h1>
    <section class="xp">
      <h2>總經驗值</h2>
      <p>{{ store.totalXP }}</p>
    </section>
    <section>
      <h2>徽章</h2>
      <ul>
        <li v-for="badge in store.badges" :key="badge.id">
          <strong>{{ badge.name }}</strong> - {{ badge.description }}
        </li>
      </ul>
    </section>
    <section>
      <h2>我的徽章</h2>
      <ul>
        <li v-for="badge in store.userBadges" :key="badge.id">
          {{ badge.badge.name }} - {{ badge.awarded_at }}
        </li>
      </ul>
    </section>
    <section>
      <h2>學習小組</h2>
      <button @click="createGroup">建立小組</button>
      <ul>
        <li v-for="group in store.studyGroups" :key="group.id">
          {{ group.name }} ({{ group.members_count }}人)
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useGamificationStore } from '@/stores/gamificationStore'

const store = useGamificationStore()

onMounted(() => {
  store.loadDashboard()
})

const createGroup = async () => {
  const name = prompt('輸入小組名稱')
  if (name) {
    await store.createGroup({ name })
  }
}
</script>

<style scoped>
.gamification-dashboard {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}
section {
  margin-bottom: 1.5rem;
}
</style>


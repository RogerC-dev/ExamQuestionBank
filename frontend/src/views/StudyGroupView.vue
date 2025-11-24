<template>
  <div class="study-group-view">
    <h1>學習小組</h1>
    <ul>
      <li v-for="group in store.studyGroups" :key="group.id">
        <h2>{{ group.name }}</h2>
        <p>{{ group.description }}</p>
        <small>成員 {{ group.members_count }} / {{ group.max_members }}</small>
        <button @click="join(group.id)">加入</button>
        <button @click="leave(group.id)">退出</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useGamificationStore } from '@/stores/gamificationStore'

const store = useGamificationStore()

onMounted(() => {
  store.loadDashboard()
})

const join = async (id) => {
  await store.joinGroup(id)
  store.loadDashboard()
}

const leave = async (id) => {
  await store.leaveGroup(id)
  store.loadDashboard()
}
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
}
li {
  border: 1px solid #ddd;
  margin-bottom: 1rem;
  padding: 1rem;
}
</style>


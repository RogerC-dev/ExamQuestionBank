<template>
  <div class="discussion-view">
    <h1>討論區</h1>
    <section class="new-thread">
      <input v-model="form.title" placeholder="主題" />
      <textarea v-model="form.content" placeholder="分享你的想法..." />
      <button @click="createDiscussion" :disabled="loading">送出</button>
    </section>
    <section class="threads">
      <article v-for="discussion in discussions" :key="discussion.id">
        <header>
          <h2>{{ discussion.title }}</h2>
          <small>UP {{ discussion.upvotes }} / DOWN {{ discussion.downvotes }}</small>
        </header>
        <p>{{ discussion.content }}</p>
        <button @click="vote(discussion.id, 'up')">讚</button>
        <button @click="vote(discussion.id, 'down')">噓</button>
        <div class="reply">
          <textarea v-model="replyContent[discussion.id]" placeholder="回覆" />
          <button @click="reply(discussion.id)">回覆</button>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const discussions = ref([])
const loading = ref(false)
const form = ref({ title: '', content: '' })
const replyContent = ref({})

const loadDiscussions = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/discussions/')
    discussions.value = data
  } finally {
    loading.value = false
  }
}

const createDiscussion = async () => {
  if (!form.value.title || !form.value.content) return
  await api.post('/discussions/', form.value)
  form.value = { title: '', content: '' }
  loadDiscussions()
}

const vote = async (id, vote_type) => {
  await api.post(`/discussions/${id}/vote/`, { vote_type })
  loadDiscussions()
}

const reply = async (id) => {
  const content = replyContent.value[id]
  if (!content) return
  await api.post(`/discussions/${id}/reply/`, { title: `Re:${id}`, content })
  replyContent.value[id] = ''
  loadDiscussions()
}

onMounted(loadDiscussions)
</script>

<style scoped>
.discussion-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}
textarea {
  width: 100%;
}
article {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1rem;
}
</style>


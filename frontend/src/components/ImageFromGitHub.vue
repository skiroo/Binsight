<script setup>
import { ref, onMounted } from 'vue'

const images = ref([])
const loading = ref(false)
const error = ref(null)

const fetchImages = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('http://localhost:5000/api/github_images')
    const data = await res.json()
    if (data.error) throw new Error(data.error)
    images.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchImages)
</script>

<template>
  <div>
    <h2>Images GitHub</h2>
    <div v-if="loading">Chargement...</div>
    <div v-if="error" style="color:red">Erreur : {{ error }}</div>
    <div v-if="images.length === 0 && !loading && !error">Aucune image trouvée.</div>
    <div v-if="images.length > 0" style="display: flex; flex-wrap: wrap; gap: 20px;">
      <div v-for="(img, index) in images" :key="index">
        <img :src="img" :alt="img" style="max-width: 200px;" />
        <p>{{ img }}</p>
      </div>
    </div>
  </div>
</template>
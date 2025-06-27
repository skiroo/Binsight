<script setup>
import { ref, onMounted } from 'vue'

const images = ref([])

const fetchImages = async () => {
  const res = await fetch('http://localhost:5000/api/images')
  const data = await res.json()
  images.value = data.images
}

onMounted(fetchImages)
</script>

<template>
  <div>
    <h2>Carte Dynamique</h2>
    <div v-if="images.length">
      <div v-for="(img, i) in images" :key="i" style="margin-bottom: 1rem;">
        <img :src="`http://localhost:5000/static/uploads/${img.filename}`" width="100" />
        <p>{{ img.filename }} — {{ img.width }}x{{ img.height }} — {{ img.size_kb }} Ko</p>
        <p>Couleur moyenne : {{ img.mean_color }}</p>
      </div>
    </div>
    <p v-else>Chargement...</p>
  </div>
</template>
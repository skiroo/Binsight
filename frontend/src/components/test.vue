<script setup>
import { ref, onMounted } from 'vue'

const images = ref([])

onMounted(async () => {
  const res = await fetch('http://localhost:5000/api/images')
  const data = await res.json()
  images.value = data.images
})
</script>

<template>
  <div>
    <h2>Liste des images</h2>
    <table border="1">
      <thead>
        <tr>
          <th>Image</th>
          <th>Dimensions</th>
          <th>Taille (Ko)</th>
          <th>Couleur moyenne</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(img, index) in images" :key="index">
          <td><img :src="`http://localhost:5000/static/uploads/${img.filename}`" width="100" /></td>
          <td>{{ img.width }} × {{ img.height }}</td>
          <td>{{ img.size_kb }}</td>
          <td :style="{ backgroundColor: `rgb${img.mean_color}` }">{{ img.mean_color }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
table {
  border-collapse: collapse;
  margin-top: 1rem;
}
td, th {
  padding: 8px;
  text-align: center;
}
</style>
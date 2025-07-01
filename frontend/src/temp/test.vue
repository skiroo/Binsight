<script setup>
import { ref, onMounted } from 'vue'

const images = ref([])
const selectedFile = ref(null)
const message = ref('')

const fetchImages = async () => {
  try {
    const res = await fetch('http://localhost:5001/api/images')
    const data = await res.json()
    images.value = data.images
  } catch (error) {
    console.error('Erreur de chargement :', error)
  }
}

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const uploadImage = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('image', selectedFile.value)

  try {
    const res = await fetch('http://localhost:5001/', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      message.value = '✅ Upload réussi'
      await fetchImages()
    } else {
      message.value = '❌ Erreur serveur'
    }
  } catch (err) {
    message.value = 'Erreur réseau'
    console.error(err)
  }
}

onMounted(fetchImages)
</script>

<template>
  <div>
    <h2>Upload d’image</h2>
    <input type="file" @change="handleFileChange" accept="image/*"/>
    <button @click="uploadImage">Envoyer</button>
    <p>{{ message }}</p>

    <table v-if="images.length">
      <thead>
      <tr>
        <th>Image</th>
        <th>Dimensions</th>
        <th>Taille (Ko)</th>
        <th>Couleur</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(img, index) in images" :key="index">
        <td><img :src="`http://localhost:5001/static/uploads/${img.filename}`" width="100"/></td>
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
  margin-top: 1rem;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
  border: 1px solid #ccc;
}
</style>
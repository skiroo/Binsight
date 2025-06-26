<script setup>
import { ref } from 'vue'

const selectedFile = ref(null)
const message = ref('')

const handleFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

const uploadImage = async () => {
  if (!selectedFile.value) return
  const formData = new FormData()
  formData.append('image', selectedFile.value)

  const res = await fetch('http://localhost:5001/', {
    method: 'POST',
    body: formData
  })

  message.value = res.ok ? '✅ Image envoyée' : '❌ Erreur'
}
</script>

<template>
  <div>
    <h2>Uploader une image</h2>
    <input type="file" accept="image/*" @change="handleFileChange" />
    <button @click="uploadImage">Envoyer</button>
    <p>{{ message }}</p>
  </div>
</template>
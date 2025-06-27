<template>
  <div class="upload-container">
    <h2>Uploader une image</h2>

    <form @submit.prevent="uploadImage">
      <input type="file" @change="handleFileChange" accept="image/*" />
      <button type="submit">Envoyer</button>
    </form>

    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: "UploadPage",
  data() {
    return {
      selectedFile: null,
      message: "",
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadImage() {
      if (!this.selectedFile) {
        this.message = "Aucun fichier sélectionné.";
        return;
      }

      const formData = new FormData();
      formData.append("image", this.selectedFile);

      try {
        const response = await fetch("http://localhost:5000/upload", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        this.message = result.message || "Image envoyée avec succès.";
      } catch (error) {
        this.message = "Erreur lors de l’envoi.";
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
.upload-container {
  padding: 2rem;
  max-width: 600px;
  margin: auto;
}
input[type="file"] {
  margin-bottom: 1rem;
}
button {
  padding: 0.5rem 1rem;
}
</style>
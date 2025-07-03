<template>
  <div class="upload-container">
    <h2>Téléversement d'une image</h2>

    <!-- Upload image -->
    <input type="file" @change="handleImageUpload" accept="image/*" />

    <!-- Loader pendant le traitement -->
    <div v-if="loading">
      <p>Classification automatique en cours...</p>
      <div class="loader"></div>
    </div>

    <!-- Aperçu image -->
    <div v-if="imagePreview && !loading">
      <img :src="imagePreview" alt="Aperçu" class="preview" />
    </div>

    <!-- Affichage annotation actuelle -->
    <div v-if="etat && !loading">
      <p><strong>État :</strong> {{ etat === 'dirty' ? 'Pleine' : etat === 'clean' ? 'Vide' : 'Non défini' }}</p>
    </div>

    <!-- Choix manuel -->
    <div v-if="imageId && !loading">
      <label><input type="radio" value="dirty" v-model="etatAnnot" /> Pleine</label>
      <label><input type="radio" value="clean" v-model="etatAnnot" /> Vide</label>
    </div>

    <!-- Localisation -->
    <h3>Localisation</h3>
    <input v-model="localisation.rue_num" placeholder="Numéro de rue" />
    <input v-model="localisation.rue_nom" placeholder="Nom de rue" />
    <input v-model="localisation.cp" placeholder="Code postal" />
    <input v-model="localisation.ville" placeholder="Ville" />
    <input v-model="localisation.pays" placeholder="Pays" />

    <div id="map" style="height: 300px; margin-top: 10px;"></div>
    <p>Latitude : {{ localisation.lat }}, Longitude : {{ localisation.lon }}</p>

    <!-- Bouton de validation -->
    <button @click="submit" :disabled="loading || !image">Valider</button>

    <transition name="fade">
      <p v-if="message" class="success-msg">{{ message }}</p>
    </transition>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default {
  data() {
    return {
      image: null,
      imageId: null,
      imagePreview: null,
      etat: '',
      etatAnnot: '',
      message: '',
      loading: false,
      localisation: {
        rue_num: '',
        rue_nom: '',
        cp: '',
        ville: '',
        pays: '',
        lat: '',
        lon: ''
      },
      map: null,
      marker: null
    };
  },
  mounted() {
    this.initMap();
    this.getLocation();
  },
  methods: {
    handleImageUpload(e) {
      const file = e.target.files[0];
      if (!file) return;

      this.loading = true;
      this.image = file;
      this.imagePreview = URL.createObjectURL(file);
      this.imageId = null;
      this.etat = '';
      this.etatAnnot = '';

      const formData = new FormData();
      formData.append('image', file);
      formData.append('mode_classification', 'auto');

      fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          this.imageId = data.image_id;
          this.etat = data.classification_auto;
          this.etatAnnot = data.classification_auto;
        })
        .catch(err => {
          console.error('Erreur classification :', err);
          this.message = "Erreur lors de la classification.";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    submit() {
      if (!this.imageId || !this.etatAnnot) return;

      const payload = {
        etat: this.etatAnnot,
        localisation: this.localisation
      };

      fetch(`http://localhost:5000/update/${this.imageId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(data => {
          this.message = data.message || 'Annotation mise à jour';
          setTimeout(() => this.message = '', 4000);

          // Réinitialiser les champs
          this.image = null;
          this.imageId = null;
          this.imagePreview = null;
          this.etat = '';
          this.etatAnnot = '';
          this.localisation = {
            rue_num: '',
            rue_nom: '',
            cp: '',
            ville: '',
            pays: '',
            lat: '',
            lon: ''
          };
        })
        .catch(err => {
          console.error('Erreur :', err);
          this.message = 'Erreur lors de la mise à jour.';
        });
    },
    initMap() {
      this.map = L.map('map').setView([48.8566, 2.3522], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
      }).addTo(this.map);
      this.map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        this.localisation.lat = lat;
        this.localisation.lon = lng;
        if (this.marker) this.map.removeLayer(this.marker);
        this.marker = L.marker([lat, lng]).addTo(this.map);
      });
    },
    getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
          this.localisation.lat = position.coords.latitude;
          this.localisation.lon = position.coords.longitude;
        });
      }
    }
  }
};
</script>

<style scoped>
.upload-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
}
.preview {
  max-width: 100%;
  margin-top: 10px;
}
.success-msg {
  margin-top: 15px;
  color: green;
  font-weight: bold;
  text-align: center;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.loader {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 10px auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

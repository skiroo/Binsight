<template>
  <div class="upload-container">
    <h2>Téléversement d'une image</h2>

    <!-- Upload image ou prise de photo -->
    <input type="file" @change="handleImageUpload" accept="image/*" />
    <button @click="startCamera">Prendre une photo</button>
    <video ref="video" autoplay playsinline style="display:none; width: 100%; margin-top: 10px;"></video>
    <div v-if="cameraActive">
      <button @click="capturePhoto">Capturer</button>
      <button @click="stopCamera">Fermer la caméra</button>
    </div>
    <canvas ref="canvas" style="display:none;"></canvas>

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
    <input v-model="localisation.rue_nom" placeholder="Nom de rue" @input="fetchAddressSuggestions" />
    <ul v-if="suggestions.length" class="suggestions">
      <li v-for="(sug, index) in suggestions" :key="index" @click="applySuggestion(sug)">
        {{ sug.label }}
      </li>
    </ul>
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
      cameraActive: false,
      suggestions: [],
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
      this.processImage(file);
    },
    processImage(file) {
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
    startCamera() {
      this.cameraActive = true;
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          this.$refs.video.srcObject = stream;
          this.$refs.video.style.display = 'block';
        })
        .catch(err => {
          console.error("Erreur caméra :", err);
        });
    },
    stopCamera() {
      const stream = this.$refs.video.srcObject;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        this.$refs.video.srcObject = null;
        this.cameraActive = false;
        this.$refs.video.style.display = 'none';
      }
    },
    capturePhoto() {
      const video = this.$refs.video;
      const canvas = this.$refs.canvas;
      const context = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      canvas.toBlob(blob => {
        navigator.geolocation.getCurrentPosition(position => {
          this.localisation.lat = position.coords.latitude;
          this.localisation.lon = position.coords.longitude;

          const file = new File([blob], "captured.jpg", { type: "image/jpeg" });
          this.processImage(file);
        });

        this.stopCamera();
      }, "image/jpeg");
    },
    fetchAddressSuggestions() {
      if (this.localisation.rue_nom.length < 3) {
        this.suggestions = [];
        return;
      }
      fetch(`https://api-adresse.data.gouv.fr/search/?q=${this.localisation.rue_nom}`)
        .then(res => res.json())
        .then(data => {
          this.suggestions = data.features.map(f => ({
            label: f.properties.label,
            city: f.properties.city,
            postcode: f.properties.postcode,
            name: f.properties.name,
            number: f.properties.housenumber,
            lat: f.geometry.coordinates[1],
            lon: f.geometry.coordinates[0]
          }));
        });
    },
    applySuggestion(sug) {
      this.localisation.rue_nom = sug.name;
      this.localisation.rue_num = sug.number || '';
      this.localisation.ville = sug.city;
      this.localisation.cp = sug.postcode;
      this.localisation.lat = sug.lat;
      this.localisation.lon = sug.lon;
      this.localisation.pays = 'France';
      this.suggestions = [];
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
          this.suggestions = [];
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
  padding: 20px 15px;
  font-size: 0.95rem;
}

h2, h3 {
  margin-bottom: 12px;
  font-size: 1.4rem;
  text-align: center;
}

input[type="file"],
input,
button {
  font-family: inherit;
  font-size: 0.95rem;
}

input[type="file"] {
  margin-bottom: 12px;
}

input {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
  border-radius: 5px;
  border: 1px solid #ccc;
}

.preview {
  display: block;
  max-width: 100%;
  max-height: 220px;
  margin: 10px auto;
  border-radius: 6px;
  object-fit: contain;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.15);
}

.success-msg {
  margin-top: 10px;
  color: #10b981;
  font-weight: 600;
  text-align: center;
}

button {
  background-color: #10b981;
  color: white;
  padding: 6px 12px; /* ⬅️ réduit la taille */
  font-size: 0.9rem;  /* ⬅️ texte plus petit */
  border-radius: 5px;
  font-weight: 600;
  border: none;
  margin: 8px auto;
  display: block;
  cursor: pointer;
  transition: background-color 0.2s ease;
  max-width: 180px; /* optionnel : limite la largeur */
}

button:hover {
  background-color: #059669;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  animation: spin 0.8s linear infinite;
  margin: 15px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

#map {
  height: 240px;
  margin: 10px 0;
  border-radius: 8px;
  overflow: hidden;
}

p {
  text-align: center;
  margin-top: 8px;
  line-height: 1.3;
}

/* Mode sombre */
.dark-theme .upload-container {
  color: #f3f3f3;
}

.dark-theme input {
  background-color: #1f2937;
  border: 1px solid #374151;
  color: #f3f3f3;
}

.dark-theme button {
  background-color: #10b981;
  color: #fff;
}

.dark-theme button:hover {
  background-color: #059669;
}

.dark-theme #map {
  filter: brightness(0.85);
}

/* css pour suggestion adresse */
.suggestions {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ccc;
  background: white;
  max-height: 150px;
  overflow-y: auto;
}
.suggestions li {
  padding: 8px;
  cursor: pointer;
}
.suggestions li:hover {
  background-color: #f0f0f0;
}
</style>

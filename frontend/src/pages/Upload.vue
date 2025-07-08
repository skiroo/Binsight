<template>
  <div class="upload-container">
    <h2>{{ lang === 'fr' ? "Téléversement d'une image" : "Upload an image" }}</h2>

    <label for="groupe">Groupe de règles :</label>
    <select v-model="selectedGroupe" required>
      <option v-for="g in groupes" :key="g.id" :value="g.id">
        {{ g.nom }}
      </option>
    </select>

    <input type="file" @change="handleImageUpload" accept="image/*" />
    <div :class="['camera-toggle', { active: cameraActive }]" @click="toggleCamera">
      <img src="@/assets/camera.png" alt="Camera" />
    </div>

    <video ref="video" autoplay playsinline style="display:none; width: 100%; margin-top: 10px;"></video>
    <div v-if="cameraActive">
      <button @click="capturePhoto">{{ lang === 'fr' ? "Capturer" : "Capture" }}</button>
    </div>
    <canvas ref="canvas" style="display:none;"></canvas>

    <div v-if="loading">
      <p>{{ lang === 'fr' ? "Classification automatique en cours..." : "Automatic classification in progress..." }}</p>
      <div class="loader"></div>
    </div>

    <div v-if="imagePreview && !loading">
      <img :src="imagePreview" alt="Preview" class="preview" />
    </div>

    <div v-if="etat && !loading">
      <p>
        <strong>{{ lang === 'fr' ? "État" : "Status" }} :</strong>
        {{
          etat === 'dirty'
            ? lang === 'fr' ? 'Pleine' : 'Full'
            : etat === 'clean'
            ? lang === 'fr' ? 'Vide' : 'Empty'
            : lang === 'fr' ? 'Non défini' : 'Undefined'
        }}
      </p>
    </div>

    <div v-if="imageId && !loading">
      <label><input type="radio" value="dirty" v-model="etatAnnot" /> {{ lang === 'fr' ? "Pleine" : "Full" }}</label>
      <label><input type="radio" value="clean" v-model="etatAnnot" /> {{ lang === 'fr' ? "Vide" : "Empty" }}</label>
    </div>

    <h3>{{ lang === 'fr' ? "Adresse" : "Address" }}</h3>
    <input
      v-model="adresseComplete"
      :placeholder="lang === 'fr' ? 'Ex : 15 rue de Paris, 75000 Paris' : 'E.g. 15 rue de Paris, 75000 Paris'"
      @input="fetchAddressSuggestions"
    />
    <ul v-if="suggestions.length" class="suggestions">
      <li v-for="(sug, index) in suggestions" :key="index" @click="applySuggestion(sug)">
        {{ sug.label }}
      </li>
    </ul>

    <div id="map" style="height: 300px; margin-top: 10px;"></div>
    <p>Latitude : {{ localisation.lat }}, Longitude : {{ localisation.lon }}</p>

    <button @click="submit" :disabled="loading || !image">{{ lang === 'fr' ? "Valider" : "Submit" }}</button>

    <transition name="fade">
      <p v-if="message" class="success-msg">{{ message }}</p>
    </transition>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import API from '@/services/api';  // Assure-toi que ton API est configuré ici

export default {
  props: ['lang'],
  data() {
    return {
      groupes: [],
      selectedGroupe: null,
      image: null,
      imageId: null,
      imagePreview: null,
      etat: '',
      etatAnnot: '',
      message: '',
      loading: false,
      cameraActive: false,
      adresseComplete: '',
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
    this.loadRuleGroups();
    this.initMap();
    this.getLocation();
  },
  methods: {
    async loadRuleGroups() {
      try {
        const res = await API.get('/api/rule-groups');
        this.groupes = res.data;
        // Sélection automatique du groupe id=1 ou premier groupe dispo
        const defaultGroup = this.groupes.find(g => g.id === 1) || this.groupes[0];
        if (defaultGroup) {
          this.selectedGroupe = defaultGroup.id;
        }
      } catch (e) {
        console.error('Erreur chargement groupes de règles', e);
      }
    },
    handleImageUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      this.processImage(file);
    },
    async processImage(file) {
      this.message = '';

      if (this.imageId) {
        try {
          await fetch(`http://localhost:5000/delete_temp/${this.imageId}`, {
            method: 'DELETE'
          });
        } catch (err) {
          console.error('Erreur suppression image précédente :', err);
        }
      }

      this.loading = true;
      this.image = file;
      this.imagePreview = URL.createObjectURL(file);
      this.imageId = null;
      this.etat = '';
      this.etatAnnot = '';

      const formData = new FormData();
      const user = JSON.parse(localStorage.getItem('user'));
      formData.append('image', file);
      formData.append('mode_classification', 'auto');
      formData.append('utilisateur_id', user?.id || '');
      formData.append('source', user?.role || 'citoyen');

      // Ajout du groupe de règles choisi
      formData.append('groupe_id', this.selectedGroupe);

      fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          this.imageId = data.image_id;
          this.etat = data.classification_auto;
          this.etatAnnot = data.classification_auto;

          if (data.classification_auto === 'non déterminé') {
            this.message = this.lang === 'fr'
              ? 'Classification non déterminée. Veuillez annoter manuellement.'
              : 'Automatic classification failed. Please annotate manually.';
          } else {
            this.message = data.message || '';
          }
        })
        .catch(err => {
          console.error('Erreur classification :', err);
          this.message = this.lang === 'fr'
            ? "Erreur lors de la classification."
            : "Classification error.";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    toggleCamera() {
      if (this.cameraActive) {
        const stream = this.$refs.video?.srcObject;
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }
        this.$refs.video.srcObject = null;
        this.cameraActive = false;
        this.$refs.video.style.display = 'none';
      } else {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            this.$refs.video.srcObject = stream;
            this.$refs.video.style.display = 'block';
            this.cameraActive = true;
          })
          .catch(err => {
            console.error("Erreur caméra :", err);
          });
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
      if (this.adresseComplete.length < 3) {
        this.suggestions = [];
        return;
      }
      fetch(`https://api-adresse.data.gouv.fr/search/?q=${this.adresseComplete}`)
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
      this.adresseComplete = sug.label;
      this.suggestions = [];

      if (this.marker) this.map.removeLayer(this.marker);
      this.marker = L.marker([sug.lat, sug.lon]).addTo(this.map);
      this.map.setView([sug.lat, sug.lon], 17);
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
          this.message = data.message || (this.lang === 'fr' ? 'Annotation mise à jour' : 'Annotation updated');
          setTimeout(() => this.message = '', 4000);

          // Réinitialisation
          this.image = null;
          this.imageId = null;
          this.imagePreview = null;
          this.etat = '';
          this.etatAnnot = '';
          this.adresseComplete = '';
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
          this.message = this.lang === 'fr' ? 'Erreur lors de la mise à jour.' : 'Update error.';
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
    },
    stopCamera() {
      if (!this.cameraActive) return;
      const stream = this.$refs.video?.srcObject;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      this.$refs.video.srcObject = null;
      this.cameraActive = false;
      this.$refs.video.style.display = 'none';
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
/* Suggestions (input autocomplete) en mode sombre */
.dark-theme .leaflet-control-geocoder form input,
.dark-theme .autocomplete-suggestions,
.dark-theme .leaflet-geosearch-bar input,
.dark-theme .leaflet-geosearch-bar .suggestions {
  color: white !important;
  background-color: #1e1e1e !important;
  border-color: #444 !important;
}

.dark-theme .leaflet-geosearch-bar .suggestions > * {
  color: white !important;
  background-color: #2a2a2a !important;
  border-bottom: 1px solid #444;
}
.dark-theme .suggestions {
  background-color: #1f2937; /* fond sombre */
  color: #f3f3f3;            /* texte clair */
  border: 1px solid #374151;
}

.dark-theme .suggestions li {
  color: #f3f3f3;
}

.dark-theme .suggestions li:hover {
  background-color: #374151;
}

/* Prendre photo */
.camera-toggle {
  width: 60px;
  height: 60px;
  margin: 12px auto;
  border-radius: 50%;
  background-color: white;
  border: 2px solid #10b981;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.camera-toggle img {
  width: 32px;
  height: 32px;
}

.camera-toggle.active {
  background-color: #10b981;
}

.camera-active .camera-toggle {
  background-color: #10b981;
}

label[for="groupe"] {
  font-weight: 600;
  margin-bottom: 6px;
  display: inline-block;
  font-size: 1rem;
  color: inherit; /* hérite de la couleur du texte global */
}

select {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid #ccc; /* bordure grise claire au repos */
  border-radius: 8px;
  font-size: 1rem;
  color: inherit; /* texte couleur normale */
  background-color: white;
  outline: none;
  cursor: pointer;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

select:focus {
  border-color: #48bb78; /* bordure verte au focus */
  box-shadow: 0 0 5px #48bb78aa;
}

/* Mode sombre */
.dark-theme label[for="groupe"] {
  color: #e5e7eb;
}

.dark-theme select[v-model="selectedGroupe"] {
  background: #374151 url("data:image/svg+xml,%3csvg fill='none' stroke='%23e5e7eb' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3e%3cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3e%3c/path%3e%3c/svg%3e") no-repeat right 12px center / 1em auto;
  border: 1px solid #4b5563;
  color: #e5e7eb;
}

.dark-theme select[v-model="selectedGroupe"]:focus {
  border-color: #10b981;
  box-shadow: 0 0 5px #10b981aa;
}
</style>

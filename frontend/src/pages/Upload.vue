<template>
  <div class="upload-container">
    <h2>Téléversement d'une image</h2>

    <!-- Mode de classification -->
    <label for="mode">Mode de classification :</label>
    <select v-model="mode" id="mode">
      <option value="auto">Automatique</option>
      <option value="manuel">Manuel</option>
      <option value="ia">IA</option>
    </select>

    <!-- Upload image -->
    <input type="file" @change="handleImageUpload" accept="image/*" capture="environment" />

    <!-- Affichage image -->
    <div v-if="imagePreview">
      <img :src="imagePreview" alt="Aperçu de l'image" class="preview" />
    </div>

    <!-- Résultat de classification auto -->
    <div v-if="mode === 'auto' && autoAnnotation">
      <p>Classification automatique : <strong>{{ autoAnnotation }}</strong></p>
    </div>

    <!-- Annotation manuelle -->
    <div v-if="imagePreview">
      <label><input type="radio" value="pleine" v-model="annotation" /> Pleine</label>
      <label><input type="radio" value="vide" v-model="annotation" /> Vide</label>
    </div>

    <!-- Localisation texte -->
    <h3>Localisation</h3>
    <input v-model="localisation.rue_num" placeholder="Numéro de rue" />
    <input v-model="localisation.rue_nom" placeholder="Nom de rue" />
    <input v-model="localisation.cp" placeholder="Code postal" />
    <input v-model="localisation.ville" placeholder="Ville" />
    <input v-model="localisation.pays" placeholder="Pays" />

    <!-- Localisation par carte -->
    <div id="map" style="height: 300px; margin-top: 10px;"></div>
    <p>Latitude : {{ localisation.lat }}, Longitude : {{ localisation.lon }}</p>

    <!-- Bouton de validation -->
    <button @click="submit">Valider</button>

    <p v-if="annotationMsg">{{ annotationMsg }}</p>
  </div>
</template>

<script>
    import L from 'leaflet';
    import 'leaflet/dist/leaflet.css';

    export default {
        data() {
            return {
                mode: 'auto',
                image: null,
                imagePreview: null,
                autoAnnotation: '',
                annotation: '',
                annotationMsg: '',
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

                this.image = file;
                this.imagePreview = URL.createObjectURL(file);

                if (this.mode === 'auto') {
                    const formData = new FormData();
                    formData.append('image', file);
                    formData.append('mode_classification', this.mode);

                    fetch('http://localhost:5000/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(res => res.json())
                    .then(data => {
                        this.autoAnnotation = data.classification_auto || '';
                        this.annotation = this.autoAnnotation;
                    })
                    .catch(err => {
                        console.error("Erreur d'upload :", err);
                        this.autoAnnotation = 'Erreur';
                    });
                }
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
</style>

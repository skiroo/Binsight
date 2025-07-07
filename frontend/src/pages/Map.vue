<template>
  <div class="map-wrapper">
    <!-- Sidebar -->
    <div class="sidebar">
      <h3>{{ lang === 'fr' ? 'Filtres' : 'Filters' }}</h3>

      <label><b>{{ lang === 'fr' ? 'État' : 'Status' }} :</b></label><br />
      <label><input type="radio" value="all" v-model="filter" /> {{ lang === 'fr' ? 'Tous' : 'All' }}</label><br />
      <label><input type="radio" value="clean" v-model="filter" /> {{ lang === 'fr' ? 'Propres' : 'Clean' }}</label><br />
      <label><input type="radio" value="dirty" v-model="filter" /> {{ lang === 'fr' ? 'Pleines' : 'Full' }}</label><br /><br />

      <label><b>📍 {{ lang === 'fr' ? 'Quartier' : 'District' }} :</b></label><br />
      <input type="text" v-model="selectedArrondissement" list="arr-options" :placeholder="lang === 'fr' ? 'Ex: Paris 15e' : 'e.g., Paris 15'" />
      <datalist id="arr-options">
        <option v-for="a in arrondissements" :key="a" :value="a" />
      </datalist><br /><br />

      <label><b>{{ lang === 'fr' ? 'Date minimale' : 'Minimum date' }} :</b></label><br />
      <input type="date" v-model="dateMin" /><br /><br />

      <label><b>{{ lang === 'fr' ? 'Source' : 'Source' }} :</b></label><br />
      <select v-model="selectedSource">
        <option value="all">{{ lang === 'fr' ? 'Toutes' : 'All' }}</option>
        <option value="citoyen">{{ lang === 'fr' ? 'Citoyen' : 'Citizen' }}</option>
        <option value="agent">{{ lang === 'fr' ? 'Agent' : 'Agent' }}</option>
        <option value="caméra">{{ lang === 'fr' ? 'Caméra' : 'Camera' }}</option>
      </select><br /><br />

      <label><b>{{ lang === 'fr' ? 'Autour de (lat, lon + km)' : 'Around (lat, lon + km)' }} :</b></label><br />
      <input type="number" v-model="rayonLat" :placeholder="lang === 'fr' ? 'Latitude' : 'Latitude'" /><br />
      <input type="number" v-model="rayonLon" :placeholder="lang === 'fr' ? 'Longitude' : 'Longitude'" /><br />
      <input type="number" v-model="rayonKm" :placeholder="lang === 'fr' ? 'Rayon (km)' : 'Radius (km)'" /><br /><br />

      <button @click="recentrer">📍 {{ lang === 'fr' ? 'Ma position' : 'My position' }}</button>
    </div>

    <!-- Map -->
    <div class="map-container">
      <h1>{{ lang === 'fr' ? 'Carte des poubelles' : 'Bin Map' }}</h1>
      <div id="leaflet-map"></div>

      <div class="map-legend">
        <div><span class="legend-dot dirty"></span> {{ lang === 'fr' ? 'Pleine' : 'Full' }}</div>
        <div><span class="legend-dot clean"></span> {{ lang === 'fr' ? 'Vide' : 'Empty' }}</div>
      </div>

      <p class="map-count">
        🔢 {{ visibleCount }} {{ lang === 'fr' ? 'point(s) affiché(s)' : 'point(s) shown' }}
      </p>

      <div v-if="alertes.length > 0" class="alert-box">
        <h3>🚨 {{ lang === 'fr' ? 'Zones en alerte :' : 'Alert zones:' }}</h3>
        <ul>
          <li v-for="a in alertes" :key="a.quartier">
            {{ a.quartier }} : {{ a.nb_dirty }} {{ lang === 'fr' ? 'poubelles pleines' : 'full bins' }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { getLocalisations, getAlerts } from '@/services/api'

const props = defineProps({
  isDark: Boolean,
  lang: String
})

const filter = ref('all')
const selectedArrondissement = ref('all')
const selectedSource = ref('all')
const dateMin = ref(null)
const rayonLat = ref(null)
const rayonLon = ref(null)
const rayonKm = ref(null)
const arrondissements = ref([])
const visibleCount = ref(0)
const alertes = ref([])

let map = null
let markerGroup = null
let allPoints = []

function afficherPoints(points) {
  markerGroup.clearLayers()
  visibleCount.value = points.length

  points.forEach(p => {
    if (!p.latitude || !p.longitude) return
    const color = p.etat_annot === 'dirty' ? 'red' : 'green'
    const html = `<div style="text-align:center">
      <svg height="14" width="14"><circle cx="7" cy="7" r="7" fill="${color}" /></svg>
    </div>`
    const marker = L.marker([p.latitude, p.longitude], {
      icon: L.divIcon({ html, className: '' })
    }).bindPopup(`
      <b>${p.fichier_nom}</b><br>
      État : ${p.etat_annot}<br>
      Ville : ${p.ville || 'non spécifiée'}<br>
      Quartier : ${p.quartier || 'non spécifié'}<br>
      Source : ${p.source || 'inconnue'}
    `)
    markerGroup.addLayer(marker)
  })
}

function appliquerFiltres() {
  let filtrés = allPoints
  if (filter.value !== 'all') filtrés = filtrés.filter(p => p.etat_annot === filter.value)
  if (selectedArrondissement.value !== 'all' && selectedArrondissement.value.trim() !== '')
    filtrés = filtrés.filter(p => (p.quartier || p.ville || '').toLowerCase() === selectedArrondissement.value.toLowerCase())
  if (selectedSource.value !== 'all')
    filtrés = filtrés.filter(p => (p.source || '').toLowerCase() === selectedSource.value)
  if (dateMin.value)
    filtrés = filtrés.filter(p => p.date_upload && new Date(p.date_upload) >= new Date(dateMin.value))
  if (rayonLat.value && rayonLon.value && rayonKm.value) {
    const R = 6371
    filtrés = filtrés.filter(p => {
      const dLat = (p.latitude - rayonLat.value) * Math.PI / 180
      const dLon = (p.longitude - rayonLon.value) * Math.PI / 180
      const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(p.latitude * Math.PI / 180) * Math.cos(rayonLat.value * Math.PI / 180) *
        Math.sin(dLon / 2) ** 2
      const d = 2 * R * Math.asin(Math.sqrt(a))
      return d <= rayonKm.value
    })
  }
  afficherPoints(filtrés)
  verifierAlertes()
}

async function verifierAlertes() {
  try {
    const res = await getAlerts()
    alertes.value = res.data.alertes || []
  } catch (err) {
    console.error("Erreur lors du chargement des alertes :", err)
  }
}

watch([filter, selectedArrondissement, selectedSource, dateMin, rayonLat, rayonLon, rayonKm], appliquerFiltres)

function recentrer() {
  if (!navigator.geolocation) return alert("Géolocalisation non supportée.")
  navigator.geolocation.getCurrentPosition(
    pos => map.setView([pos.coords.latitude, pos.coords.longitude], 14),
    err => alert("Impossible d'obtenir votre position.")
  )
}

onMounted(async () => {
  map = L.map('leaflet-map').setView([48.8566, 2.3522], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)
  markerGroup = L.markerClusterGroup()
  map.addLayer(markerGroup)
  const response = await getLocalisations()
  allPoints = response.data
  const raw = allPoints.map(p => p.quartier || p.ville || '').filter(Boolean)
  arrondissements.value = [...new Set(raw)].sort()
  appliquerFiltres()
})
</script>


<style scoped>
.map-wrapper {
  display: flex;
  gap: 20px;
  padding: 20px;
  flex-wrap: wrap;
}

.sidebar {
  width: 220px;
  padding: 15px;
  border-radius: 10px;
  flex-shrink: 0;
  border: 1px solid #444;
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text);
  font-size: 14px;
}

.sidebar h3 {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: bold;
}

.sidebar label {
  display: block;
  margin: 6px 0 2px;
  font-weight: 600;
}

.sidebar input,
.sidebar select,
.sidebar button {
  width: 100%;
  padding: 6px 8px;
  font-size: 13px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid var(--input-border);
  background-color: var(--input-bg);
  color: var(--input-text);
  box-sizing: border-box;
}

.sidebar input[type="radio"] {
  width: auto;
  margin-right: 6px;
  accent-color: var(--accent-color);
}

.sidebar button {
  background-color: var(--btn-bg);
  color: var(--btn-text);
  border: 1px solid var(--btn-border);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.sidebar button:hover {
  background-color: var(--btn-hover);
}

:root {
  --sidebar-bg: #ffffff;
  --sidebar-text: #000;
  --input-bg: #ffffff;
  --input-text: #000;
  --input-border: #ccc;
  --btn-bg: #f0f0f0;
  --btn-text: #000;
  --btn-border: #bbb;
  --btn-hover: #e0e0e0;
  --accent-color: #10b981;
}

body.dark-theme {
  --sidebar-bg: #101010;
  --sidebar-text: #f5f5f5;
  --input-bg: #1f1f1f;
  --input-text: #f5f5f5;
  --input-border: #555;
  --btn-bg: #2a2a2a;
  --btn-text: #fff;
  --btn-border: #444;
  --btn-hover: #3a3a3a;
  --accent-color: #10b981;
}

input, select, button {
  width: 100%;
  padding: 6px 10px;
  margin-bottom: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: var(--input-bg);
  color: var(--input-text);
}

input[type="radio"] {
  width: auto;
  margin-right: 5px;
  accent-color: var(--accent-color);
}

button {
  cursor: pointer;
  border: 1px solid var(--btn-border);
  background-color: var(--btn-bg);
  color: var(--btn-text);
  transition: background-color 0.2s ease;
}

button:hover {
  background-color: var(--btn-hover);
}

:root {
  --sidebar-bg: #ffffff;
  --sidebar-text: #000;
  --input-bg: #ffffff;
  --input-text: #000;
  --btn-bg: #f5f5f5;
  --btn-text: #000;
  --btn-border: #ccc;
  --btn-hover: #e0e0e0;
  --accent-color: #10b981;
}

body.dark-theme {
  --sidebar-bg: #1a1a1a;
  --sidebar-text: #f5f5f5;
  --input-bg: #2a2a2a;
  --input-text: #f5f5f5;
  --btn-bg: #333;
  --btn-text: #fff;
  --btn-border: #555;
  --btn-hover: #444;
  --accent-color: #10b981;
}

.map-container {
  flex: 1;
  min-width: 300px;
  text-align: center;
}

#leaflet-map {
  height: 600px;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  margin-bottom: 10px;
}

.map-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 14px;
  margin-top: 5px;
}

.legend-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}

.legend-dot.dirty {
  background-color: red;
}

.legend-dot.clean {
  background-color: green;
}

.map-count {
  font-size: 14px;
  color: var(--sidebar-text);
}

.alert-box {
  background: #ffe0e0;
  color: #900;
  padding: 12px;
  border-radius: 10px;
  margin-top: 10px;
  text-align: left;
  max-width: 400px;
  margin-inline: auto;
}
</style>

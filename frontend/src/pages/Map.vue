<template>
  <div class="map-wrapper">
    <div class="sidebar">
      <h3>{{ lang === 'fr' ? 'Filtres' : 'Filters' }}</h3>

      <!-- État -->
      <label><b>{{ lang === 'fr' ? 'État' : 'Status' }} :</b></label>
      <div class="etat-filters">
        <button :class="{ active: filter === 'all' }" @click="setFilter('all')">{{ lang === 'fr' ? 'Tous' : 'All' }}</button>
        <button :class="{ active: filter === 'clean' }" @click="setFilter('clean')">{{ lang === 'fr' ? 'Propres' : 'Clean' }}</button>
        <button :class="{ active: filter === 'dirty' }" @click="setFilter('dirty')">{{ lang === 'fr' ? 'Pleines' : 'Full' }}</button>
      </div>

      <!-- Source -->
      <label><b>{{ lang === 'fr' ? 'Source' : 'Source' }} :</b></label>
      <div class="source-filters">
        <button :class="{ active: selectedSource === 'all' }" @click="setSource('all')">{{ lang === 'fr' ? 'Toutes' : 'All' }}</button>
        <button :class="{ active: selectedSource === 'citoyen' }" @click="setSource('citoyen')">{{ lang === 'fr' ? 'Citoyen' : 'Citizen' }}</button>
        <button :class="{ active: selectedSource === 'agent' }" @click="setSource('agent')">{{ lang === 'fr' ? 'Agent' : 'Agent' }}</button>
      </div>

      <!-- Quartier -->
      <label><b>{{ lang === 'fr' ? 'Quartier' : 'District' }} :</b></label>
      <div class="quartier-wrapper">
        <input
          type="text"
          v-model="selectedArrondissementInput"
          class="quartier-input"
          :placeholder="lang === 'fr' ? 'Ex: Paris 15e' : 'e.g., Paris 15'"
          @input="updateSuggestions"
          @blur="hideSuggestionsWithDelay"
          @focus="showSuggestions = selectedArrondissementInput.length >= 2"
        />
        <ul v-if="showSuggestions" class="suggestion-list">
          <li v-for="a in arrondissementSuggestions" :key="a" @mousedown.prevent="selectSuggestion(a)">{{ a }}</li>
        </ul>
      </div>
      <button class="reset-button" @click="resetDistrict">{{ lang === 'fr' ? 'Réinitialiser le quartier' : 'Reset district' }}</button>

      <!-- Dates -->
      <label><b>{{ lang === 'fr' ? 'Du' : 'From' }} :</b></label>
      <input type="date" v-model="dateMin" />
      <label><b>{{ lang === 'fr' ? 'Au' : 'To' }} :</b></label>
      <input type="date" v-model="dateMax" />

      <label><b>{{ lang === 'fr' ? 'Dates rapides' : 'Quick dates' }} :</b></label>
      <div class="date-filters">
        <button :class="{ active: dateRange === 'today' }" @click="setDateRange('today')">{{ lang === 'fr' ? 'Aujourd\'hui' : 'Today' }}</button>
        <button :class="{ active: dateRange === '7d' }" @click="setDateRange('7d')">{{ lang === 'fr' ? '7 jours' : '7 days' }}</button>
        <button :class="{ active: dateRange === 'month' }" @click="setDateRange('month')">{{ lang === 'fr' ? 'Ce mois' : 'This month' }}</button>
      </div>
      <button class="reset-button" @click="resetDateFilters">{{ lang === 'fr' ? 'Réinitialiser les dates' : 'Reset dates' }}</button>

      <!-- Coordonnées -->
      <label><b>{{ lang === 'fr' ? 'Autour de' : 'Around' }} :</b></label>
      <input type="number" v-model="rayonLat" :placeholder="lang === 'fr' ? 'Latitude' : 'Latitude'" disabled />
      <input type="number" v-model="rayonLon" :placeholder="lang === 'fr' ? 'Longitude' : 'Longitude'" disabled />
      <input type="number" v-model="rayonKm" :placeholder="lang === 'fr' ? 'Rayon (km)' : 'Radius (km)'" />
      <button class="reset-button" @click="resetCoordFilters">{{ lang === 'fr' ? 'Réinitialiser les coordonnées' : 'Reset coordinates' }}</button>

      <button @click="recentrer">📍 {{ lang === 'fr' ? 'Ma position' : 'My position' }}</button>

        <!-- Réinitialiser tous -->
        <button class="reset-button" @click="resetAllFilters" style="margin-top: 10px; font-weight: bold;">
            {{ lang === 'fr' ? 'Réinitialiser tous les filtres' : 'Reset all filters' }}
        </button>
    </div>

    <!-- Carte -->
    <div class="map-container">
      <h1>{{ lang === 'fr' ? 'Carte des poubelles' : 'Bin Map' }}</h1>
      <div id="leaflet-map"></div>

      <div class="map-legend">
        <div><span class="legend-dot dirty"></span> {{ lang === 'fr' ? 'Pleine' : 'Full' }}</div>
        <div><span class="legend-dot clean"></span> {{ lang === 'fr' ? 'Vide' : 'Empty' }}</div>
      </div>

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

const props = defineProps({ isDark: Boolean, lang: String })

// Reactive states
const filter = ref('all')
const selectedSource = ref('all')
const selectedArrondissementInput = ref('')
const dateMin = ref(null)
const dateMax = ref(null)
const dateRange = ref(null)
const rayonLat = ref(null)
const rayonLon = ref(null)
const rayonKm = ref(null)
const arrondissements = ref([])
const arrondissementSuggestions = ref([])
const showSuggestions = ref(false)
const visibleCount = ref(0)
const alertes = ref([])

// Map and markers
let map = null
let markerGroup = null
let allPoints = []
let rayonCircle = null

function afficherPoints(points) {
  markerGroup.clearLayers()
  visibleCount.value = points.length

  points.forEach(p => {
    if (!p.latitude || !p.longitude) return

    const color = p.etat_annot === 'dirty' ? 'orangered' : 'green'
    const html = `<svg height="14" width="14"><circle cx="7" cy="7" r="7" fill="${color}" /></svg>`

    const marker = L.marker([p.latitude, p.longitude], {
      icon: L.divIcon({ html, className: '' })
    })

    const popupContent = `
      <b>${p.fichier_nom}</b><br>
      État : ${p.etat_annot}<br>
      Ville : ${p.ville || 'non spécifiée'}<br>
      Quartier : ${p.quartier || 'non spécifié'}<br>
      Source : ${p.source || 'inconnue'}`

    marker.bindPopup(popupContent)

    marker.on('click', (e) => {
      rayonLat.value = p.latitude
      rayonLon.value = p.longitude
      updateRayonCircle()
      L.popup().setLatLng(e.latlng).setContent(popupContent).openOn(map)
      appliquerFiltres()
    })

    markerGroup.addLayer(marker)
  })
}

function appliquerFiltres() {
  let filtrés = allPoints
  if (filter.value !== 'all') filtrés = filtrés.filter(p => p.etat_annot === filter.value)

  const arrInput = selectedArrondissementInput.value.trim().toLowerCase()
  if (arrInput) filtrés = filtrés.filter(p => (p.quartier || p.ville || '').toLowerCase().includes(arrInput))

  if (selectedSource.value !== 'all') filtrés = filtrés.filter(p => (p.source || '').toLowerCase() === selectedSource.value)
  if (dateMin.value) filtrés = filtrés.filter(p => p.date_upload && new Date(p.date_upload) >= new Date(dateMin.value))
  if (dateMax.value) filtrés = filtrés.filter(p => p.date_upload && new Date(p.date_upload) <= new Date(dateMax.value))

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

function updateRayonCircle() {
  if (rayonLat.value && rayonLon.value && rayonKm.value) {
    if (rayonCircle) map.removeLayer(rayonCircle)
    rayonCircle = L.circle([rayonLat.value, rayonLon.value], {
      radius: rayonKm.value * 1000,
      color: '#10b981',
      weight: 2,
      fillOpacity: 0.1
    }).addTo(map)
  }
}

function setDateRange(type) {
  const today = new Date()
  const past = new Date()
  dateRange.value = type

  if (type === 'today') {
    dateMin.value = dateMax.value = today.toISOString().split('T')[0]
  } else if (type === '7d') {
    past.setDate(today.getDate() - 6)
    dateMin.value = past.toISOString().split('T')[0]
    dateMax.value = today.toISOString().split('T')[0]
  } else if (type === 'month') {
    past.setDate(1)
    dateMin.value = past.toISOString().split('T')[0]
    dateMax.value = today.toISOString().split('T')[0]
  }
}

function resetDateFilters() {
  dateMin.value = dateMax.value = dateRange.value = null
}

function resetCoordFilters() {
  rayonLat.value = rayonLon.value = rayonKm.value = null
  if (rayonCircle) map.removeLayer(rayonCircle)
  appliquerFiltres()
}

function selectSuggestion(val) {
  selectedArrondissementInput.value = val
  showSuggestions.value = false
  appliquerFiltres()
}

function hideSuggestionsWithDelay() {
  setTimeout(() => showSuggestions.value = false, 200)
}

function updateSuggestions() {
  if (selectedArrondissementInput.value.length >= 2) {
    const input = selectedArrondissementInput.value.toLowerCase()
    arrondissementSuggestions.value = arrondissements.value.filter(a => a.toLowerCase().includes(input)).slice(0, 10)
    showSuggestions.value = true
  } else {
    showSuggestions.value = false
  }
}

function resetDistrict() {
  selectedArrondissementInput.value = ''
  appliquerFiltres()
}

function setFilter(val) { filter.value = val }
function setSource(val) { selectedSource.value = val }

async function verifierAlertes() {
  try {
    const res = await getAlerts()
    alertes.value = res.data.alertes || []
  } catch (err) {
    console.error("Erreur lors du chargement des alertes :", err)
  }
}

function resetAllFilters() {
  filter.value = 'all'
  selectedSource.value = 'all'
  selectedArrondissementInput.value = ''
  dateMin.value = null
  dateMax.value = null
  dateRange.value = null
  rayonLat.value = null
  rayonLon.value = null
  rayonKm.value = null
  if (rayonCircle) map.removeLayer(rayonCircle)
  appliquerFiltres()
}

watch([
  filter, selectedSource, selectedArrondissementInput,
  dateMin, dateMax, rayonLat, rayonLon, rayonKm
], appliquerFiltres)

watch(rayonKm, updateRayonCircle)

function recentrer() {
  if (!navigator.geolocation) return alert("Géolocalisation non supportée.")
  navigator.geolocation.getCurrentPosition(
    pos => map.setView([pos.coords.latitude, pos.coords.longitude], 14),
    () => alert("Impossible d'obtenir votre position.")
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

.sidebar label,
.sidebar input,
.sidebar select,
.sidebar button {
  display: block;
  width: 100%;
  font-size: 13px;
  margin-bottom: 8px;
  border-radius: 6px;
  box-sizing: border-box;
}

.sidebar label {
  margin: 6px 0 2px;
  font-weight: 600;
}

.sidebar input,
.sidebar select,
.sidebar button {
  padding: 6px 8px;
  border: 1px solid var(--input-border);
  background-color: var(--input-bg);
  color: var(--input-text);
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

.legend-dot.dirty { background-color: orangered; }
.legend-dot.clean { background-color: green; }

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

.etat-filters,
.source-filters,
.date-filters {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
}

.etat-filters button,
.source-filters button,
.date-filters button {
  flex: 1;
  background: white;
  color: black;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.etat-filters button.active,
.source-filters button.active,
.date-filters button.active {
  background-color: #16a085;
  color: white;
  font-weight: bold;
}

.quartier-wrapper {
  position: relative;
}

.quartier-input {
  width: 100%;
  padding: 6px 8px;
  font-size: 13px;
  border-radius: 6px;
  border: 1px solid var(--input-border);
  background-color: var(--input-bg);
  color: var(--input-text);
}

.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 2px 0 0;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  background-color: #fff;
  color: #000;
  max-height: 180px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: absolute;
  width: 100%;
  z-index: 10;
}

.suggestion-list li {
  padding: 8px 10px;
  cursor: pointer;
  color: var(--input-text);
  transition: background-color 0.2s;
}

.suggestion-list li:hover {
  background-color: var(--btn-hover);
  font-weight: bold;
}

:root {
  --sidebar-bg: #ffffff;
  --sidebar-text: #000;
  --input-bg: #ffffff;
  --input-text: #000;
  --input-border: #ccc;
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
  --input-border: #555;
  --btn-bg: #333;
  --btn-text: #fff;
  --btn-border: #555;
  --btn-hover: #444;
  --accent-color: #10b981;
}

</style>
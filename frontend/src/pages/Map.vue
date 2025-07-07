<template>
  <div class="map-wrapper">
    <!-- Barre latérale -->
    <div class="sidebar">
      <h3>Filtres</h3>
      <label><input type="radio" value="all" v-model="filter" /> Tous</label><br />
      <label><input type="radio" value="clean" v-model="filter" /> Propres</label><br />
      <label><input type="radio" value="dirty" v-model="filter" /> Pleines</label><br />

      <br />
      <label><b>Arrondissement :</b></label><br />
      <select v-model="selectedArrondissement">
        <option value="all">Tous</option>
        <option v-for="a in arrondissements" :key="a" :value="a">{{ a }}</option>
      </select>

      <br /><br />
      <button @click="recentrer">📍 Ma position</button>
    </div>

    <!-- Carte -->
    <div class="map-container">
      <h1>Carte des poubelles</h1>
      <div id="leaflet-map"></div>

      <div class="map-legend">
        <div><span class="legend-dot dirty"></span> Pleine</div>
        <div><span class="legend-dot clean"></span> Vide</div>
      </div>

      <p class="map-count">
        🔢 {{ visibleCount }} point{{ visibleCount === 1 ? '' : 's' }} affiché{{ visibleCount > 1 ? 's' : '' }}
      </p>
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
import { getLocalisations } from '@/services/api'

const map = ref(null)
const markerGroup = ref(null)
const filter = ref('all')
const selectedArrondissement = ref('all')
const arrondissements = ref([])
const visibleCount = ref(0)

const weatherCache = {}
let allPoints = []

function emojiTemp(temp) {
  return temp !== '--' ? `${temp}°C` : 'N/A'
}

async function getWeather(lat, lon) {
  const key = `${lat.toFixed(4)},${lon.toFixed(4)}`
  if (weatherCache[key]) return weatherCache[key]

  const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`)
  const j = await res.json()
  const w = j.current_weather || {}
  const temp = w.temperature !== undefined ? w.temperature : '--'
  weatherCache[key] = { temp }
  return weatherCache[key]
}

function afficherPoints(points) {
  markerGroup.value.clearLayers()
  visibleCount.value = points.length

  points.forEach(async p => {
    if (!p.latitude || !p.longitude) return

    const w = await getWeather(p.latitude, p.longitude)
    const emoji = emojiTemp(w.temp)
    const color = p.etat_annot === 'dirty' ? 'red' : 'green'

    const html = `
      <div style="text-align:center">
        <svg height="14" width="14"><circle cx="7" cy="7" r="7" fill="${color}" /></svg>
        <div style="font-size:11px">${emoji}</div>
      </div>`

    const marker = L.marker([p.latitude, p.longitude], {
      icon: L.divIcon({ html, className: '' })
    }).bindPopup(`
      <b>${p.fichier_nom}</b><br>
      État : ${p.etat_annot}<br>
      Météo : ${emoji}
    `)

    markerGroup.value.addLayer(marker)
  })
}

function appliquerFiltres() {
  let filtrés = filter.value === 'all'
    ? allPoints
    : allPoints.filter(p => p.etat_annot === filter.value)

  if (selectedArrondissement.value !== 'all') {
    filtrés = filtrés.filter(p =>
      (p.quartier || p.ville || '').toLowerCase() === selectedArrondissement.value.toLowerCase()
    )
  }

  afficherPoints(filtrés)
}

watch([filter, selectedArrondissement], appliquerFiltres)

function recentrer() {
  if (!navigator.geolocation) return alert("Géolocalisation non supportée.")
  navigator.geolocation.getCurrentPosition(
    pos => map.value.setView([pos.coords.latitude, pos.coords.longitude], 14),
    err => alert("Impossible d'obtenir votre position.")
  )
}

onMounted(async () => {
  map.value = L.map('leaflet-map').setView([48.8566, 2.3522], 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  markerGroup.value = L.markerClusterGroup()
  map.value.addLayer(markerGroup.value)

  const response = await getLocalisations()
  allPoints = response.data

  // Extraire les arrondissements uniques
  const raw = response.data.map(p => p.quartier || p.ville || '').filter(Boolean)
  arrondissements.value = [...new Set(raw)].sort()

  appliquerFiltres()
})
</script>

<style scoped>
.map-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  flex-wrap: wrap;
}

.sidebar {
  width: 200px;
  background: #f2f2f2;
  padding: 20px;
  border-radius: 10px;
  flex-shrink: 0;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
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
  margin-top: 5px;
  font-size: 14px;
  color: #333;
}
</style>

<template>
  <div class="map-wrapper">
    <!-- Barre latérale -->
    <div :class="['sidebar', isDarkMode ? 'sidebar-dark' : 'sidebar-light']">
      <h3>Filtres</h3>

      <label><b>État :</b></label><br />
      <label><input type="radio" value="all" v-model="filter" /> Tous</label><br />
      <label><input type="radio" value="clean" v-model="filter" /> Propres</label><br />
      <label><input type="radio" value="dirty" v-model="filter" /> Pleines</label><br /><br />

      <label><b>📍 Quartier :</b></label><br />
      <input type="text" v-model="selectedArrondissement" list="arr-options" placeholder="Ex: Paris 15e" />
      <datalist id="arr-options">
        <option v-for="a in arrondissements" :key="a" :value="a" />
      </datalist><br /><br />

      <label><b>Date minimale :</b></label><br />
      <input type="date" v-model="dateMin" /><br /><br />

      <label><b>Source :</b></label><br />
      <select v-model="selectedSource">
        <option value="all">Toutes</option>
        <option value="citoyen">Citoyen</option>
        <option value="agent">Agent</option>
        <option value="caméra">Caméra</option>
      </select><br /><br />

      <label><b>Autour de (lat, lon + km) :</b></label><br />
      <input type="number" v-model="rayonLat" placeholder="Latitude" /><br />
      <input type="number" v-model="rayonLon" placeholder="Longitude" /><br />
      <input type="number" v-model="rayonKm" placeholder="Rayon (km)" /><br /><br />

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

      <div v-if="alertes.length > 0" class="alert-box">
        <h3>🚨 Zones en alerte :</h3>
        <ul>
          <li v-for="a in alertes" :key="a.quartier">
            {{ a.quartier }} : {{ a.nb_dirty }} poubelles pleines
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

const isDarkMode = ref(document.body.classList.contains("dark-mode"))

const observer = new MutationObserver(() => {
  isDarkMode.value = document.body.classList.contains("dark-mode")
})

onMounted(() => {
  observer.observe(document.body, { attributes: true, attributeFilter: ["class"] })
})

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
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  flex-wrap: wrap;
}

.sidebar {
  width: 220px;
  padding: 20px;
  border-radius: 10px;
  flex-shrink: 0;
  border: 1px solid #ddd;
}

.sidebar-light {
  background-color: #ffffff;
  color: #000000;
}

.sidebar-light input,
.sidebar-light select {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #ccc;
}

.sidebar-light button {
  background-color: #f5f5f5;
  color: #000000;
  border: 1px solid #bbb;
  padding: 6px 12px;
  cursor: pointer;
}

.sidebar-dark {
  background-color: #121212;
  color: #eeeeee;
  border: 1px solid #2a2a2a;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.sidebar-dark input,
.sidebar-dark select {
  background-color: #1e1e1e;
  color: #f5f5f5;
  border: 1px solid #444;
  padding: 6px 10px;
  border-radius: 6px;
}

.sidebar-dark input::placeholder {
  color: #888;
}

.sidebar-dark button {
  background-color: #2b2b2b;
  color: #fff;
  border: 1px solid #555;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.sidebar-dark button:hover {
  background-color: #3a3a3a;
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

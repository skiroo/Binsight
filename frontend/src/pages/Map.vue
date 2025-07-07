<template>
  <div class="dashboard-container">
    <div class="sidebar">
      <h2>Filtres & Statistiques</h2>
      <div class="filter-group">
        <label>Quartier</label>
        <select v-model="filters.quartier">
          <option value="">Tous</option>
          <option v-for="q in quartiers" :key="q">{{ q }}</option>
        </select>

        <label>Date</label>
        <input type="date" v-model="filters.date" />

        <label>État</label>
        <select v-model="filters.etat">
          <option value="">Tous</option>
          <option value="dirty">Pleine</option>
          <option value="clean">Vide</option>
        </select>
      </div>

      <div class="stats">
        <p>Total : {{ stats.total }}</p>
        <p>Pleines : {{ stats.dirtyPercent }} %</p>
        <p>Annotées : {{ stats.annotatedPercent }} %</p>
        <p>Photos récentes : {{ stats.recent }}</p>
      </div>

      <div class="context">
        <h3>Contexte</h3>
        <p>Météo : {{ weather.desc }}, {{ weather.temp }} °C</p>
        <p>Jour de marché ? 🛒 {{ isMarketDay ? 'Oui' : 'Non' }}</p>
        <p>Prochaine collecte : {{ nextCollection }}</p>
      </div>
    </div>

    <div class="map-container">
      <h1>Carte des poubelles annotées</h1>
      <div id="leaflet-map"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Cartographie
const map = ref(null)
const markers = ref([])
const data = ref([])
const quartiers = ref([])
const filters = ref({ quartier: '', date: '', etat: '' })
const stats = ref({ total: 0, dirtyPercent: 0, annotatedPercent: 0, recent: 0 })

// Contexte
const weather = ref({ desc: '...', temp: '--' })
const isMarketDay = ref(false)
const nextCollection = ref('...')

// Bug icônes Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

// Jour de marché par arrondissement (ex)
// Paris principalement les mercredis/samedis
const marketDays = {
  '1er': ['mercredi', 'samedi'],
  '2e': ['jeudi', 'samedi'],
  '3e': ['mardi', 'vendredi'],
  // etc.
}

// Jours de collecte fictifs
const collectionDays = {
  '1er': 'Lundi, Jeudi',
  '2e': 'Mardi, Vendredi',
  '3e': 'Mercredi, Samedi',
  // etc.
}

function computeContext() {
  if (filters.value.quartier) {
    const arr = filters.value.quartier
    const today = new Date().toLocaleDateString('fr-FR', { weekday: 'long' })
    isMarketDay.value = (marketDays[arr] || []).includes(today)
    nextCollection.value = collectionDays[arr] || 'N/A'
  } else {
    isMarketDay.value = false
    nextCollection.value = 'Sélectionner un quartier'
  }
}

const updateMap = () => {
  markers.value.forEach(m => map.value.removeLayer(m))
  markers.value = []

  const filtered = data.value.filter(p => {
    return (!filters.value.quartier || p.arrondissement === filters.value.quartier) &&
           (!filters.value.date || p.date_upload?.startsWith(filters.value.date)) &&
           (!filters.value.etat || p.etat_annot === filters.value.etat)
  })

  filtered.forEach(point => {
    const m = L.circleMarker([point.latitude, point.longitude], {
      radius: 8,
      color: point.etat_annot === 'dirty' ? 'red' : 'green',
      fillOpacity: 0.7
    })
    m.bindPopup(`<b>${point.fichier_nom}</b><br>${point.etat_annot}`)
    m.addTo(map.value)
    markers.value.push(m)
  })

  const dirtyCnt = filtered.filter(p => p.etat_annot === 'dirty').length
  const annCnt = filtered.filter(p => p.etat_annot === 'dirty' || p.etat_annot === 'clean').length
  const rec = filtered.filter(p => new Date(p.date_upload) > Date.now() - 7*86400*1000).length

  stats.value = {
    total: filtered.length,
    dirtyPercent: filtered.length ? Math.round((dirtyCnt/filtered.length)*100) : 0,
    annotatedPercent: filtered.length ? Math.round((annCnt/filtered.length)*100) : 0,
    recent: rec
  }

  computeContext()
  updateWeather()
}

async function updateWeather() {
  try {
    const q = filters.value.quartier ? filters.value.quartier : 'Paris'
    // Remplace PAR_TOKEN par ta clé OpenWeather
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${q},FR&units=metric&lang=fr&appid=PAR_TOKEN`)
    const w = await res.json()
    weather.value = {
      desc: w.weather[0].description,
      temp: Math.round(w.main.temp)
    }
  } catch {
    weather.value = { desc: 'N/A', temp: '--' }
  }
}

onMounted(async () => {
  map.value = L.map('leaflet-map').setView([48.8566, 2.3522], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  const res = await fetch('http://localhost:5000/api/localisation')
  data.value = await res.json()
  quartiers.value = [...new Set(data.value.map(p => p.arrondissement))].sort()
  updateMap()
})

watch(filters, updateMap, { deep: true })
</script>

<style scoped>
.dashboard-container { display: flex; gap:20px; max-width:1300px; margin:auto; }
.sidebar { flex:1 1 280px; background:#f9fafb; border-radius:10px; padding:16px; }
.filter-group label, .stats p, .context p { margin-top:10px; }
#leaflet-map { flex:1 1 900px; height:600px; border-radius:12px; box-shadow:0 0 8px rgba(0,0,0,0.2); }

.dashboard-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  max-width: 1300px;
  margin: auto;
  flex-wrap: wrap;
}

.sidebar {
  flex: 1 1 280px;
  background: #f9fafb;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 0 8px rgba(0,0,0,0.05);
}

.filter-group label {
  display: block;
  font-weight: 600;
  margin-top: 10px;
}

.filter-group select,
.filter-group input[type="date"] {
  width: 100%;
  padding: 6px;
  margin-top: 4px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.stats {
  margin-top: 20px;
  font-size: 0.95rem;
  line-height: 1.5;
}

.map-container {
  flex: 1 1 900px;
}

#leaflet-map {
  height: 600px;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}
</style>
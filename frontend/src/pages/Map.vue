<template>
  <div class="dashboard-container">
    <div class="sidebar">
      <h2> Filtres & Statistiques</h2>
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
        <p> Total : {{ stats.total }}</p>
        <p>️ Pleines : {{ stats.dirtyPercent }}%</p>
        <p> Annotées : {{ stats.annotatedPercent }}%</p>
        <p> Photos récentes : {{ stats.recent }}</p>
      </div>
    </div>

    <div class="map-container">
      <h1> Carte des poubelles annotées</h1>
      <div id="leaflet-map"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref(null)
const markers = ref([])
const data = ref([])
const quartiers = ref([])
const filters = ref({ quartier: '', date: '', etat: '' })
const stats = ref({ total: 0, dirtyPercent: 0, annotatedPercent: 0, recent: 0 })

// Corrige le bug d’icônes manquantes
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

const updateMap = () => {
  markers.value.forEach(m => map.value.removeLayer(m))
  markers.value = []
  const filtered = data.value.filter(point => {
    return (!filters.value.quartier || point.quartier === filters.value.quartier) &&
           (!filters.value.date || point.date_upload?.startsWith(filters.value.date)) &&
           (!filters.value.etat || point.etat_annot === filters.value.etat)
  })

  filtered.forEach(point => {
    const marker = L.circleMarker([point.latitude, point.longitude], {
      radius: 8,
      color: point.etat_annot === 'dirty' ? 'red' : 'green',
      fillOpacity: 0.7
    })
      .bindPopup(`<strong>${point.fichier_nom}</strong><br>État : ${point.etat_annot}`)
      .addTo(map.value)
    markers.value.push(marker)
  })

  const dirtyCount = filtered.filter(p => p.etat_annot === 'dirty').length
  const annotatedCount = filtered.filter(p => ['dirty', 'clean'].includes(p.etat_annot)).length
  const recent = filtered.filter(p => new Date(p.date_upload) > Date.now() - 7 * 24 * 60 * 60 * 1000).length

  stats.value.total = filtered.length
  stats.value.dirtyPercent = filtered.length ? Math.round((dirtyCount / filtered.length) * 100) : 0
  stats.value.annotatedPercent = filtered.length ? Math.round((annotatedCount / filtered.length) * 100) : 0
  stats.value.recent = recent
}

onMounted(async () => {
  map.value = L.map('leaflet-map').setView([48.8566, 2.3522], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  try {
    const response = await fetch('http://localhost:5000/api/localisation')
    data.value = await response.json()
    quartiers.value = [...new Set(data.value.map(p => p.quartier).filter(Boolean))].sort()
    updateMap()
  } catch (err) {
    console.error("Erreur :", err)
  }
})

watch(filters, updateMap, { deep: true })
</script>

<style scoped>
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
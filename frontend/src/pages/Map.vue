<template>
  <div class="map-container">
    <h1>🗺️ Carte interactive des poubelles annotées</h1>
    <div id="leaflet-map" style="height: 600px; border-radius: 12px;"></div>
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

onMounted(async () => {
  const response = await fetch('http://localhost:5000/api/localisation')
  const data = await response.json()

  const map = L.map('leaflet-map').setView([48.8566, 2.3522], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  data.forEach(point => {
    const color = point.etat_annot === 'dirty' ? 'red' : 'green'
    const marker = L.circleMarker([point.latitude, point.longitude], {
      radius: 8,
      fillColor: color,
      color: color,
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    }).addTo(map)

    marker.bindPopup(`
      <b>${point.fichier_nom}</b><br/>
      État : ${point.etat_annot === 'dirty' ? 'Pleine' : 'Vide'}
    `)
  })
})
</script>

<style scoped>
.map-container {
  padding: 20px;
  max-width: 1200px;
  margin: auto;
}

#leaflet-map {
  width: 100%;
  height: 600px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
}
</style>
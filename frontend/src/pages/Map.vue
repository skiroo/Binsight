<template>
  <div class="map-container">
    <h1>🗑️ + 🌤️ État des poubelles & météo locale</h1>
    <div id="leaflet-map"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getLocalisations } from '@/services/api'

const map = ref(null)
const weatherCache = {}

async function getWeather(lat, lon) {
  const key = `${lat.toFixed(4)},${lon.toFixed(4)}`
  if (weatherCache[key]) return weatherCache[key]

  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`
  const res = await fetch(url)
  const j = await res.json()
  const w = j.current_weather || {}
  const ico = w.weathercode !== undefined ? w.weathercode : null
  const temp = w.temperature !== undefined ? w.temperature : '--'
  weatherCache[key] = { icon: ico, temp }
  return weatherCache[key]
}

onMounted(async () => {
  map.value = L.map('leaflet-map').setView([48.8566, 2.3522], 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value)

  const response = await getLocalisations()
  const data = response.data

  for (const p of data) {
    const w = await getWeather(p.latitude, p.longitude)
    const emoji = w.temp !== '--'
      ? `🌡️ ${w.temp}°C`
      : '🌤️ N/A'
    const color = p.etat_annot === 'dirty' ? 'red' : 'green'
    const html = `
      <div style="text-align:center">
        <svg height="14" width="14"><circle cx="7" cy="7" r="7" fill="${color}" /></svg>
        <div style="font-size:11px">${emoji}</div>
      </div>`

    const marker = L.marker([p.latitude, p.longitude], {
      icon: L.divIcon({ html, className: '' })
    })

    marker.bindPopup(`
      <b>${p.fichier_nom}</b><br>
      État : ${p.etat_annot || 'inconnu'}<br>
      Ville : ${p.ville || 'non spécifiée'}<br>
      Météo : ${emoji}
    `)

    marker.addTo(map.value)
  }
})
</script>

<style scoped>
.map-container {
  max-width: 1000px;
  margin: 20px auto;
  text-align: center;
}
#leaflet-map {
  height: 600px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
</style>

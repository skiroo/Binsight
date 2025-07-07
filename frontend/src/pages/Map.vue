<template>
  <div class="map-container">
    <h1>🗺️ Carte interactive des poubelles annotées</h1>
    <div ref="mapContainer" class="map" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

const mapContainer = ref(null)
const map = ref(null)

// ⚠️ Remplace cette clé par ta propre clé Mapbox si besoin
mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4Nm52eTA2emYycXBndjZ4bWl3N3gifQ.1JY8uYvXDsTkFgF7jVIR0g'

onMounted(async () => {
  const response = await fetch('http://localhost:5000/api/localisation') // ← à adapter si nécessaire
  const data = await response.json()

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [2.3522, 48.8566],
    zoom: 11,
  })

  // Ajout des points
  data.forEach((point) => {
    new mapboxgl.Marker({
      color: point.etat_annot === 'dirty' ? 'red' : 'green',
    })
      .setLngLat([point.longitude, point.latitude])
      .setPopup(new mapboxgl.Popup().setHTML(`<b>${point.fichier_nom}</b><br>${point.etat_annot}`))
      .addTo(map.value)
  })
})
</script>

<style scoped>
.map-container {
  padding: 20px;
  max-width: 1200px;
  margin: auto;
}

.map {
  width: 100%;
  height: 600px;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
}
</style>
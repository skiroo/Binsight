<template>
  <div class="map-container">
    <h1>🗺️ Carte interactive des poubelles annotées</h1>
    <div id="leaflet-map"></div>
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Corrige le bug d’icônes manquantes
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

onMounted(async () => {
  // Initialise la carte centrée sur Paris
  const map = L.map('leaflet-map').setView([48.8566, 2.3522], 12)

  // Ajoute le fond de carte OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  // Charge les points depuis le backend
  try {
    const response = await fetch('http://localhost:5000/api/localisation')
    const data = await response.json()
    console.log(data)

    // Ajoute un marqueur pour chaque point
    data.forEach(point => {
      const marker = L.circleMarker([point.latitude, point.longitude], {
        radius: 8,
        color: point.etat_annot === 'dirty' ? 'red' : 'green',
        fillOpacity: 0.7
      })

      marker.bindPopup(`
        <strong>${point.fichier_nom}</strong><br>
        État : ${point.etat_annot === 'dirty' ? 'Pleine' : 'Vide'}
      `)

      marker.addTo(map)
    })

  } catch (error) {
    console.error("Erreur de chargement des données :", error)
  }
})

</script>

<style scoped>
.map-container {
  max-width: 1100px;
  margin: 20px auto;
  padding: 10px;
}

#leaflet-map {
  height: 600px;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}
</style>
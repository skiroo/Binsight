<template>
  <div id="map" style="height: 80vh;"></div>
</template>

<script>
import L from 'leaflet';
import { onMounted } from 'vue';
import { getLocalisations } from '@/services/api';

export default {
  name: 'Map',
  setup() {
    onMounted(async () => {
      const map = L.map('map').setView([48.8566, 2.3522], 12); // Vue initiale sur Paris

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(map);

      const response = await getLocalisations();

      response.data.forEach((loc) => {
        if (!loc.latitude || !loc.longitude) return;

        const color = loc.etat_annot === 'dirty' ? 'red' : 'green';

        const icon = L.circleMarker([loc.latitude, loc.longitude], {
          radius: 8,
          color,
          fillOpacity: 0.8
        }).addTo(map);

        icon.bindPopup(`
          <b>${loc.fichier_nom}</b><br/>
          État : ${loc.etat_annot || 'non annotée'}<br/>
          Ville : ${loc.ville || 'Inconnue'}
        `);
      });
    });
  }
};
</script>

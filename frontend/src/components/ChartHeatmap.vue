<template>
  <div class="heatmap-container">
    <h3 class="heatmap-title">{{ t("Carte de chaleur des déchets", "Trash Heatmap") }}</h3>

    <!-- Filtres état -->
    <div class="toggle-buttons">
      <button :class="{ active: mode === 'dirty' }" @click="mode = 'dirty'; updateHeatmap()">
        {{ t("Poubelles pleines", "Full bins") }}
      </button>
      <button :class="{ active: mode === 'clean' }" @click="mode = 'clean'; updateHeatmap()">
        {{ t("Poubelles vides", "Empty bins") }}
      </button>
    </div>

    <div id="map"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet.heat'
import { getLocalisations } from '@/services/api'

const props = defineProps({
  lang: String,
  periode: String,
  start: String,
  end: String
})

const t = (fr, en) => props.lang === 'fr' ? fr : en
const map = ref(null)
const heatLayer = ref(null)
const localisations = ref([])
const mode = ref('dirty')

async function fetchLocalisations() {
  try {
    const res = props.periode === 'custom' && props.start && props.end
      ? await getLocalisations('custom', props.start, props.end)
      : await getLocalisations(props.periode)

    localisations.value = res.data || []
    updateHeatmap()
  } catch (error) {
    console.error('Erreur chargement localisations heatmap :', error)
  }
}

function updateHeatmap() {
  if (!map.value || localisations.value.length === 0) return

  const filtered = localisations.value.filter(p => p.etat_annot === mode.value)
  const points = filtered.map(p => [p.latitude, p.longitude, 0.8])

  if (heatLayer.value) {
    map.value.removeLayer(heatLayer.value)
  }

  heatLayer.value = L.heatLayer(points, {
    radius: 30,
    blur: 25,
    maxZoom: 17,
    gradient: mode.value === 'dirty'
      ? { 0.2: '#ff9933', 0.4: '#ff3300', 0.6: '#cc0000' }
      : { 0.2: '#99ffcc', 0.4: '#33cc99', 0.6: '#009966' }
  }).addTo(map.value)
}

onMounted(() => {
  map.value = L.map('map').setView([48.8566, 2.3522], 12)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CartoDB'
  }).addTo(map.value)

  fetchLocalisations()
})

watch([() => props.periode, () => props.start, () => props.end], fetchLocalisations)
</script>

<style scoped>
.heatmap-container {
  background: white;
  color: #111827;
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, color 0.3s ease;
}
:deep(.dark-theme) .heatmap-container {
  background: #161b22;
  color: #f1f1f1;
}

.heatmap-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

#map {
  width: 100%;
  height: 400px;
  border-radius: 1rem;
  margin-top: 0.5rem;
}

/* Boutons toggle */
.toggle-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.toggle-buttons button {
  flex: 1;
  padding: 0.4rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  background: #f0f0f0;
  cursor: pointer;
  font-weight: 500;
  color: #111827;
}
.toggle-buttons button.active {
  background: #16a085;
  color: white;
  border-color: #16a085;
}
:deep(.dark-theme) .toggle-buttons button {
  background: #222;
  border-color: #444;
  color: #eee;
}
:deep(.dark-theme) .toggle-buttons button.active {
  background: #1abc9c;
  border-color: #1abc9c;
  color: #ffffff;
}
</style>
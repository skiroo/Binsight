<template>
  <div class="dashboard-container" :class="{ 'dark-theme': isDark }">
    <h1 class="dashboard-title">{{ t('Tableau de bord', 'Dashboard') }}</h1>

    <!-- 🎛️ Barre de filtre -->
    <div class="filter-bar">
      <label for="periode">{{ t('Période', 'Period') }} :</label>
      <select v-model="periode" @change="handlePeriodChange">
        <option value="day">{{ t("Aujourd'hui", "Today") }}</option>
        <option value="week">{{ t("7 derniers jours", "Last 7 days") }}</option>
        <option value="month">{{ t("30 derniers jours", "Last 30 days") }}</option>
        <option value="custom">{{ t("Plage personnalisée", "Custom range") }}</option>
      </select>

      <template v-if="periode === 'custom'">
        <label>{{ t("Du", "From") }} :</label>
        <input type="date" v-model="startDate" @change="fetchStats" />
        <label>{{ t("Au", "To") }} :</label>
        <input type="date" v-model="endDate" @change="fetchStats" />
      </template>
    </div>

    <!-- 📊 Statistiques générales -->
    <div class="stats-grid">
      <div class="stat-card stat-total">
        <h2>{{ t("Total d'images", "Total images") }}</h2>
        <p>{{ stats.total_images }}</p>
      </div>
      <div class="stat-card stat-vides">
        <h2>{{ t("% Vides", "% Empty") }}</h2>
        <p>{{ stats.vides_percent }}%</p>
      </div>
      <div class="stat-card stat-pleines">
        <h2>{{ t("% Pleines", "% Full") }}</h2>
        <p>{{ stats.pleines_percent }}%</p>
      </div>
    </div>

    <!-- 📈 Graphiques -->
    <div class="charts-grid">
      <ChartTrend :lang="lang" />
      <ChartDensity :lang="lang" :periode="periode" :start="startDate" :end="endDate" />
      <ChartPie :lang="lang" :periode="periode" :start="startDate" :end="endDate" />
      <ChartHeatmap :lang="lang" :periode="periode" :start="startDate" :end="endDate" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getStats } from '@/services/api';
import ChartDensity from '@/components/ChartDensity.vue';
import ChartTrend from '@/components/ChartTrend.vue';
import ChartPie from '@/components/ChartPie.vue';
import ChartHeatmap from '@/components/ChartHeatmap.vue';

const props = defineProps({ lang: String, isDark: Boolean });
const t = (fr, en) => props.lang === 'fr' ? fr : en;

const stats = ref({ total_images: 0, vides_percent: 0, pleines_percent: 0 });
const periode = ref('day');
const startDate = ref('');
const endDate = ref('');

async function fetchStats() {
  let res;
  if (periode.value === 'custom' && startDate.value && endDate.value) {
    res = await getStats(startDate.value, endDate.value);
  } else {
    res = await getStats(periode.value);
  }
  stats.value = {
    total_images: res.total_images,
    vides_percent: res['vides_%'],
    pleines_percent: res['pleines_%']
  };
}

function handlePeriodChange() {
  if (periode.value !== 'custom') {
    fetchStats();
  }
}

onMounted(fetchStats);
</script>
<style scoped>
.dashboard-container {
  padding: 1.5rem;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 🌞 Mode clair */
.light-theme {
  background-color: #ffffff;
  color: #111827;
}

/* 🌙 Mode sombre */
.dark-theme {
  background-color: #0d1117; /* Noir bleuté comme ta page d'accueil */
  color: #f1f1f1;
}

/* TITRE */
.dashboard-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

/* BARRE DE FILTRES */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filter-bar select,
.filter-bar input {
  padding: 0.3rem 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid #ccc;
  background: white;
  color: #111827;
}
.dark-theme .filter-bar select,
.dark-theme .filter-bar input {
  background: #161b22;
  color: #f1f1f1;
  border: 1px solid #333;
}

/* GRILLE STATS */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}
@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* CARTES */
.stat-card {
  padding: 1rem;
  border-radius: 1rem;
  background-color: white;
  color: #111827;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, color 0.3s ease;
}
.dark-theme .stat-card {
  background-color: #161b22;
  color: #f1f1f1;
}

.stat-card h2 {
  font-size: 1.125rem;
  font-weight: 600;
}
.stat-card p {
  font-size: 1.875rem;
}

/* COULEURS SPÉCIFIQUES */
.stat-vides {
  background-color: #d1fae5;
}
.stat-pleines {
  background-color: #fecaca;
}
.dark-theme .stat-vides {
  background-color: #054438;
}
.dark-theme .stat-pleines {
  background-color: #430415;
}

/* CHARTS */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 1024px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.dark-theme .charts-grid > * {
  background-color: #161b22;
  border-radius: 1rem;
  padding: 1rem;
  color: #ffffff;
}
</style>
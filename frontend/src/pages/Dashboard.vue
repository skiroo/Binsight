<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">{{ t('Tableau de bord', 'Dashboard') }}</h1>

    <div class="filter-bar">
      <label for="periode">{{ t('Période', 'Period') }} :</label>
      <select id="periode" v-model="periode" @change="fetchStats">
        <option value="day">{{ t("Aujourd'hui", "Today") }}</option>
        <option value="week">{{ t("7 derniers jours", "Last 7 days") }}</option>
        <option value="month">{{ t("30 derniers jours", "Last 30 days") }}</option>
      </select>
    </div>

    <div class="stats-grid">
      <div class="stat-card stat-total">
        <h2>{{ t("Total d'images", "Total images") }}</h2>
        <p>{{ stats.total_images }}</p>
      </div>
      <div class="stat-card stat-vides">
        <h2>{{ t('% Vides', '% Empty') }}</h2>
        <p>{{ stats.vides_percent }}%</p>
      </div>
      <div class="stat-card stat-pleines">
        <h2>{{ t('% Pleines', '% Full') }}</h2>
        <p>{{ stats.pleines_percent }}%</p>
      </div>
    </div>

    <div class="charts-grid">
      <ChartDensity />
      <ChartTrend />
    </div>
  </div>
</template>

<script setup>
import { getStats } from '@/services/api';
import ChartDensity from '@/components/ChartDensity.vue';
import ChartTrend from '@/components/ChartTrend.vue';
import { ref, onMounted } from 'vue';

const props = defineProps({ lang: String })
const t = (fr, en) => props.lang === 'fr' ? fr : en

const stats = ref({
  total_images: 0,
  vides_percent: 0,
  pleines_percent: 0
})

const periode = ref('day')

async function fetchStats() {
  const res = await getStats(periode.value);
  stats.value = {
    total_images: res.total_images,
    vides_percent: res['vides_%'],
    pleines_percent: res['pleines_%']
  };
}

onMounted(fetchStats);
</script>

<style scoped>
.dashboard-container {
  padding: 1.5rem;
}

.dashboard-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-bar select {
  padding: 0.3rem 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid #ccc;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
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

.stat-card {
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: white;
}

.stat-total {
  background-color: white;
}

.stat-vides {
  background-color: #d1fae5;
}

.stat-pleines {
  background-color: #fecaca;
}

.stat-card h2 {
  font-size: 1.125rem;
  font-weight: 600;
}

.stat-card p {
  font-size: 1.875rem;
}

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
</style>
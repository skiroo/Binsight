<template>
  <div class="chart-container">
    <h2 class="chart-title">{{ t('Quartiers les plus touchés', 'Most affected districts') }}</h2>
    <canvas ref="densityChart"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import { getAlerts } from '@/services/api'; // ✅ utilise ton API centralisée
Chart.register(...registerables);

export default {
  name: 'ChartDensity',
  props: {
    lang: { type: String, default: 'fr' },
    periode: { type: String, required: true },
    start: { type: String, default: '' },
    end: { type: String, default: '' }
  },
  data() {
    return {
      chartInstance: null
    };
  },
  methods: {
    t(fr, en) {
      return this.lang === 'fr' ? fr : en;
    },
    async fetchAlerts() {
      try {
        const res = await getAlerts(this.periode, this.start, this.end); // 👈 utilisation avec filtres
        const alertes = res.data?.alertes || [];

        const labels = alertes.map(e => e.quartier);
        const values = alertes.map(e => e.nb_dirty);

        if (this.chartInstance) this.chartInstance.destroy();

        const ctx = this.$refs.densityChart.getContext('2d');
        this.chartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label: this.t('Nombre de poubelles pleines', 'Number of full bins'),
              data: values,
              backgroundColor: 'rgba(255, 99, 132, 0.6)'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              y: { beginAtZero: true }
            }
          }
        });
      } catch (err) {
        console.error("❌ Erreur ChartDensity :", err);
      }
    }
  },
  mounted() {
    this.fetchAlerts();
  },
  watch: {
    periode: 'fetchAlerts',
    start: 'fetchAlerts',
    end: 'fetchAlerts'
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }
};
</script>

<style scoped>
.chart-container {
  background: white;
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 360px;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

canvas {
  width: 100% !important;
  height: 280px !important;
}
</style>

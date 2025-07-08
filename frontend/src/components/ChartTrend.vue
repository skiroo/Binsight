<template>
  <div class="chart-container">
    <h2 class="chart-title">{{ t("Évolution des déchets", "Trash evolution") }}</h2>
    <canvas ref="trendChart" height="300"></canvas>
  </div>
</template>

<script>
import { getLocalisations } from '@/services/api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ChartTrend',
  props: {
    lang: { type: String, default: 'fr' }
  },
  data() {
    return {
      chartInstance: null
    }
  },
  methods: {
    t(fr, en) {
      return this.lang === 'fr' ? fr : en;
    }
  },
  async mounted() {
    try {
      const res = await getLocalisations();
      const data = res.data || [];

      const countsByDate = {};

      data.forEach(item => {
        const date = item.date_upload.split('T')[0];
        if (!countsByDate[date]) {
          countsByDate[date] = { clean: 0, dirty: 0 };
        }
        if (item.etat_annot === 'clean') countsByDate[date].clean++;
        if (item.etat_annot === 'dirty') countsByDate[date].dirty++;
      });

      const labels = Object.keys(countsByDate).sort();
      const cleanData = labels.map(d => countsByDate[d].clean);
      const dirtyData = labels.map(d => countsByDate[d].dirty);

      const ctx = this.$refs.trendChart.getContext('2d');
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: this.t('Propres', 'Clean'),
              data: cleanData,
              borderColor: 'green',
              backgroundColor: 'rgba(0,128,0,0.1)',
              fill: true
            },
            {
              label: this.t('Pleines', 'Full'),
              data: dirtyData,
              borderColor: 'red',
              backgroundColor: 'rgba(255,0,0,0.1)',
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    } catch (err) {
      console.error("Erreur ChartTrend :", err);
    }
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }
}
</script>

<style scoped>
.chart-container {
  background: white;
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

canvas {
  width: 100% !important;
}
</style>

<template>
  <div class="bg-white p-4 rounded-2xl shadow">
    <h2 class="text-xl font-semibold mb-2">{{ t('Répartition par source', 'Breakdown by source') }}</h2>
    <canvas ref="pieChart" height="300"></canvas>
  </div>
</template>

<script>
import { getLocalisations } from '@/services/api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ChartPieSource',
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

      const sources = { citoyen: 0, agent: 0, camera: 0, autre: 0 };
      data.forEach(p => {
        const s = (p.source || '').toLowerCase();
        if (s === 'citoyen') sources.citoyen++;
        else if (s === 'agent') sources.agent++;
        else if (s === 'camera') sources.camera++;
        else sources.autre++;
      });

      const ctx = this.$refs.pieChart.getContext('2d');
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: [
            this.t('Citoyen', 'Citizen'),
            this.t('Agent', 'Agent'),
            'Camera',
            this.t('Autre', 'Other')
          ],
          datasets: [{
            label: this.t('Images', 'Images'),
            data: Object.values(sources),
            backgroundColor: [
              '#34d399', '#60a5fa', '#fcd34d', '#a78bfa'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
            title: { display: false }
          }
        }
      });
    } catch (err) {
      console.error("Erreur ChartPieSource:", err);
    }
  },
  beforeDestroy() {
    if (this.chartInstance) this.chartInstance.destroy();
  }
}
</script>

<style scoped>
canvas {
  width: 100% !important;
}
</style>
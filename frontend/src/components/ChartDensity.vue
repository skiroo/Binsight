<template>
  <div class="bg-white p-4 rounded-2xl shadow">
    <h2 class="text-xl font-semibold mb-2">Quartiers les plus touchés</h2>
    <canvas ref="densityChart" height="300"></canvas>
  </div>
</template>

<script>
import { getAlerts } from '@/services/api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ChartDensity',
  data() {
    return {
      chartInstance: null
    }
  },

    async mounted() {
        try {
            const res = await getAlerts();
            const alertes = res.data?.alertes || [];

            const labels = alertes.map(e => e.quartier);
            const values = alertes.map(e => e.nb_dirty);

            const ctx = this.$refs.densityChart.getContext('2d');
            this.chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                label: 'Nombre de poubelles pleines',
                data: values,
                backgroundColor: 'rgba(255, 99, 132, 0.6)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                legend: { display: false }
                },
                scales: {
                y: { beginAtZero: true }
                }
            }
            });
        } catch (err) {
            console.error("Erreur ChartDensity :", err);
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
canvas {
  width: 100% !important;
}
</style>
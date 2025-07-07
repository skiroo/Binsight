import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import './assets/styles.css';

import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

const app = createApp(App);
app.use(router);
app.mount('#app');

import { createRouter, createWebHistory } from 'vue-router';

import Home from './pages/Home.vue';
import Upload from './pages/Upload.vue';
import Dashboard from './pages/Dashboard.vue';
import Map from './pages/Map.vue';
import About from './pages/About.vue';

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },

    {
        path: '/upload',
        name: 'Upload',
        component: Upload
    },

    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
    },

    {
        path: '/map',
        name: 'Map',
        component: Map
    },

    {
        path: '/about',
        name: 'About',
        component: About
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;

import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from './components/UploadPage.vue'
import MapPage from './components/MapPage.vue'
import ImageFromGitHub from './components/ImageFromGitHub.vue' // <- il manquait ça

const routes = [
  { path: '/github-image', component: ImageFromGitHub },
  { path: '/upload', component: UploadPage },
  { path: '/carte', component: MapPage },
  { path: '/', redirect: '/upload' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
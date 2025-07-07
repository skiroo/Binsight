<template>
  <div class="app-container" :class="isDark ? 'dark-theme' : 'light-theme'">
    <Navbar
      :isDark="isDark"
      :user="connectedUser"
      :lang="lang"
      @toggle-theme="toggleTheme"
      @toggle-lang="toggleLang"
      @open-login="showModal = true"
    />

    <LoginRegisterModal
      v-if="showModal"
      :isDark="isDark"
      @close="showModal = false"
      @user-connected="handleUserConnected"
    />

    <main class="flex-grow">
      <RouterView :lang="lang" />
    </main>

<Footer :lang="lang" />

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import LoginRegisterModal from './components/LoginRegisterModal.vue'

const isDark = ref(false)
const showModal = ref(false)
const connectedUser = ref(null)
const lang = ref('fr') // <-- Langue par défaut

function toggleLang() {
  lang.value = lang.value === 'fr' ? 'en' : 'fr'
}

function toggleTheme() {
  isDark.value = !isDark.value
}

function handleUserConnected(user) {
  connectedUser.value = user
  localStorage.setItem('user', JSON.stringify(user))
}

watch(isDark, (newVal) => {
  document.documentElement.classList.toggle('dark-theme', newVal)
  document.documentElement.classList.toggle('light-theme', !newVal)
})

onMounted(() => {
  document.documentElement.classList.add('light-theme')
  const user = localStorage.getItem('user')
  if (user) {
    connectedUser.value = JSON.parse(user)
  }
})
</script>

<style>
/* STRUCTURE */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex-grow: 1;
}

/* BASE */
html,
body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  transition: background-color 0.3s, color 0.3s;
}

/* THÈME CLAIR */
.light-theme {
  background-color: #ffffff;
  color: #1a1a1a;
}

/* THÈME SOMBRE */
.dark-theme {
  background-color: #0e1117;
  color: #f1f1f1;
}

.dark-theme h1,
.dark-theme h2,
.dark-theme h3,
.dark-theme p,
.dark-theme a {
  color: #f1f1f1;
}

.dark-theme .card {
  background-color: #1c1f26;
  border: 1px solid #2c313c;
}

.dark-theme .btn-primary {
  background-color: #10b981;
  color: #fff;
}

.dark-theme .btn-primary:hover {
  background-color: #059669;
}
</style>
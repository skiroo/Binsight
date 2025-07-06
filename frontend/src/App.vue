<template>
  <div class="app-container">
    <Navbar @open-login="showLogin = true" @toggle-theme="toggleDark" :is-dark="darkMode" />

    <LoginRegisterModal v-if="showLogin" @close="showLogin = false" :is-dark="darkMode" />

    <main class="flex-grow">
      <router-view />
    </main>

    <Footer />
  </div>
</template>

<script>
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import LoginRegisterModal from "@/components/LoginRegisterModal.vue";

export default {
  components: {
    Navbar,
    Footer,
    LoginRegisterModal,
  },
  data() {
    return {
      showLogin: false,
      darkMode: false,
    };
  },
  methods: {
    toggleDark() {
      this.darkMode = !this.darkMode;
    },
  },
  watch: {
    darkMode(newVal) {
      document.documentElement.classList.toggle("dark-theme", newVal);
      document.documentElement.classList.toggle("light-theme", !newVal);
    },
  },
  mounted() {
    document.documentElement.classList.add("light-theme"); // Thème par défaut
  },
};
</script>

<style>
/* STRUCTURE FLEX POUR PIED DE PAGE FIXÉ */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex-grow: 1;
}

/* BASE GLOBALE */
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
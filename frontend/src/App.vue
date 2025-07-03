<template>
  <div id="app">
    <Navbar @open-login="showLogin = true" @toggle-theme="toggleDark" :is-dark="darkMode" />
    <LoginRegisterModal v-if="showLogin" @close="showLogin = false" :is-dark="darkMode" />
    <router-view />
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
    LoginRegisterModal,
    Footer,
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
      document.documentElement.classList.toggle('dark-theme', newVal);
      document.documentElement.classList.toggle('light-theme', !newVal);
    }
  },
  mounted() {
    document.documentElement.classList.add('light-theme'); // Thème par défaut
  }
};
</script>

<style>
/* Base */
html, body {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  transition: background-color 0.3s, color 0.3s;
}

/* Thème clair */
.light-theme {
  background-color: #ffffff;
  color: #1a1a1a;
}

/* Thème sombre */
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


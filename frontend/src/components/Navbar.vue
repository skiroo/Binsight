<template>
    <header class="navbar">
        <div class="logo-title">
            <img src="@/assets/logo.png" alt="Logo Binsight" class="logo-image" />
            <h1 class="title">Binsight</h1>
        </div>

        <nav class="nav-links">
            <router-link to="/">{{ lang === 'fr' ? "Accueil" : "Home" }}</router-link>
            <router-link to="/upload">{{ lang === 'fr' ? "Image" : "Upload" }}</router-link>
            <router-link to="/map">{{ lang === 'fr' ? "Carte" : "Map" }}</router-link>
            <router-link to="/dashboard">{{ lang === 'fr' ? "Tableau de Bord" : "Dashboard" }}</router-link>

            <router-link v-if="user && (user.role === 'admin' || user.role === 'agent')" to="/option">
                {{ lang === 'fr' ? "Paramètre" : "Option" }}
            </router-link>

            <router-link to="/about">{{ lang === 'fr' ? "À propos" : "About" }}</router-link>
        </nav>

        <div class="navbar-actions">
            <button class="theme-btn" @click="$emit('toggle-theme')">
                {{ isDark ? "☀️" : "🌙" }}
            </button>

            <!-- 🌐 Bouton langue -->
            <button class="theme-btn" @click="$emit('toggle-lang')">
                {{ lang === 'fr' ? "EN" : "FR" }}
            </button>

            <template v-if="user">
                <span class="user-info">
                    {{ lang === 'fr' ? "Bienvenue" : "Welcome" }}, {{ user.nom_utilisateur }}
                </span>
                <button class="login-btn" @click="logout">
                    {{ lang === 'fr' ? "Déconnexion" : "Logout" }}
                </button>
            </template>

            <template v-else>
                <button class="login-btn" @click="$emit('open-login')">
                    {{ lang === 'fr' ? "Connexion / Inscription" : "Login / Sign Up" }}
                </button>
            </template>
        </div>
    </header>
</template>

<script setup>
import { useRouter } from 'vue-router';

const { isDark, user, lang } = defineProps({
  isDark: Boolean,
  user: Object,
  lang: String
})

const router = useRouter()

function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('role');
  router.go(); // ou router.push('/') pour forcer un retour à l’accueil
}
</script>

<style scoped>
.logo-image {
  height: 60px; 
  width: auto;
  object-fit: contain;
  margin-right: 0.75rem;
}
.navbar {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.logo-title {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 2rem;
  margin-right: 0.5rem;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.nav-links {
  display: flex;
  gap: 1.2rem;
  flex-wrap: wrap;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: #1abc9c;
}

.navbar-actions {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  flex-wrap: wrap;
}

.theme-btn {
  background: linear-gradient(135deg, #34495e, #2c3e50);
  color: #f1f1f1;
  border: 1px solid #4b5563;
  border-radius: 6px;
  padding: 0.45rem 0.9rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.theme-btn:hover {
  background: linear-gradient(135deg, #3b5368, #1f2b38);
}

.login-btn {
  background-color: #1abc9c;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: bold;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #16a085;
}

.user-info {
  font-weight: 500;
  margin-right: 0.5rem;
}
</style>
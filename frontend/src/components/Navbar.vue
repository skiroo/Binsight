<template>
  <header class="navbar">
    <div class="logo-title">
      <span class="logo">🗑️</span>
      <h1 class="title">VISIO</h1>
    </div>

    <nav class="nav-links">
      <router-link to="/">Accueil</router-link>
      <router-link to="/upload">Upload</router-link>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link to="/map">Carte</router-link>
      <router-link to="/about">À propos</router-link>
    </nav>

    <div class="navbar-actions">
      <button class="theme-btn" @click="$emit('toggle-theme')">
        {{ isDark ? "☀️" : "🌙" }}
      </button>

      <button class="login-btn" @click="$emit('open-login')">
        Connexion / Inscription
      </button>
    </div>
  </header>
</template>

<script>
export default {
  props: {
    isDark: Boolean
  }
};
</script>

<style scoped>
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
</style>
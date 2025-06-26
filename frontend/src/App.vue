<script setup>
</script>

<template>
  <header>
    <h1>VISIO</h1>
    <nav>
      <router-link to="/upload">📤 Upload</router-link>
      |
      <router-link to="/carte">🗺️ Carte Dynamique</router-link>
    </nav>
  </header>

  <main>
    <router-view />
  </main>
</template>

<style scoped>
header {
  padding: 1rem;
  background: #333;
  color: white;
  text-align: center;
}
nav a {
  color: white;
  text-decoration: none;
  margin: 0 1rem;
}
</style>
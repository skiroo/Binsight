<template>
  <footer class="footer">
    <div class="footer-content">
      <p>&copy; 2025 BinSight —
        {{ lang === 'fr' ? 'Tous droits réservés' : 'All rights reserved' }}
      </p>
      <nav class="footer-nav">
        <RouterLink to="/about">
          {{ lang === 'fr' ? 'À propos' : 'About' }}
        </RouterLink>
      </nav>
    </div>
  </footer>
</template>

<script setup>
const { lang } = defineProps({
  lang: String
})
</script>

<style scoped>
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 20px 0;
  text-align: center;
  margin-top: 60px;
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.1);
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-nav {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: text-decoration 0.3s ease;
}

.footer-nav a:hover {
  text-decoration: underline;
}
</style>
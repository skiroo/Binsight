<template>
  <div class="home">
    <section class="hero">
      <h1>
        {{ lang === 'fr' ? 'Bienvenue sur' : 'Welcome to' }}
        <span class="highlight">Binsight</span>
      </h1>
      <p class="intro">
        {{
          lang === 'fr'
            ? "Plateforme intelligente de suivi et d’identification des déchets publics.\nEnsemble, luttons contre les dépôts sauvages grâce à la technologie."
            : "Smart platform for monitoring and identifying public waste.\nTogether, let's fight illegal dumping with technology."
        }}
      </p>
      <router-link to="/upload" class="btn-primary">
        📤 {{ lang === 'fr' ? 'Déposer une image' : 'Upload an image' }}
      </router-link>
    </section>

    <section class="features">
      <div class="card feature-card">
        <h3>📍 <strong>{{ lang === 'fr' ? 'Géolocalisation' : 'Geolocation' }}</strong></h3>
        <p>{{ lang === 'fr' ? 'Identifiez et suivez les lieux de dépôts sauvages.' : 'Identify and track illegal dumping locations.' }}</p>
      </div>
      <div class="card feature-card">
        <h3>🤖 <strong>{{ lang === 'fr' ? 'IA & Reconnaissance' : 'AI & Recognition' }}</strong></h3>
        <p>{{ lang === 'fr' ? 'Analyse intelligente des images envoyées.' : 'Smart analysis of uploaded images.' }}</p>
      </div>
      <div class="card feature-card">
        <h3>📊 <strong>{{ lang === 'fr' ? 'Tableau de bord' : 'Dashboard' }}</strong></h3>
        <p>{{ lang === 'fr' ? 'Visualisation claire et intuitive des données.' : 'Clear and intuitive data visualization.' }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
const { lang } = defineProps({
  lang: String
})
</script>

<style scoped>
.home {
  padding: 40px 20px;
  text-align: center;
}

.hero h1 {
  font-size: 2.8rem;
  margin-bottom: 20px;
}

.highlight {
  color: #10b981;
}

.intro {
  font-size: 1.2rem;
  margin-bottom: 30px;
  white-space: pre-line;
}

.btn-primary {
  background-color: #10b981;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: bold;
  text-decoration: none;
  display: inline-block;
  margin-top: 15px;
}

.btn-primary:hover {
  background-color: #059669;
}

.features {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  flex-wrap: wrap;
}

.feature-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 15px;
  width: 250px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: left;
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.dark-theme .feature-card {
  background-color: #1f2937;
  color: #f1f1f1;
}
</style>
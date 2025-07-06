<template>
  <div class="about">
    <section class="hero">
      <h1>À propos de <span class="highlight">VISIO</span></h1>
      <p class="intro">
        VISIO est une plateforme intelligente de suivi, d’analyse et de visualisation des dépôts sauvages.<br />
        Grâce à l’IA, à la géolocalisation et à des outils interactifs, elle contribue à la préservation de notre environnement.
      </p>
    </section>

    <section class="features">
      <div class="card feature-card">
        <h3> <strong>Notre mission</strong></h3>
        <p>Lutter contre les dépôts sauvages en combinant technologie, citoyenneté et écologie.</p>
      </div>

      <div class="card feature-card">
        <h3> <strong>Notre équipe</strong></h3>
        <p>Une équipe d’étudiants passionnés par l’innovation, la tech éthique et l’environnement.</p>
      </div>

      <div class="card feature-card">
        <h3> <strong>Notre vision</strong></h3>
        <p>Rendre la propreté urbaine plus intelligente, plus accessible et participative.</p>
      </div>
    </section>

    <div class="conclusion">
      <p>
        VISIO est né dans le cadre d’un projet étudiant à vocation écologique.<br />
        Nous croyons en la technologie au service du bien commun.
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({isDark: Boolean})
</script>

<style scoped>
.about {
  padding: 40px 20px;
  text-align: center;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
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
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.features {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  flex-wrap: wrap;
}

.feature-card {
  background-color: #e5e7eb;
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

.conclusion {
  margin-top: 60px;
  font-size: 0.95rem;
  color: #ccc;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.5;
}

/* Mode sombre (optionnel si tu gères via classe globale) */
.dark-theme .about {
  --bg-color: #0e1015;
  --text-color: #ffffff;
}

.dark-theme .feature-card {
  background-color: #1f2937;
  color: #e5e7eb;
}

.light-theme .about {
  --bg-color: #ffffff;
  --text-color: #1a1a1a;
}
</style>
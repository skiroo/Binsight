<template>
  <div class="about">
    <section class="hero">
      <h1>{{ text.title }} <span class="highlight">Binsight</span></h1>
      <p class="intro">{{ text.intro }}</p>
    </section>

    <section class="features">
      <div class="card feature-card">
        <h3><strong>{{ text.missionTitle }}</strong></h3>
        <p>{{ text.mission }}</p>
      </div>

      <div class="card feature-card">
        <h3><strong>{{ text.teamTitle }}</strong></h3>
        <p>{{ text.team }}</p>
      </div>

      <div class="card feature-card">
        <h3><strong>{{ text.visionTitle }}</strong></h3>
        <p>{{ text.vision }}</p>
      </div>
    </section>

    <div class="conclusion">
      <p>{{ text.conclusion }}</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ isDark: Boolean, lang: String });

const text = {
  title: props.lang === 'fr' ? 'À propos de' : 'About',
  intro:
    props.lang === 'fr'
      ? 'Binsight est une plateforme intelligente de suivi, d’analyse et de visualisation des dépôts sauvages.\nGrâce à l’IA, à la géolocalisation et à des outils interactifs, elle contribue à la préservation de notre environnement.'
      : 'Binsight is a smart platform for monitoring, analyzing, and visualizing illegal dumping.\nWith AI, geolocation, and interactive tools, it helps protect our environment.',
  missionTitle: props.lang === 'fr' ? 'Notre mission' : 'Our mission',
  mission:
    props.lang === 'fr'
      ? 'Lutter contre les dépôts sauvages en combinant technologie, citoyenneté et écologie.'
      : 'Fight illegal dumping by combining technology, citizenship, and ecology.',
  teamTitle: props.lang === 'fr' ? 'Notre équipe' : 'Our team',
  team:
    props.lang === 'fr'
      ? 'Une équipe d’étudiants passionnés par l’innovation, la tech éthique et l’environnement.'
      : 'A team of students passionate about innovation, ethical tech, and the environment.',
  visionTitle: props.lang === 'fr' ? 'Notre vision' : 'Our vision',
  vision:
    props.lang === 'fr'
      ? 'Rendre la propreté urbaine plus intelligente, plus accessible et participative.'
      : 'Make urban cleanliness smarter, more accessible, and participative.',
  conclusion:
    props.lang === 'fr'
      ? 'Binsight est né dans le cadre d’un projet étudiant à vocation écologique.\nNous croyons en la technologie au service du bien commun.'
      : 'Binsight was born as a student project with an ecological purpose.\nWe believe in technology serving the common good.'
};
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
  white-space: pre-line;
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
  white-space: pre-line;
}

/* Mode sombre */
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
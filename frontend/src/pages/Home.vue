<template>
  <div class="home">
    <section class="hero">
      <h1>Bienvenue sur <span class="highlight">VISIO</span></h1>
      <p class="intro">
        Plateforme intelligente de suivi et d’identification des déchets publics.<br />
        Ensemble, luttons contre les dépôts sauvages grâce à la technologie.
      </p>
      <router-link to="/upload" class="btn-primary">
         Déposer une image
      </router-link>
    </section>

    <section class="features">
      <div class="card feature-card">
        <h3> <strong>Géolocalisation</strong></h3>
        <p>Identifiez et suivez les lieux de dépôts sauvages.</p>
      </div>
      <div class="card feature-card">
        <h3> <strong>IA & Reconnaissance</strong></h3>
        <p>Analyse intelligente des images envoyées.</p>
      </div>
      <div class="card feature-card">
        <h3> <strong>Tableau de bord</strong></h3>
        <p>Visualisation claire et intuitive des données.</p>
      </div>
    </section>
  </div>
</template>

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

.dark-theme .feature-card {
  background-color: #1f2937;
  color: #f1f1f1;
}
</style>
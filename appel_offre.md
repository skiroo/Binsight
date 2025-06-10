# VISIO - Vision Intelligente de Suivi et d'Identification des Ordures

## Thème : Image Processing

## Mot-clé :
- WDP
- IA
- Data

### Quel problème / défi l'appel d'offre abordera-t-il ?
Face au manque de données précises sur les déchets dits abandonnés et à l’urgence d’agir pour limiter leur prolifération, le projet Wild Dump Prevention (WDP) propose une approche innovante visant à dresser un état des lieux aussi exhaustif que possible de la problématique des déchets sauvages. S’appuyant sur la démarche AI for Good, WDP vise non seulement à cartographier les dépôts existants, mais surtout à anticiper l’apparition de nouveaux sites de dépôt, en se concentrant notamment sur les zones où les poubelles débordent fréquemment, car elles deviennent souvent des points de départ de dépôts sauvages.
Ainsi, dans un contexte où le volet préventif se limite encore trop souvent à des actions de sensibilisation ou de formation, l’IA peut offrir une capacité de prédiction accrue, permettant une meilleure anticipation des risques de débordement et contribuant à la réduction des déchets abandonnés dans l’espace public.
Le manque de suivi en temps réel de l’état des infrastructures de collecte (poubelles, conteneurs) entraîne souvent une réaction tardive de la part des services municipaux ou des prestataires privés responsables. Cela favorise l’apparition de comportements inciviques.
Lorsque les débordements ne sont pas détectés rapidement, les déchets s’accumulent dans l’espace public, dégradent le cadre de vie et peuvent rapidement se transformer en dépôts sauvages difficiles à maîtriser. De plus, la diversité des lieux et des contextes rend la planification des tournées de ramassage plus complexe.

### Objectif de l'appel d'offre
Développer une plateforme intelligente de détection de l’état des poubelles publiques (pleines ou débordantes, vides) à partir d’images collectées sur le terrain pour améliorer la gestion des déchets urbains et la prévention des dépôts sauvages 
Quel est le contexte /  tendance actuelle dans le domaine ? Dans quelle mesure  l'appel d'offre changera-t-il la situation actuelle (veuillez quantifier l’objectif en volume ou en valeur).
Aujourd’hui, très peu d’initiatives permettent une surveillance proactive des dispositifs de collecte. La maintenance des bacs est souvent déclenchée trop tard, une fois le problème devenu visible dans l’espace public. Ce projet propose une alternative numérique simple, peu coûteuse et plus efficace, capable d’améliorer la performance du service public de gestion des déchets en s’appuyant sur des données de terrain. Il permettra de prédire avec précision les zones à risque et d’anticiper les périodes les plus propices à l’apparition de dépôts.

### Quels principaux résultats de l'appel d'offre sont attendus pour réaliser cette plus-value ?
Une plateforme web capable de :
- Collecter des images de poubelles via upload citoyen, agent, caméra embarquée
- Détecter automatiquement leur état (pleine, vide) à partir de caractéristiques visuelles simples
- Enrichir les données collectées avec des métadonnées (localisation, date, caractéristiques d’image)
- Cartographier dynamiquement les zones à risque de débordement

### Développement de la solution attendue(must have; should have; could have)

**Niveau 1 - Basique (Must)**
- Mise en place d’une plateforme web simple (upload, affichage image, annotation), utilisation d’outils existants pour annotation comme par exemple Scalabel
- Détermination des caractéristiques de base (taille, dimensions, couleur) et leur stockage dans une base de données
- Définir des règles conditionnelles de classification codées en dur (directement intégrées dans le code).
- Visualisation des statistiques basiques (matplotlib).

**Niveau 2 – Intermédiaire (Should)**
- Développement complet de l’interface d’annotation UX : navigation entre les images, raccourcis claviers, etc
- Extension des caractéristiques extraites avancées comme (histogrammes, contraste, contours, etc.).
- Définir des règles de classification configurables via l’interface  avec une sauvegarde dynamique dans la base.
- Tableau de bord interactif avec graphes dynamiques (Chart.js) et filtres.
 
**Niveau 3 – Avancé (could have)**
- Intégration de module de vérification de la conformité des données stockées dans une base
- Développement d’un tableau de bord avancé avec des indicateurs en temps réel, via des technologies telles que WebSocket ou AJAX. Ces indicateurs incluent notamment la localisation, la population, les jours de marché, les déclarations de travaux BTP, la météo, le jour de la semaine et la date d’acquisition des images, afin de cartographier dynamiquement les zones à risque de débordement.
- Optimisation de performance (compression image, gestion mémoire interne, gestion asynchrone de l'upload et de l'extraction de features pour ne pas bloquer l'interface, pagination pour les listes d'images, optimisation des requêtes BDD, etc.).
- Optimisation des performances : compression des images, gestion de la mémoire interne, gestion asynchrone de l’upload et de l’extraction des caractéristiques pour ne pas bloquer l’interface, pagination des listes d’images, optimisation des requêtes vers la BDD, etc
- Version multilingue de la plateforme.

### Exigences Fonctionnelles : Quelles fonctionnalités ou capacités doivent être incluses dans la solution proposée ? Soyez le plus précis possible
Ce projet intègre l’IA afin de mettre en place une plateforme web capable de :
- Collecter des images de poubelles (via upload et stockage)
- Proposer une interface d’annotation manuelle (pleine / vide)
- Extraire automatiquement des caractéristiques simples (dimensions, taille du fichier, couleur moyenne, histogrammes, contraste, contours, etc.)

### Exigences Techniques : Quelles technologies doivent être utilisées ? Quels sont les langages de programmation, les frameworks, les bases de données, etc., requis ?
- **Back-end :** Python (Flask,  Django, etc.),
- **Gestion des images :** Pillow, os, shutil,…
- Base de données : SQLite / PostgreSQL,…
- Front-end : HTML/CSS + Bootstrap (ou autre), Chart.js (pour les graphes dynamiques),
- Visualisation : matplotlib (Python) ou Chart.js (web).

### Critères d'Évaluation : Comment les soumissions seront-elles évaluées ? Quels sont les critères de sélection utilisés ?
Trame d’évaluation technique
- Rappel de l’appel d’offre (2 points)
  - Contexte : Décrire le contexte général du projet.
  - Problématique : Définir la problématique spécifique à résoudre.

- Méthodologie (4 points)
  - Conception de la chaîne : Acquisition → annotation → stockage → traitement des données.
  - Pertinences des caractéristiques et des règles de classification choisies
- Implémentation et expérimentation (5 points)
  - Librairies et Framework utilisés (justification des choix techniques)
  - Détails des phases d’entrainement et de validation : Explication et interprétation de ces phases.
  - Fonctionnalités implémentées
  - Utilisation des règles configurables
  - UX du dashboard implémenté
  - Modularité / maintenabilité du code

- Résultats (5 points)
  - Résultats de la classification (Performance des modèles sur le jeu de données) : Taux de classification correcte avec des métriques adaptées à la classification (Accuracy, Precision, Recall,…)
  - Résultats de l’explicabilité (Evaluation des techniques d’explicabilité fournies par les modèles avec des exemples concrets)
  - Cartographie dynamiquement les zones à risque de débordement
  - Performance de la plateforme (temps de réponse)

- Démo (2 points)
  - Démonstration des différentes fonctionnalités du projet.

- Appréciation des Experts (2 points) : Innovation et Créativité, Impact Potentiel, Qualité de la Documentation

### Est-ce que le projet ou ses résultats auront un impact positif (sociétale/ environnemental) ?
Reduction de l'empreinte écologique de l'homme et le risque des dépôts sauvages par une action préventive efficace et une meilleure gestion des points de collecte officiels

Lien github de la base de données + Explication du projet :
https://github.com/AGhaziBla/Solution_Factory_Data.git 

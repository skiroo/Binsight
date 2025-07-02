-- Tables de la base de données
SELECT tablename
FROM pg_catalog.pg_tables
WHERE schemaname = 'public';

-- ==========Tables==========
-- 1. Utilisateurs
SELECT * FROM utilisateurs;

-- 2. Images uploadées
SELECT * FROM images;

-- 3. Caractéristiques des images
SELECT * FROM caracteristiques_image;

-- 4. Règles de classification
SELECT * FROM regles_classification;

-- 5. Statistiques globales
SELECT * FROM statistiques;

-- 6. Données de géolocalisation
SELECT * FROM localisation;




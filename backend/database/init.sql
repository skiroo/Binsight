CREATE DATABASE IF NOT EXISTS Poubelle;
USE Poubelle;

-- 1. Table des utilisateurs
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_utilisateur TEXT UNIQUE NOT NULL,
    email TEXT,
    mot_de_passe TEXT NOT NULL,
    role_user TEXT NOT NULL CHECK (role IN ('citoyen', 'agent', 'admin')),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    avatar_url TEXT
);

-- 2. Table des localisations
CREATE TABLE IF NOT EXISTS localisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    numero_rue TEXT,
    rue TEXT NOT NULL,
    ville TEXT NOT NULL,
    code_postal TEXT NOT NULL,
    pays TEXT NOT NULL,
    zone_description TEXT
);

-- 3. Table des images
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fichier_nom TEXT NOT NULL,
    chemin_stockage TEXT NOT NULL,
    date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    utilisateur_id INTEGER NOT NULL,
    source TEXT CHECK (source IN ('citoyen', 'agent', 'caméra')),
    etat_annot TEXT CHECK (etat_annot IN ('pleine', 'vide')),
    classification_auto TEXT,
    localisation_id INTEGER NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (localisation_id) REFERENCES localisations(id)
);

-- 4. Table des caractéristiques d'image
CREATE TABLE IF NOT EXISTS caracteristiques_image (
    id INTEGER PRIMARY KEY,
    taille_ko FLOAT NOT NULL,
    hauteur INTEGER NOT NULL,
    largeur INTEGER NOT NULL,
    moyenne_rouge INTEGER NOT NULL,
    moyenne_vert INTEGER NOT NULL,
    moyenne_bleu INTEGER NOT NULL,
    contraste FLOAT,
    histogramme TEXT,
    contours_detectes BOOLEAN,
    FOREIGN KEY (id) REFERENCES images(id)
);

-- 5. Table des règles de classification
CREATE TABLE IF NOT EXISTS regles_classification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_regle TEXT NOT NULL,
    description_rc TEXT,
    condition_rc TEXT NOT NULL,
    active BOOLEAN DEFAULT 1
);

-- 6. Table des statistiques
CREATE TABLE IF NOT EXISTS statistiques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_img DATE NOT NULL,
    localisation_id INTEGER NOT NULL,
    nb_images INTEGER,
    nb_vides INTEGER,
    nb_pleines INTEGER,
    FOREIGN KEY (localisation_id) REFERENCES localisations(id)
);

CREATE TABLE IF NOT EXISTS localisation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL FOREIGN KEY REFERENCES images(id),
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    numero_rue TEXT,
    nom_rue TEXT NOT NULL,
    ville TEXT NOT NULL,
    code_postal TEXT NOT NULL,
    pays TEXT NOT NULL,
);
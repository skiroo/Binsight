CREATE DATABASE Poubelle;
USE Poubelle;

CREATE TABLE utilisateurs (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom_utilisateur TEXT UNIQUE NOT NULL,
	email TEXT,
	mot_de_passe TEXT NOT NULL,
	role TEXT NOT NULL CHECK(role IN ('citoyen', 'agent', 'admin')),
	date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	avatar_url TEXT
);

CREATE TABLE images (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	fichier_nom TEXT NOT NULL,
	chemin_stockage TEXT NOT NULL,
	date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	utilisateur_id INTEGER NOT NULL,
	source TEXT CHECK(source IN ('citoyen', 'agent', 'caméra')),
	etat_annot TEXT CHECK(etat_annot IN ('pleine', 'vide')),
	classification_auto TEXT,
	localisation TEXT,
	FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

CREATE TABLE caracteristiques_image (
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
	FOREIGN KEY (id) REFERENCES images(id) ON DELETE CASCADE
);

CREATE TABLE regles_classification (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom_regle TEXT NOT NULL,
	description_rc TEXT,
	condition_rc TEXT NOT NULL,
	active BOOLEAN DEFAULT 1
);

CREATE TABLE statistiques (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	date DATE NOT NULL,
	nb_images INTEGER,
	nb_vides INTEGER,
	nb_pleines INTEGER,
	localisation TEXT
);

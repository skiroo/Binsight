from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# === Table des utilisateurs ===
class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text)
    mot_de_passe = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)  # citoyen / agent / admin
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

# === Table des images ===
class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    fichier_nom = db.Column(db.Text, nullable=False)
    chemin_stockage = db.Column(db.Text, nullable=False)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id', ondelete="CASCADE"), nullable=False)
    source = db.Column(db.Text)  # citoyen / agent / caméra
    etat_annot = db.Column(db.Text)  # annotation manuelle : pleine / vide
    classification_auto = db.Column(db.Text)  # dirty / clean

    utilisateur = db.relationship('Utilisateur', backref=db.backref('images', lazy=True))
    criticites = db.relationship("Criticite", back_populates="image", cascade="all, delete-orphan")

# === Table des caractéristiques extraites ===
class CaracteristiquesImage(db.Model):
    __tablename__ = 'caracteristiques_image'
    id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete="CASCADE"), primary_key=True)
    taille_ko = db.Column(db.Float, nullable=False)
    hauteur = db.Column(db.Integer, nullable=False)
    largeur = db.Column(db.Integer, nullable=False)
    moyenne_rouge = db.Column(db.Integer, nullable=False)
    moyenne_vert = db.Column(db.Integer, nullable=False)
    moyenne_bleu = db.Column(db.Integer, nullable=False)
    contraste = db.Column(db.Float)
    histogramme = db.Column(db.Text)
    contours_detectes = db.Column(db.Boolean)
    luminance_moyenne = db.Column(db.Float)
    dark_pixel_ratio = db.Column(db.Float)
    texture_score = db.Column(db.Float)

    image = db.relationship('Image', backref=db.backref('caracteristiques', uselist=False))

# === Table des règles de classification ===
class RegleClassification(db.Model):
    __tablename__ = 'regles_classification'
    id = db.Column(db.Integer, primary_key=True)
    nom_regle = db.Column(db.Text, nullable=False)
    description_rc = db.Column(db.Text)
    condition_rc = db.Column(db.Text, nullable=False)  # Ex: "moyenne_rouge < 100 AND taille_ko > 2000"
    active = db.Column(db.Boolean, default=True)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes_regles.id'))

class GroupeRegles(db.Model):
    __tablename__ = 'groupes_regles'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    regles = db.relationship('RegleClassification', backref='groupe', lazy=True)

# === Table de localisation ===
class Localisation(db.Model):
    __tablename__ = 'localisation'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete="CASCADE"), nullable=False, unique=True)

    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    numero_rue = db.Column(db.Text)
    nom_rue = db.Column(db.Text)
    ville = db.Column(db.Text)
    code_postal = db.Column(db.Text)
    pays = db.Column(db.Text)
    quartier = db.Column(db.Text)

    image = db.relationship('Image', backref=db.backref('localisation', uselist=False, cascade="all, delete"))

# === Table des clés d'accès ===
class CleAcces(db.Model):
    __tablename__ = 'cles_acces'
    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.Text, unique=True, nullable=False)
    valide = db.Column(db.Boolean, default=True)
    role = db.Column(db.Text, default='agent')

# === Table des criticités ===
class Criticite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    etat = db.Column(db.String(20))
    pluie = db.Column(db.Float)
    criticite = db.Column(db.Integer)  # de 0 (faible) à 3 (critique)

    image = db.relationship("Image", back_populates="criticites")

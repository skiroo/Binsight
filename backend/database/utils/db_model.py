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
    avatar_url = db.Column(db.Text)

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
    classification_auto = db.Column(db.Text)  # pleine / vide

    utilisateur = db.relationship('Utilisateur', backref=db.backref('images', lazy=True))

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

# === Table des statistiques globales ===
class Statistique(db.Model):
    __tablename__ = 'statistiques'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    nb_images = db.Column(db.Integer)
    nb_vides = db.Column(db.Integer)
    nb_pleines = db.Column(db.Integer)
    localisation = db.Column(db.Text)

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

    image = db.relationship('Image', backref=db.backref('localisation', uselist=False, cascade="all, delete"))

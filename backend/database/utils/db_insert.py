import os
from datetime import datetime
from database.utils.db_model import db, Image, CaracteristiquesImage, Utilisateur, RegleClassification, Localisation
from app.extensions import bcrypt
from app.utils.rules import appliquer_regles_sur_image
from app.utils.extract_caract import extraire_caracteristiques

# === Utilisateur ===
def ajouter_utilisateur(nom_utilisateur, email, mot_de_passe, role="citoyen", avatar_url=None):
    hashed_pw = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        email=email,
        mot_de_passe=hashed_pw,
        role=role,
        avatar_url=avatar_url
    )
    db.session.add(utilisateur)
    db.session.commit()
    return utilisateur

# === Image ===
def enregistrer_image(image_path, utilisateur_id=1, source='citoyen'):
    filename = os.path.basename(image_path)
    image = Image(
        fichier_nom=filename,
        chemin_stockage=image_path,
        date_upload=datetime.utcnow(),
        utilisateur_id=utilisateur_id,
        source=source
    )
    db.session.add(image)
    db.session.commit()
    return image

# === Caractéristiques d'image ===
def enregistrer_caracteristiques(image_id, features):
    caract = CaracteristiquesImage(
        id=image_id,
        taille_ko=features['taille_ko'],
        hauteur=features['hauteur'],
        largeur=features['largeur'],
        moyenne_rouge=features['moyenne_rouge'],
        moyenne_vert=features['moyenne_vert'],
        moyenne_bleu=features['moyenne_bleu'],
        contraste=features['contraste'],
        histogramme=features['histogramme'],
        contours_detectes=features['contours_detectes'],
        luminance_moyenne=features['luminance_moyenne'],
        dark_pixel_ratio=features['dark_pixel_ratio'],
        texture_score=features['texture_score']
    )
    db.session.add(caract)
    db.session.commit()

# === Règle de classification ===
def ajouter_regle(nom_regle, condition_rc, description="", active=True):
    regle = RegleClassification(
        nom_regle=nom_regle,
        condition_rc=condition_rc,
        description_rc=description,
        active=active
    )
    db.session.add(regle)
    db.session.commit()
    return regle

# === Localisation ===
def ajouter_localisation(image_id, longitude, latitude, numero_rue, nom_rue, ville, code_postal, pays, quartier=None):
    loc = Localisation(
        image_id=image_id,
        longitude=longitude,
        latitude=latitude,
        numero_rue=numero_rue,
        nom_rue=nom_rue,
        ville=ville,
        code_postal=code_postal,
        pays=pays,
        quartier=quartier
    )
    db.session.add(loc)
    db.session.commit()
    return loc

# === Traitement complet d'une image ===
def traiter_image(image_path, utilisateur_id=1, source='citoyen'):
    # 1. Extraire les caractéristiques
    features = extraire_caracteristiques(image_path)

    # 2. Enregistrer l'image
    image = enregistrer_image(image_path, utilisateur_id, source)

    # 3. Enregistrer les caractéristiques
    enregistrer_caracteristiques(image.id, features)

    # 4. Appliquer les règles présentes en base
    label, msg = appliquer_regles_sur_image(image.id)

    return image.id, label, msg


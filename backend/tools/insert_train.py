import os
import random
from datetime import datetime
from flask import Flask
from database.utils.db_model import db, Image, Localisation, CaracteristiquesImage
from app.utils.extract_caract import extraire_caracteristiques
from app.utils.rules import appliquer_regles_sur_image

def random_latlon():
    lat = round(random.uniform(48.82, 48.90), 6)
    lon = round(random.uniform(2.27, 2.41), 6)
    return lat, lon

def extraire_caract_pour_images(ids):
    for image_id in ids:
        img = Image.query.get(image_id)
        if not img:
            print(f"Image id {image_id} non trouvée")
            continue
        if CaracteristiquesImage.query.get(image_id):
            print(f"Caractéristiques déjà présentes pour image {image_id}")
            continue
        
        chemin = img.chemin_stockage
        if not os.path.exists(chemin):
            print(f"Fichier image manquant : {chemin}")
            continue
        
        caract = extraire_caracteristiques(chemin)
        if caract:
            caract_obj = CaracteristiquesImage(
                id=image_id,
                taille_ko=caract['taille_ko'],
                hauteur=caract['hauteur'],
                largeur=caract['largeur'],
                moyenne_rouge=caract['moyenne_rouge'],
                moyenne_vert=caract['moyenne_vert'],
                moyenne_bleu=caract['moyenne_bleu'],
                contraste=caract['contraste'],
                histogramme=caract['histogramme'],
                contours_detectes=caract['contours_detectes'],
                luminance_moyenne=caract['luminance_moyenne'],
                dark_pixel_ratio=caract['dark_pixel_ratio'],
                texture_score=caract['texture_score']
            )
            db.session.add(caract_obj)
            db.session.commit()
            print(f"Caractéristiques extraites pour image {image_id}")
        else:
            print(f"Erreur extraction caractéristiques image {image_id}")

def appliquer_classification_auto(ids):
    for image_id in ids:
        classe_auto, msg = appliquer_regles_sur_image(image_id)
        img = Image.query.get(image_id)
        if img:
            img.classification_auto = classe_auto
            db.session.commit()
            print(f"Classification auto appliquée à image {image_id} : {classe_auto}")
        else:
            print(f"Image id {image_id} non trouvée pour classification")

def reparer_dernieres_images(app):
    with app.app_context():
        ids = list(range(673, 713))  # IDs 673 à 712 inclus
        print(f"Traitement des images IDs: {ids[0]} à {ids[-1]}")
        extraire_caract_pour_images(ids)
        appliquer_classification_auto(ids)
        print("Réparation terminée.")

if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://poubelle_db_pd0z_user:phy1gGsk1Wgrhx0TtbZOlJGnUVORGXVT@dpg-d1i4bundiees738toq1g-a.frankfurt-postgres.render.com/poubelle_db_pd0z'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    reparer_dernieres_images(app)

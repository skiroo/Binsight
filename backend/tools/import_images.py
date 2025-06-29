import os
from datetime import datetime, timezone
from PIL import Image as PILImage
import numpy as np

from app.app import create_app
from model.models import db, Image, CaracteristiquesImage
from app.utils.rules import appliquer_regles_sur_image

# Dossier d'où importer les images
IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'train', 'with_label'))


print("Contenu du dossier :", os.listdir(IMAGE_DIR))

def allowed_file(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.png'))

# Fonction pour extraire les caractéristiques simples d'une image
def extraire_caracteristiques(image_path):
    with PILImage.open(image_path) as img:
        img = img.convert('RGB')
        np_img = np.array(img)
        hauteur, largeur = img.height, img.width
        moyenne_rouge = int(np.mean(np_img[:, :, 0]))
        moyenne_vert = int(np.mean(np_img[:, :, 1]))
        moyenne_bleu = int(np.mean(np_img[:, :, 2]))
        taille_ko = round(os.path.getsize(image_path) / 1024, 2)
        return {
            'taille_ko': taille_ko,
            'hauteur': hauteur,
            'largeur': largeur,
            'moyenne_rouge': moyenne_rouge,
            'moyenne_vert': moyenne_vert,
            'moyenne_bleu': moyenne_bleu
        }

# Fonction principale d'importation
def importer_images():
    app = create_app()

    images_traitees = 0     # total d'images lues
    images_enregistree = 0    # images réellement ajoutées en base

    with app.app_context():
        for root, _, files in os.walk(IMAGE_DIR):
            for filename in files:
                if not allowed_file(filename):
                    continue

                images_traitees += 1
                image_path = os.path.join(root, filename)
                print(f"Traitement : {filename}")

                # Vérifie si l'image est déjà en base
                if Image.query.filter_by(fichier_nom=filename).first():
                    print(f"[SKIP] {filename} déjà en base")
                    continue

                # Étape 1 : créer l’image en base
                image = Image(
                    fichier_nom=filename,
                    chemin_stockage=image_path,
                    date_upload=datetime.now(timezone.utc),
                    utilisateur_id=1,
                    source='import'
                )
                db.session.add(image)
                db.session.commit()
                images_enregistree += 1
                print(f"[INSÉRÉ] image {image.id} enregistrée")

                # Étape 2 : extraire les caractéristiques
                features = extraire_caracteristiques(image_path)

                caract = CaracteristiquesImage(
                    id=image.id,
                    taille_ko=features['taille_ko'],
                    hauteur=features['hauteur'],
                    largeur=features['largeur'],
                    moyenne_rouge=features['moyenne_rouge'],
                    moyenne_vert=features['moyenne_vert'],
                    moyenne_bleu=features['moyenne_bleu']
                )
                db.session.add(caract)
                db.session.commit()

                # Étape 3 : classification automatique par règles
                label, _ = appliquer_regles_sur_image(image.id)
                print(f"[OK] {filename} → {label}")

    print(f"\n✅ Total d’images traitées : {images_traitees}")
    print(f"✅ Total d’images enregistrée : {images_enregistree}")

if __name__ == '__main__':
    importer_images()

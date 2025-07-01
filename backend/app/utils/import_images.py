import os

from app.app import create_app
from database.utils.db_model import *
from database.utils.db_insert import *

IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'train', 'with_label'))

print("Contenu du dossier :", os.listdir(IMAGE_DIR))

def allowed_file(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.png'))

def importer_images():
    app = create_app()
    images_traitees = 0
    images_enregistree = 0

    with app.app_context():
        for root, _, files in os.walk(IMAGE_DIR):
            for filename in files:
                if not allowed_file(filename):
                    continue

                images_traitees += 1
                image_path = os.path.join(root, filename)
                print(f"Traitement : {filename}")

                if Image.query.filter_by(fichier_nom=filename).first():
                    print(f"[SKIP] {filename} déjà en base")
                    continue

                image_id, label, msg = traiter_image(image_path, utilisateur_id=1, source='import')
                images_enregistree += 1
                print(f"[OK] {filename} → {label}")

    print(f"\n✅ Total d’images traitées : {images_traitees}")
    print(f"✅ Total d’images enregistrée : {images_enregistree}")


if __name__ == '__main__':
    importer_images()

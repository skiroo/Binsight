import os
import pandas as pd
from database.utils.db_model import db
from database.utils.db_insert import traiter_image, ajouter_localisation
from flask import Flask

# === CONFIGURATION ===
# Configure Flask app to connect to PostgreSQL on Render
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://poubelle_db_pd0z_user:phy1gGsk1Wgrhx0TtbZOlJGnUVORGXVT@dpg-d1i4bundiees738toq1g-a.frankfurt-postgres.render.com/poubelle_db_pd0z'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# === PARAMÈTRES ===
# Racine du projet (remonte de /backend/tools → ../..)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Chemin complet vers le dossier des images
IMAGE_FOLDER = os.path.join(BASE_DIR, 'data', 'test')
CSV_FILE = os.path.join(os.path.dirname(__file__), 'annotations_test.csv')
UTILISATEUR_ID = 1  # à adapter selon ton système

# === TRAITEMENT GLOBAL ===
with app.app_context():
    df = pd.read_csv(CSV_FILE, sep=';')  # séparateur correct

    for _, row in df.iterrows():
        image_name = row['filename']
        image_path = os.path.join(IMAGE_FOLDER, image_name)

        if not os.path.exists(image_path):
            print(f"Image introuvable : {image_name}")
            continue

        try:
            # 1. Extraire / enregistrer / classifier automatiquement
            image_id, label, msg = traiter_image(image_path, utilisateur_id=UTILISATEUR_ID)

            # 2. Ajouter l'annotation manuelle si différente
            from database.utils.db_model import Image
            image_obj = Image.query.get(image_id)
            image_obj.etat_annot = row['annotation_manuel']  # clean/dirty
            db.session.commit()

            # 3. Ajouter la localisation
            ajouter_localisation(
                image_id=image_id,
                longitude=row['longitude'],
                latitude=row['latitude'],
                numero_rue='',
                nom_rue='',
                ville='',
                code_postal='',
                pays=''
            )

            print(f"✅ Image {image_name} traitée → ID {image_id} | Auto: {label} | Manu: {row['annotation_manuel']}")

        except Exception as e:
            print(f"❌ Erreur pour {image_name} :", e)

import os
import csv
from PIL import Image as PILImage
import numpy as np

# Définition des chemins de base
BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), 'image_features_all.csv'))

# Dossiers à parcourir avec label associé
DATASETS = {
    'train/with_label/clean': 'clean',
    'train/with_label/dirty': 'dirty',
}

# Fonction pour extraire les caractéristiques
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

# Création du CSV
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['fichier', 'label', 'taille_ko', 'hauteur', 'largeur', 'moyenne_rouge', 'moyenne_vert', 'moyenne_bleu']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for relative_path, label in DATASETS.items():
        folder_path = os.path.join(BASE_DATA_DIR, relative_path)
        if not os.path.exists(folder_path):
            print(f"[ATTENTIOIN] Dossier introuvable : {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(folder_path, filename)
                try:
                    features = extraire_caracteristiques(full_path)
                    features.update({'fichier': filename, 'label': label})
                    writer.writerow(features)
                    print(f"[OK] {label} → {filename}")
                except Exception as e:
                    print(f"[ERREUR] {label} → {filename} : {e}")

print(f"\n✅ Fichier CSV généré : {OUTPUT_CSV}")

import os
import csv
from datetime import datetime
from app.utils.extract_caract import extraire_caracteristiques

# Définition des chemins de base
BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), 'image_features_all.csv'))

# Dossiers à parcourir avec label associé
DATASETS = {
    'train/with_label/clean': 'clean',
    'train/with_label/dirty': 'dirty',
}

# Champs que l'on souhaite vraiment écrire dans le CSV
fieldnames = [
    'fichier', 'label',
    'taille_ko', 'hauteur', 'largeur',
    'moyenne_rouge', 'moyenne_vert', 'moyenne_bleu',
    'contraste', 'luminance_moyenne', 'dark_pixel_ratio',
    'texture_score', 'nombre_contours'
]

# Création du fichier CSV
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for relative_path, label in DATASETS.items():
        folder_path = os.path.join(BASE_DATA_DIR, relative_path)
        if not os.path.exists(folder_path):
            print(f"[ATTENTION] Dossier introuvable : {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(folder_path, filename)
                try:
                    features = extraire_caracteristiques(full_path)
                    features.update({
                        'fichier': filename,
                        'label': label,
                    })

                    # Ne conserver que les champs listés dans fieldnames
                    filtered_features = {k: features[k] for k in fieldnames if k in features}

                    writer.writerow(filtered_features)
                    print(f"[OK] {label} → {filename}")
                except Exception as e:
                    print(f"[ERREUR] {label} → {filename} : {e}")

print(f"\n✅ Fichier CSV généré : {OUTPUT_CSV}")

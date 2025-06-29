import os
import numpy as np
import joblib
import csv
from PIL import Image as PILImage

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'test'))
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models')
RESULT_CSV = os.path.join(os.path.dirname(__file__), 'results', 'evaluation.csv')

def extraire_features(image_path):
    try:
        with PILImage.open(image_path) as img:
            img = img.convert('RGB').resize((100, 100))
            np_img = np.array(img)
            r, g, b = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2]
            return [
                np.mean(r), np.mean(g), np.mean(b),
                np.std(r), np.std(g), np.std(b),
                np.median(r), np.median(g), np.median(b)
            ]
    except:
        return None

model_files = sorted(os.listdir(MODEL_PATH))
if not model_files:
    raise ValueError("Aucun modèle trouvé dans 'models/'")

model = joblib.load(os.path.join(MODEL_PATH, model_files[-1]))

with open(RESULT_CSV, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['filename', 'prediction'])

    for filename in os.listdir(TEST_DIR):
        path = os.path.join(TEST_DIR, filename)
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        features = extraire_features(path)
        if not features:
            continue
        prediction = model.predict([features])[0]
        label = 'clean' if prediction == 0 else 'dirty'
        writer.writerow([filename, label])

print(f"✅ Résultats sauvegardés dans {RESULT_CSV}")
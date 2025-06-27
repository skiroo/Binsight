import os
import numpy as np
import joblib
from PIL import Image as PILImage
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Dossiers contenant les images labellisées
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'train', 'with_label'))
CATEGORIES = ['clean', 'dirty']

# Fonction pour extraire les features d'une image
def extraire_features(image_path):
    try:
        with PILImage.open(image_path) as img:
            img = img.convert('RGB')
            img = img.resize((100, 100))  # réduction pour simplifier
            np_img = np.array(img)
            r, g, b = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2]
            return [
                np.mean(r), np.mean(g), np.mean(b),
                np.std(r), np.std(g), np.std(b),
                np.median(r), np.median(g), np.median(b)
            ]
    except:
        return None

# Charger les données
X, y = [], []

for label, category in enumerate(CATEGORIES):
    folder = os.path.join(BASE_DIR, category)
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        features = extraire_features(path)
        if features:
            X.append(features)
            y.append(label)

print(f"Images chargées : {len(X)}")

# Entraînement du modèle
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Évaluation
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=CATEGORIES))

# Sauvegarde
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'modele_random_forest.pkl')
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Modèle entraîné et sauvegardé dans : {MODEL_PATH}")
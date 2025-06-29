import os
from datetime import datetime
import numpy as np
import joblib
import json
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay,
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'train', 'with_label'))
CATEGORIES = ['clean', 'dirty']
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

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

X, y = [], []
for label, category in enumerate(CATEGORIES):
    folder = os.path.join(BASE_DIR, category)
    if not os.path.exists(folder):
        continue
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        features = extraire_features(path)
        if features:
            X.append(features)
            y.append(label)

if not X:
    raise ValueError("Aucune image valide trouvée dans le dossier d'entraînement.")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'f1_score': f1_score(y_test, y_pred),
    'classification_report': classification_report(y_test, y_pred, target_names=CATEGORIES, output_dict=True)
}
with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=4)

cm_display = ConfusionMatrixDisplay.from_predictions(y_test, y_pred, display_labels=CATEGORIES)
plt.title("Matrice de confusion")
plt.savefig(os.path.join(RESULTS_DIR, "confusion_matrix.png"))
plt.close()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_path = os.path.join(MODEL_DIR, f'modele_rf_{timestamp}.pkl')
joblib.dump(model, model_path)
print(f"✅ Modèle sauvegardé : {model_path}")
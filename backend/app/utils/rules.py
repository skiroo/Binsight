from model.models import Image, CaracteristiquesImage, RegleClassification
from sqlalchemy.sql import text
import joblib
import os

# Charger le modèle IA s'il existe
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'modele_random_forest.pkl')
modele_ia = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def appliquer_regles_sur_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return None, f"Aucune image avec l'ID {image_id}"

    caract = CaracteristiquesImage.query.get(image_id)
    if not caract:
        return None, f"Aucune caractéristique pour l'image {image_id}"

    regles = RegleClassification.query.filter_by(active=True).all()
    if not regles:
        return None, "Aucune règle active trouvée."

    # Dictionnaire des attributs utilisables dans les règles
    contexte = {
        'taille_ko': caract.taille_ko,
        'hauteur': caract.hauteur,
        'largeur': caract.largeur,
        'moyenne_rouge': caract.moyenne_rouge,
        'moyenne_vert': caract.moyenne_vert,
        'moyenne_bleu': caract.moyenne_bleu
    }

    for regle in regles:
        try:
            if eval(regle.condition_rc, {}, contexte):
                image.classification_auto = regle.nom_regle
                return regle.nom_regle, f"Classé par règle : {regle.nom_regle}"
        except Exception as e:
            continue

    return None, "Aucune règle ne s'applique."

def classifier_avec_ia(features):
    if not modele_ia:
        return None, "Modèle IA non trouvé."

    vecteur = [
        features['moyenne_rouge'],
        features['moyenne_vert'],
        features['moyenne_bleu'],
        features.get('ecart_rouge', 0),
        features.get('ecart_vert', 0),
        features.get('ecart_bleu', 0),
        features.get('med_rouge', 0),
        features.get('med_vert', 0),
        features.get('med_bleu', 0)
    ]

    prediction = modele_ia.predict([vecteur])[0]
    label = 'vide' if prediction == 0 else 'pleine'
    return label, f"Classé par IA : {label}"

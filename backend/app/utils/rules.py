from database.utils.db_model import db, CaracteristiquesImage, RegleClassification, Image

def appliquer_regles_sur_image(image_id, groupe_id=None):
    # 1. Récupérer les caractéristiques de l’image
    caracteristiques = CaracteristiquesImage.query.get(image_id)
    if not caracteristiques:
        return None, "Caractéristiques non trouvées pour cette image."

    # 2. Construire le dictionnaire de variables accessibles
    variables = {
        'taille_ko': caracteristiques.taille_ko,
        'hauteur': caracteristiques.hauteur,
        'largeur': caracteristiques.largeur,
        'moyenne_rouge': caracteristiques.moyenne_rouge,
        'moyenne_vert': caracteristiques.moyenne_vert,
        'moyenne_bleu': caracteristiques.moyenne_bleu,
        'contraste': caracteristiques.contraste or 0,
        'luminance_moyenne': caracteristiques.luminance_moyenne or 0,
        'dark_pixel_ratio': caracteristiques.dark_pixel_ratio or 0,
        'texture_score': caracteristiques.texture_score or 0,
    }

    # 3. Charger les règles actives (filtrées par groupe si précisé)
    if groupe_id:
        regles = RegleClassification.query.filter_by(active=True, groupe_id=groupe_id).all()
    else:
        regles = RegleClassification.query.filter_by(active=True).all()

    if not regles:
        return None, "Aucune règle active trouvée."

    # 4. Appliquer chaque règle
    for regle in regles:
        try:
            if eval(regle.condition_rc, {}, variables):
                image = Image.query.get(image_id)
                image.classification_auto = regle.nom_regle.lower()
                db.session.commit()
                return regle.nom_regle.lower(), f"Classification : {regle.nom_regle}"
        except Exception as e:
            print(f"Erreur lors de l'évaluation de la règle {regle.nom_regle}: {e}")
            continue

    # 5. Si aucune règle ne s’applique
    image = Image.query.get(image_id)
    image.classification_auto = "non déterminé"
    db.session.commit()
    return "non déterminé", "Aucune règle applicable."
from app.app import create_app
from database.utils.db_model import db, RegleClassification

# Liste des règles à ajouter
regles = [
    {
        "nom": "dirty",
        "condition": "taille_ko > 300 and dark_pixel_ratio > 0.12",
        "description": "Image sombre et lourde → probablement pleine"
    },

    {
        "nom": "dirty",
        "condition": "luminance_moyenne < 116",
        "description": "Image globalement sombre → poubelle probablement pleine"
    },

    {
        "nom": "clean",
        "condition": "taille_ko <= 300 and dark_pixel_ratio < 0.1 and luminance_moyenne >= 118",
        "description": "Image légère, claire et peu sombre → probablement vide"
    },
    
    {
        "nom": "clean",
        "condition": "moyenne_rouge >= 118 and moyenne_vert >= 118",
        "description": "Couleurs claires → probablement propre"
    },
    
    {
        "nom": "dirty",
        "condition": "moyenne_rouge < 110 and moyenne_bleu < 105",
        "description": "Couleurs ternes et sombres → probablement pleine"
    }
]


def init_regles():
    app = create_app()
    with app.app_context():
        for r in regles:
            existe = RegleClassification.query.filter_by(condition_rc=r["condition"]).first()
            if not existe:
                regle = RegleClassification(
                    nom_regle=r["nom"],
                    condition_rc=r["condition"],
                    description_rc=r["description"],
                    active=True
                )
                db.session.add(regle)
                print(f"✅ Ajout : {r['nom']} → {r['condition']}")
        db.session.commit()
        print("✅ Toutes les règles ont été insérées avec succès.")

if __name__ == "__main__":
    init_regles()

from app.app import create_app  # importe ta factory Flask
from database.utils.db_model import db, GroupeRegles, RegleClassification

app = create_app()

with app.app_context():
    groupe = GroupeRegles(nom="defaut", description="règles pour images test")
    db.session.add(groupe)
    db.session.commit()

    regles = RegleClassification.query.limit(5).all()
    for regle in regles:
        regle.groupe_id = groupe.id
    db.session.commit()
    print("Groupe créé et règles associées.")

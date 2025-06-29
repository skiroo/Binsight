from app.app import create_app
from model.models import db, Utilisateur

app = create_app()

with app.app_context():
    if not Utilisateur.query.get(1):
        user = Utilisateur(
            id=1,
            nom_utilisateur='admin',
            email='admin@example.com',
            mot_de_passe='admin',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Utilisateur admin (id=1) créé.")
    else:
        print("ℹ️ Utilisateur admin (id=1) existe déjà.")

from app.app import create_app
from database.utils.db_model import *
from app.extensions import bcrypt  # <-- Ajoute ceci

app = create_app()

with app.app_context():
    if not Utilisateur.query.get(1):
        mot_de_passe_hash = bcrypt.generate_password_hash("admin").decode('utf-8')

        user = Utilisateur(
            id=1,
            nom_utilisateur='admin',
            email='admin@mail.com',
            mot_de_passe=mot_de_passe_hash,
            role='admin'
        )
        
        db.session.add(user)
        db.session.commit()
        print("✅ Utilisateur admin (id=1) créé.")
    else:
        print("ℹ️ Utilisateur admin (id=1) existe déjà.")

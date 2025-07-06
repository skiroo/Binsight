from app.app import create_app
from database.utils.db_model import db, CleAcces
import uuid

def ajouter_cle(cle_valeur):
    app = create_app()
    with app.app_context():
        if CleAcces.query.filter_by(cle=cle_valeur).first():
            print("❌ Clé déjà existante")
            return
        nouvelle_cle = CleAcces(cle=cle_valeur, role='agent')
        db.session.add(nouvelle_cle)
        db.session.commit()
        print("✅ Clé enregistrée :", cle_valeur)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        ajouter_cle(sys.argv[1])
    else:
        # Clé aléatoire par défaut
        cle = str(uuid.uuid4())
        ajouter_cle(cle)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from model.models import db

def create_app():

    # Charger les variables d'environnement depuis .env
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'database', '.env'))
    
    # Créer l'app Flask
    app = Flask(__name__)

    # Charger la config depuis config.py
    app.config.from_object('database.config.Config')

    # Initialiser SQLAlchemy avec l'app
    db.init_app(app)

    # Importer et enregistrer les routes
    from app.routes import routes
    app.register_blueprint(routes)

    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app

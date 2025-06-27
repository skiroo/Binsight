from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

from model.models import db

def create_app():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'database', '.env'))

    app = Flask(__name__)
    app.config.from_object('database.config.Config')

    db.init_app(app)

    # ✅ Autoriser frontend sur localhost:5173 et 127.0.0.1:5173
    CORS(app,
         resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
         supports_credentials=True)

    # ✅ Ajout manuel d'en-têtes CORS si nécessaire
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    from app.routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app
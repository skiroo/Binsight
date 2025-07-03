from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from database.utils.db_model import db
from app.extensions import bcrypt
from app.routes import routes
from app.auth_routes import auth_routes

def create_app():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'database', '.env'))

    app = Flask(__name__)   
    app.config.from_object('database.config.Config')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    CORS(app, origins=["http://localhost:5173"])

    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(routes)
    app.register_blueprint(auth_routes)

    with app.app_context():
        db.create_all()

    return app

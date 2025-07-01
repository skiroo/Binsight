from flask import Blueprint, request, jsonify
from app.extensions import bcrypt
from database.utils.db_model import db, Utilisateur
from database.utils.db_insert import ajouter_utilisateur

auth_routes = Blueprint('auth', __name__)

CLE_AGENT = "AGENT2025"

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nom = data.get('nom_utilisateur')
    email = data.get('email')
    pw = data.get('mot_de_passe')
    role = data.get('role', 'citoyen')
    access_key = data.get('access_key', '')

    if not all([nom, email, pw]):
        return jsonify({'error': 'Champs requis manquants'}), 400

    if role == 'admin':
        return jsonify({'error': 'Création admin interdite'}), 403

    if role == 'agent' and access_key != CLE_AGENT:
        return jsonify({'error': 'Clé d’accès invalide'}), 403

    if Utilisateur.query.filter_by(email=email).first():
        return jsonify({'error': 'Email déjà utilisé'}), 409

    user = ajouter_utilisateur(nom, email, pw, role)
    return jsonify({
        'id': user.id,
        'nom_utilisateur': user.nom_utilisateur,
        'role': user.role
    }), 201


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    pw = data.get('mot_de_passe')

    user = Utilisateur.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.mot_de_passe, pw):
        return jsonify({
            'id': user.id,
            'nom_utilisateur': user.nom_utilisateur,
            'role': user.role
        }), 200

    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

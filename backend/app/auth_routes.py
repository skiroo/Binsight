from flask import Blueprint, request, jsonify
from app.extensions import bcrypt
from database.utils.db_model import db, Utilisateur, CleAcces
from database.utils.db_insert import ajouter_utilisateur
import uuid

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nom = data.get('nom_utilisateur')
    email = data.get('email')
    pw = data.get('mot_de_passe')
    role = 'citoyen'  # valeur par défaut
    access_key = data.get('access_key', '').strip()

    if not all([nom, email, pw]):
        return jsonify({'error': 'Champs requis manquants'}), 400

    if Utilisateur.query.filter_by(email=email).first():
        return jsonify({'error': 'Email déjà utilisé'}), 409

    if access_key:
        cle = CleAcces.query.filter_by(cle=access_key, valide=True, role='agent').first()
        if cle:
            role = 'agent'
            cle.valide = False
            db.session.commit()
        else:
            return jsonify({'error': 'Clé d’accès invalide ou expirée'}), 403

    if role == 'admin':
        return jsonify({'error': 'Création admin interdite'}), 403

    user = ajouter_utilisateur(nom, email, pw, role)
    return jsonify({
        'id': user.id,
        'nom_utilisateur': user.nom_utilisateur,
        'role': user.role
    }), 201


@auth_routes.route('/verify_key', methods=['GET'])
def verify_key():
    cle = request.args.get('cle')
    if not cle:
        return jsonify({'valide': False})
    key = CleAcces.query.filter_by(cle=cle, valide=True, role='agent').first()
    return jsonify({'valide': bool(key)})


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

@auth_routes.route('/generate-agent-key', methods=['POST'])
def generate_agent_key():
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    cle = str(uuid.uuid4())
    new_key = CleAcces(cle=cle, role='agent')
    db.session.add(new_key)
    db.session.commit()

    return jsonify({"cle": cle})

@auth_routes.route('/access-keys', methods=['GET'])
def get_access_keys():
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    cles = CleAcces.query.all()
    return jsonify([
        {
            "id": c.id,
            "cle": c.cle,
            "valide": c.valide,
            "role": c.role
        }
        for c in cles
    ])

@auth_routes.route('/access-keys/<int:id>', methods=['PUT'])
def update_access_key(id):
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    cle = CleAcces.query.get(id)
    if not cle:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    cle.valide = data.get("valide", cle.valide)
    db.session.commit()
    return jsonify({"success": True})


@auth_routes.route('/access-keys/<int:id>', methods=['DELETE'])
def delete_access_key(id):
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    cle = CleAcces.query.get(id)
    if not cle:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(cle)
    db.session.commit()
    return jsonify({"success": True})

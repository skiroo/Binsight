# Libraries
from flask import *
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image as PILImage
import os
import numpy as np
from model.models import *

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Vérifie que l'image a une extension correcte
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fonction pour extraire les caractéristiques simples d'une image
def extraire_caracteristiques(image_path):
    with PILImage.open(image_path) as img:
        img = img.convert('RGB')
        np_img = np.array(img)
        hauteur, largeur = img.height, img.width

        moyenne_rouge = int(np.mean(np_img[:, :, 0]))
        moyenne_vert = int(np.mean(np_img[:, :, 1]))
        moyenne_bleu = int(np.mean(np_img[:, :, 2]))

        taille_ko = round(os.path.getsize(image_path) / 1024, 2)

        return {
            'taille_ko': taille_ko,
            'hauteur': hauteur,
            'largeur': largeur,
            'moyenne_rouge': moyenne_rouge,
            'moyenne_vert': moyenne_vert,
            'moyenne_bleu': moyenne_bleu
        }

# Route pour uploader une image et la classifier automatiquement
@routes.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Aucun fichier reçu'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Fichier invalide'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(save_path)

    features = extraire_caracteristiques(save_path)

    if features['moyenne_rouge'] < 100 and features['taille_ko'] > 2000:
        label = 'pleine'
    else:
        label = 'vide'

    image = Image(
        fichier_nom=filename,
        chemin_stockage=save_path,
        date_upload=datetime.utcnow(),
        utilisateur_id=1,  # À adapter
        source='citoyen',
        classification_auto=label
    )
    db.session.add(image)
    db.session.commit()

    caract = CaracteristiquesImage(
        id=image.id,
        taille_ko=features['taille_ko'],
        hauteur=features['hauteur'],
        largeur=features['largeur'],
        moyenne_rouge=features['moyenne_rouge'],
        moyenne_vert=features['moyenne_vert'],
        moyenne_bleu=features['moyenne_bleu']
    )
    db.session.add(caract)
    db.session.commit()

    return jsonify({
        'message': 'Image uploadée, analysée et classée automatiquement',
        'classification_auto': label
    })


# Route pour classifier une image existante
from app.utils.rules import appliquer_regles_sur_image

@routes.route('/classify/<int:image_id>', methods=['POST'])
def classify_image(image_id):
    label, message = appliquer_regles_sur_image(image_id)

    if label is None:
        return jsonify({'success': False, 'message': message}), 404

    return jsonify({
        'success': True,
        'image_id': image_id,
        'classification_auto': label,
        'message': message
    }), 200


# Route pour ajouter une localisation à une image
@routes.route('/localisation/<int:image_id>', methods=['POST'])
def ajouter_localisation(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'success': False, 'message': 'Image non trouvée'}), 404

    if image.localisation:
        return jsonify({'success': False, 'message': 'Localisation déjà existante'}), 400

    data = request.get_json()
    champs_attendus = ['longitude', 'latitude', 'numero_rue', 'nom_rue', 'ville', 'code_postal', 'pays']
    if not all(champ in data for champ in champs_attendus):
        return jsonify({'success': False, 'message': 'Champs manquants dans la requête'}), 400

    localisation = Localisation(
        image_id=image_id,
        longitude=data['longitude'],
        latitude=data['latitude'],
        numero_rue=data['numero_rue'],
        nom_rue=data['nom_rue'],
        ville=data['ville'],
        code_postal=data['code_postal'],
        pays=data['pays']
    )
    db.session.add(localisation)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Localisation ajoutée avec succès'})


# Route pour obtenir la liste des images avec caractéristiques + localisation
@routes.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    result = []

    for img in images:
        caract = img.caracteristiques
        loc = img.localisation

        result.append({
            'id': img.id,
            'fichier_nom': img.fichier_nom,
            'etat_annot': img.etat_annot,
            'classification_auto': img.classification_auto,
            'date_upload': img.date_upload.isoformat(),
            'caracteristiques': {
                'taille_ko': caract.taille_ko if caract else None,
                'moyenne_rouge': caract.moyenne_rouge if caract else None,
                'moyenne_vert': caract.moyenne_vert if caract else None,
                'moyenne_bleu': caract.moyenne_bleu if caract else None
            },
            'localisation': {
                'ville': loc.ville if loc else None,
                'code_postal': loc.code_postal if loc else None,
                'latitude': loc.latitude if loc else None,
                'longitude': loc.longitude if loc else None
            }
        })

    return jsonify(result)


# Route HTML : galerie
@routes.route('/galerie')
def galerie():
    images = Image.query.all()

    html = """
    <html>
    <head>
        <title>Galerie des images</title>
        <style>
            body { font-family: sans-serif; background: #f4f4f4; padding: 20px; }
            .image-box {
                display: inline-block;
                border: 2px solid #ccc;
                border-radius: 10px;
                margin: 10px;
                padding: 10px;
                background: white;
                width: 200px;
                vertical-align: top;
                text-align: center;
            }
            .pleine { border-color: red; }
            .vide { border-color: green; }
            img { max-width: 100%; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🗑️ Galerie des images classées</h1>
        {% for img in images %}
        <div class="image-box {{ img.classification_auto }}">
            <img src="/data/{{ img.chemin_stockage.split('data')[-1] }}" alt="{{ img.fichier_nom }}">
            <p><strong>{{ img.fichier_nom }}</strong></p>
            <p>
                {% if img.classification_auto %}
                    Classée : {{ img.classification_auto }}
                {% else %}
                    Non classée
                {% endif %}
            </p>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, images=images)


# Route pour servir les images via /data/<filename>
@routes.route('/data/<path:filename>')
def serve_data_image(filename):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return send_from_directory(os.path.join(root_path, 'data'), filename)


# Page d'accueil simple
@routes.route('/')
def home():
    return """
    <h1>VISIO</h1>
    <h2>Bienvenue sur l'API de la plateforme intelligente de suivi des poubelles</h2>
    """
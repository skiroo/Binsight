from flask import Blueprint, request, jsonify, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from model.models import db, Image, CaracteristiquesImage, Localisation
from datetime import datetime
from PIL import Image as PILImage
import numpy as np
import os

from app.utils.rules import appliquer_regles_sur_image, classifier_avec_ia

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

        ecart_rouge = float(np.std(np_img[:, :, 0]))
        ecart_vert = float(np.std(np_img[:, :, 1]))
        ecart_bleu = float(np.std(np_img[:, :, 2]))

        med_rouge = int(np.median(np_img[:, :, 0]))
        med_vert = int(np.median(np_img[:, :, 1]))
        med_bleu = int(np.median(np_img[:, :, 2]))

        taille_ko = round(os.path.getsize(image_path) / 1024, 2)

        return {
            'taille_ko': taille_ko,
            'hauteur': hauteur,
            'largeur': largeur,
            'moyenne_rouge': moyenne_rouge,
            'moyenne_vert': moyenne_vert,
            'moyenne_bleu': moyenne_bleu,
            'ecart_rouge': ecart_rouge,
            'ecart_vert': ecart_vert,
            'ecart_bleu': ecart_bleu,
            'med_rouge': med_rouge,
            'med_vert': med_vert,
            'med_bleu': med_bleu
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

    # Étape 1 : extraire les caractéristiques
    features = extraire_caracteristiques(save_path)

    # Étape 2 : appliquer la classification avec IA
    label, msg = classifier_avec_ia(features)

    # Étape 3 : enregistrer l'image dans la BDD
    image = Image(
        fichier_nom=filename,
        chemin_stockage=save_path,
        date_upload=datetime.utcnow(),
        utilisateur_id=1,  # à adapter plus tard
        source='citoyen',
        classification_auto=label
    )
    db.session.add(image)
    db.session.commit()

    # Étape 4 : enregistrer les caractéristiques
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
        'message': msg,
        'classification_auto': label
    })


# Route pour classifier une image existante
@routes.route('/classify/<int:image_id>', methods=['GET', 'POST'])
def classify_image(image_id):
    label, message = appliquer_regles_sur_image(image_id)

    if label is None:
        return jsonify({'success': False, 'message': message}), 404

    if request.method == 'GET':
        return jsonify({
            'message': 'Cette route doit être utilisée en POST pour une classification correcte.'
        })

    return jsonify({
        'success': True,
        'image_id': image_id,
        'classification_auto': label,
        'message': message
    }), 200


# Route pour annoter manuellement une image
@routes.route('/annotate/<int:image_id>', methods=['POST'])
def annotate_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image non trouvée'}), 404

    data = request.get_json()
    etat = data.get('etat')
    if etat not in ['pleine', 'vide']:
        return jsonify({'error': 'Valeur d’annotation invalide'}), 400

    image.etat_annot = etat
    db.session.commit()
    return jsonify({'message': f"Annotation enregistrée : {etat}"}), 200


# Route pour récupérer les stats globales
@routes.route('/stats', methods=['GET'])
def stats():
    total = Image.query.count()
    pleines = Image.query.filter_by(classification_auto='pleine').count()
    vides = Image.query.filter_by(classification_auto='vide').count()
    return jsonify({
        'total_images': total,
        'pleines': pleines,
        'vides': vides,
        'pleines_%': round(pleines / total * 100, 2) if total else 0,
        'vides_%': round(vides / total * 100, 2) if total else 0
    })


# Route pour réentraîner le modèle
@routes.route('/train', methods=['POST'])
def entrainer():
    os.system('python app/utils/train_model.py')
    return jsonify({'message': 'Modèle réentraîné'}), 200


# Route pour récupérer les image
@routes.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    result = [{
        'id': i.id,
        'fichier_nom': i.fichier_nom,
        'etat_annot': i.etat_annot,
        'classification_auto': i.classification_auto
    } for i in images]
    return jsonify(result)


# Route pour la page d'accueil
@routes.route('/')
def home():
    welcome = "<h1>VISIO</h1>" \
              "<h2>Bienvenue sur l'API de la plateforme intelligente de suivi des poubelles</h2>"
    return welcome

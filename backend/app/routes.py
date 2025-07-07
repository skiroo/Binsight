from flask import Blueprint, request, jsonify
from PIL import Image as PILImage
from werkzeug.utils import secure_filename
from datetime import datetime
import requests
import os

from app.utils.rules import appliquer_regles_sur_image
from app.extensions import bcrypt
from database.utils.db_model import db, Image, RegleClassification, CaracteristiquesImage, Utilisateur, Localisation
from database.utils.db_insert import traiter_image

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Aucun fichier reçu'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Fichier invalide'}), 400

    original_filename = secure_filename(file.filename)
    basename = os.path.splitext(original_filename)[0]
    filename = basename + ".webp"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    utilisateur_id = request.form.get("utilisateur_id")
    source = request.form.get("source", "citoyen")

    try:
        img = PILImage.open(file.stream).convert("RGB")
        img.thumbnail((1024, 1024))
        img.save(save_path, format='WEBP', quality=80, method=6)

        mode = request.form.get('mode_classification', 'auto')
        image_id, label, msg = traiter_image(save_path, utilisateur_id, source)

        if label == "non déterminé":
            msg = "Classification non déterminée. Veuillez annoter manuellement."

        annotation = request.form.get('annotation')
        rue_nom = request.form.get('rue_nom')
        rue_num = request.form.get('rue_num')
        cp = request.form.get('cp')
        ville = request.form.get('ville')
        pays = request.form.get('pays')
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        img_obj = Image.query.get(image_id)
        if img_obj:
            if annotation in ['dirty', 'clean']:
                img_obj.etat_annot = annotation
                db.session.commit()

            localisation = Localisation(
                image_id=image_id,
                nom_rue=rue_nom,
                numero_rue=rue_num,
                code_postal=cp,
                ville=ville,
                pays=pays,
                latitude=float(lat) if lat else None,
                longitude=float(lon) if lon else None
            )
            db.session.add(localisation)
            db.session.commit()

        return jsonify({
            'message': msg,
            'image_id': image_id,
            'classification_auto': label
        })

    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
            

@routes.route('/update/<int:image_id>', methods=['POST'])
def update_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image introuvable'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Aucune donnée reçue'}), 400

    etat = data.get('etat')
    loc = data.get('localisation')

    if etat in ['dirty', 'clean']:
        image.etat_annot = etat
        db.session.commit()

    if loc:
        localisation = Localisation.query.filter_by(image_id=image.id).first()
        if localisation:
            localisation.nom_rue = loc.get('rue_nom')
            localisation.numero_rue = loc.get('rue_num')
            localisation.code_postal = loc.get('cp')
            localisation.ville = loc.get('ville')
            localisation.pays = loc.get('pays')
            localisation.latitude = float(loc.get('lat')) if loc.get('lat') else None
            localisation.longitude = float(loc.get('lon')) if loc.get('lon') else None
        else:
            localisation = Localisation(
                image_id=image.id,
                nom_rue=loc.get('rue_nom'),
                numero_rue=loc.get('rue_num'),
                code_postal=loc.get('cp'),
                ville=loc.get('ville'),
                pays=loc.get('pays'),
                latitude=float(loc.get('lat')) if loc.get('lat') else None,
                longitude=float(loc.get('lon')) if loc.get('lon') else None
            )
            db.session.add(localisation)

        db.session.commit()

    return jsonify({'message': 'Image mise à jour avec succès'})


@routes.route('/delete_temp/<int:image_id>', methods=['DELETE'])
def delete_temp(image_id):
    img = Image.query.get(image_id)
    if img:
        db.session.delete(img)
        db.session.commit()
        try:
            os.remove(img.chemin_stockage)
        except Exception as e:
            print("Erreur suppression fichier :", e)
        return jsonify({'message': 'Image supprimée'}), 200
    return jsonify({'message': 'Image non trouvée'}), 404


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


@routes.route('/annotate/<int:image_id>', methods=['POST'])
def annotate_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image non trouvée'}), 404

    data = request.get_json()
    etat = data.get('etat')
    if etat not in ['dirty', 'clean']:
        return jsonify({'error': 'Valeur d’annotation invalide'}), 400

    image.etat_annot = etat
    db.session.commit()
    return jsonify({'message': f"Annotation enregistrée : {etat}"}), 200


@routes.route('/stats', methods=['GET'])
def stats():
    total = Image.query.count()
    pleines = Image.query.filter_by(classification_auto='dirty').count()
    vides = Image.query.filter_by(classification_auto='clean').count()
    non_annotees = Image.query.filter(Image.etat_annot == None).count()

    return jsonify({
        'total_images': total,
        'pleines': pleines,
        'vides': vides,
        'pleines_%': round(pleines / total * 100, 2) if total else 0,
        'vides_%': round(vides / total * 100, 2) if total else 0,
        'non_annotees': non_annotees
    })


@routes.route('/rules', methods=['GET'])
def get_rules():
    regles = RegleClassification.query.all()
    return jsonify([{
        'id': r.id,
        'nom': r.nom_regle,
        'condition': r.condition_rc,
        'active': r.active
    } for r in regles])


# === Ajouter une nouvelle règle ===
@routes.route('/rules', methods=['POST'])
def add_rule():
    data = request.get_json()
    nom = data.get('nom')
    condition = data.get('condition')
    description = data.get('description', "")
    active = data.get('active', True)

    if not nom or not condition:
        return jsonify({'error': 'Champs nom et condition obligatoires'}), 400

    rule = RegleClassification(
        nom_regle=nom,
        condition_rc=condition,
        description_rc=description,
        active=active
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({'message': 'Règle ajoutée', 'id': rule.id}), 201


# === Modifier une règle ===
@routes.route('/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    rule = RegleClassification.query.get(rule_id)
    if not rule:
        return jsonify({'error': 'Règle non trouvée'}), 404

    data = request.get_json()
    rule.nom_regle = data.get('nom', rule.nom_regle)
    rule.condition_rc = data.get('condition', rule.condition_rc)
    rule.description_rc = data.get('description', rule.description_rc)
    rule.active = data.get('active', rule.active)

    db.session.commit()
    return jsonify({'message': 'Règle mise à jour'})


# === Supprimer une règle ===
@routes.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    rule = RegleClassification.query.get(rule_id)
    if not rule:
        return jsonify({'error': 'Règle non trouvée'}), 404

    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': 'Règle supprimée'})


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


@routes.route('/verify', methods=['GET'])
def verify_data():
    erreurs = []

    # 1. Image sans fichier sur le disque
    images = Image.query.all()
    for img in images:
        if not os.path.exists(img.chemin_stockage):
            erreurs.append({
                'type': 'missing_file',
                'image_id': img.id,
                'fichier': img.fichier_nom,
                'message': 'Fichier manquant sur le disque'
            })

    # 2. Fichier sur disque mais pas en base
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
    fichiers = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    for f in fichiers:
        if not Image.query.filter_by(fichier_nom=f).first():
            erreurs.append({
                'type': 'orphan_file',
                'fichier': f,
                'message': 'Fichier présent sur disque mais pas en base'
            })

    # 3. Image sans caractéristiques
    ids_avec_caract = [c.id for c in CaracteristiquesImage.query.all()]
    for img in images:
        if img.id not in ids_avec_caract:
            erreurs.append({
                'type': 'missing_features',
                'image_id': img.id,
                'fichier': img.fichier_nom,
                'message': 'Aucune caractéristique trouvée'
            })

    # 4. Image sans annotation ET sans classification
    for img in images:
        if not img.etat_annot and not img.classification_auto:
            erreurs.append({
                'type': 'unusable_image',
                'image_id': img.id,
                'fichier': img.fichier_nom,
                'message': 'Image ni annotée ni classée'
            })

    # 5. Valeurs incohérentes
    for c in CaracteristiquesImage.query.all():
        if c.taille_ko < 1 or c.moyenne_rouge > 255 or c.moyenne_bleu > 255:
            erreurs.append({
                'type': 'invalid_features',
                'image_id': c.id,
                'message': 'Valeurs incohérentes détectées'
            })

    return jsonify({
        'total_images': len(images),
        'erreurs_detectees': len(erreurs),
        'details': erreurs
    })


@routes.route('/api/localisations', methods=['GET'])
def get_all_localisations():
    localisations = Localisation.query.join(Image).all()
    result = []

    for loc in localisations:
        if loc.latitude and loc.longitude:
            result.append({
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'etat_annot': loc.image.etat_annot,
                'fichier_nom': loc.image.fichier_nom,
                'ville': loc.ville,
                'quartier': loc.quartier,
                'id': loc.image_id
            })

    return jsonify(result)


def get_arrondissement_from_coords(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = { "User-Agent": "VISIO-Efrei/1.0" }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            addr = data.get('address', {})
            arrondissement = addr.get('suburb') or addr.get('city_district') or addr.get('municipality')
            return arrondissement
    except Exception as e:
        print("Erreur géocodage :", e)
    return None


# ============================================================================

@routes.route('/')
def home():
    return "<h1>VISIO</h1>" \
    "<h2>Bienvenue sur l'API de suivi intelligent des poubelles</h2>"

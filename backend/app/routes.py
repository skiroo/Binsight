from flask import Blueprint, Response, request, jsonify
from PIL import Image as PILImage
from werkzeug.utils import secure_filename
from sqlalchemy import and_
from datetime import datetime, timedelta
import requests
import csv, io
import os

from app.utils.rules import appliquer_regles_sur_image
from app.utils.criticite import calculer_criticite
from app.extensions import bcrypt
from database.utils.db_model import db, Image, RegleClassification, GroupeRegles, CaracteristiquesImage, Utilisateur, Localisation, Criticite
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
    groupe_id = request.form.get("groupe_id")

    try:
        # 1. Conversion et sauvegarde temporaire
        img = PILImage.open(file.stream).convert("RGB")
        img.thumbnail((1024, 1024))
        img.save(save_path, format='WEBP', quality=80, method=6)

        # 2. Traitement : caractéristiques + classification
        image_id, label, msg = traiter_image(save_path, utilisateur_id, source, groupe_id=groupe_id)
        if label == "non déterminé":
            msg = "Classification non déterminée. Veuillez annoter manuellement."

        # 3. Lecture des champs du formulaire
        annotation = request.form.get('annotation')
        rue_nom = request.form.get('rue_nom')
        rue_num = request.form.get('rue_num')
        cp = request.form.get('cp')
        ville = request.form.get('ville')
        pays = request.form.get('pays')
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        latitude = float(lat) if lat else None
        longitude = float(lon) if lon else None
        quartier = get_arrondissement_from_coords(latitude, longitude) if (latitude and longitude) else None

        # 4. Mise à jour de l'annotation manuelle (si donnée)
        img_obj = Image.query.get(image_id)
        if img_obj:
            if annotation in ['dirty', 'clean']:
                img_obj.etat_annot = annotation
                db.session.commit()

            # 5. Enregistrement de la localisation complète
            localisation = Localisation(
                image_id=image_id,
                nom_rue=rue_nom,
                numero_rue=rue_num,
                code_postal=cp,
                ville=ville,
                pays=pays,
                latitude=latitude,
                longitude=longitude,
                quartier=quartier
            )
            db.session.add(localisation)
            db.session.commit()

        # 🔁 Récupérer météo et calculer criticité
        pluie = None
        criticite = 0
        if latitude and longitude:
            try:
                météo_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=precipitation&timezone=auto"
                res = requests.get(météo_url)
                if res.ok:
                    data = res.json()
                    now = datetime.now().strftime('%Y-%m-%dT%H:00')
                    index = data['hourly']['time'].index(now)
                    pluie = data['hourly']['precipitation'][index]
                    criticite = calculer_criticite(img_obj.etat_annot or label, pluie)
            except Exception as e:
                print("Erreur météo :", e)

        # 🔁 Enregistrer criticité
        db.session.add(Criticite(
            image_id=image_id,
            etat=img_obj.etat_annot or label,
            pluie=pluie,
            criticite=criticite
        ))
        db.session.commit()

        return jsonify({
            'message': msg,
            'image_id': image_id,
            'classification_auto': label,
            'quartier': quartier,
            'criticite': criticite
        })

    finally:
        if os.path.exists(save_path):
            os.remove(save_path)


@routes.route('/api/criticite/<int:image_id>', methods=['GET'])
def get_criticite(image_id):
    crit = Criticite.query.filter_by(image_id=image_id).order_by(Criticite.date.desc()).first()
    if not crit:
        return jsonify({'error': 'Criticité non trouvée'}), 404
    return jsonify({
        'image_id': image_id,
        'etat': crit.etat,
        'pluie': crit.pluie,
        'criticite': crit.criticite,
        'date': crit.date.isoformat()
    })
            

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
        latitude = float(loc.get('lat')) if loc.get('lat') else None
        longitude = float(loc.get('lon')) if loc.get('lon') else None
        quartier = get_arrondissement_from_coords(latitude, longitude) if (latitude and longitude) else None

        localisation = Localisation.query.filter_by(image_id=image.id).first()
        if localisation:
            localisation.nom_rue = loc.get('rue_nom')
            localisation.numero_rue = loc.get('rue_num')
            localisation.code_postal = loc.get('cp')
            localisation.ville = loc.get('ville')
            localisation.pays = loc.get('pays')
            localisation.latitude = latitude
            localisation.longitude = longitude
            localisation.quartier = quartier
        else:
            localisation = Localisation(
                image_id=image.id,
                nom_rue=loc.get('rue_nom'),
                numero_rue=loc.get('rue_num'),
                code_postal=loc.get('cp'),
                ville=loc.get('ville'),
                pays=loc.get('pays'),
                latitude=latitude,
                longitude=longitude,
                quartier=quartier
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


@routes.route('/api/stats', methods=['GET'])
def stats():
    periode = request.args.get('periode', 'day')  # 'day', 'week', 'month' ou 'custom'
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')

    query = Image.query

    if periode == 'day':
        today = datetime.today().date()
        query = query.filter(db.func.date(Image.date_upload) == today)
    elif periode == 'week':
        week_ago = datetime.today().date() - timedelta(days=6)
        query = query.filter(db.func.date(Image.date_upload) >= week_ago)
    elif periode == 'month':
        month_ago = datetime.today().date() - timedelta(days=29)
        query = query.filter(db.func.date(Image.date_upload) >= month_ago)
    elif periode == 'custom' and date_min and date_max:
        try:
            dmin = datetime.strptime(date_min, '%Y-%m-%d').date()
            dmax = datetime.strptime(date_max, '%Y-%m-%d').date()
            query = query.filter(and_(
                db.func.date(Image.date_upload) >= dmin,
                db.func.date(Image.date_upload) <= dmax
            ))
        except ValueError:
            return jsonify({'error': 'Format de date invalide (attendu YYYY-MM-DD)'}), 400

    total = query.count()
    pleines = query.filter_by(classification_auto='dirty').count()
    vides = query.filter_by(classification_auto='clean').count()
    non_annotees = query.filter(Image.etat_annot == None).count()

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


@routes.route('/api/rule-groups', methods=['GET'])
def get_rule_groups():
    groupes = GroupeRegles.query.all()
    return jsonify([
        {
            'id': g.id,
            'nom': g.nom,
            'description': g.description,
            'nb_regles': len(g.regles)
        }
        for g in groupes
    ])


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
    localisations = db.session.query(Localisation).join(Image).outerjoin(Criticite).all()
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
                'id': loc.image_id,
                'date_upload': loc.image.date_upload.isoformat(),
                'source': loc.image.source,
                'criticite': loc.image.criticites[-1].criticite if loc.image.criticites else 0
            })

    return jsonify(result)


@routes.route('/api/localisations/today', methods=['GET'])
def get_today_localisations():
    today = datetime.today().date()
    localisations = Localisation.query.join(Image).filter(
        db.func.date(Image.date_upload) == today
    ).all()

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
                'id': loc.image_id,
                'date_upload': loc.image.date_upload.isoformat(),
                'source': loc.image.source,
            })

    return jsonify(result)


def get_arrondissement_from_coords(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = { "User-Agent": "Binsight-Efrei/1.0" }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            addr = data.get('address', {})
            arrondissement = addr.get('suburb') or addr.get('city_district') or addr.get('municipality')
            return arrondissement
    except Exception as e:
        print("Erreur géocodage :", e)
    return None


@routes.route('/api/alerts', methods=['GET'])
def get_alerts():
    seuil_poubelles = 5
    seuil_criticite_moyenne = 2
    seuil_criticite_max = 3

    alerts = []

    periode = request.args.get('periode', 'all')
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')

    # Sous-requête : on filtre les criticités reliées aux poubelles pleines
    subquery = db.session.query(
        Localisation.quartier.label("quartier"),
        db.func.count(Image.id).label("nb_dirty"),
        db.func.avg(Criticite.criticite).label("criticite_moy"),
        db.func.max(Criticite.criticite).label("criticite_max"),
        db.func.avg(Localisation.latitude).label("lat"),
        db.func.avg(Localisation.longitude).label("lon")
    ).join(Image, Image.id == Localisation.image_id) \
     .outerjoin(Criticite, Image.id == Criticite.image_id) \
     .filter(Image.etat_annot == 'dirty')

    # Périodes
    if periode == 'day':
        today = datetime.today().date()
        subquery = subquery.filter(db.func.date(Image.date_upload) == today)
    elif periode == 'week':
        week_ago = datetime.today().date() - timedelta(days=6)
        subquery = subquery.filter(db.func.date(Image.date_upload) >= week_ago)
    elif periode == 'month':
        month_ago = datetime.today().date() - timedelta(days=29)
        subquery = subquery.filter(db.func.date(Image.date_upload) >= month_ago)
    elif periode == 'custom' and date_min and date_max:
        try:
            dmin = datetime.strptime(date_min, '%Y-%m-%d').date()
            dmax = datetime.strptime(date_max, '%Y-%m-%d').date()
            subquery = subquery.filter(and_(
                db.func.date(Image.date_upload) >= dmin,
                db.func.date(Image.date_upload) <= dmax
            ))
        except ValueError:
            return jsonify({'alertes': [], 'seuil': seuil_poubelles})

    results = subquery.group_by(Localisation.quartier).all()

    for quartier, nb_dirty, criticite_moy, criticite_max, lat, lon in results:
        if quartier and nb_dirty >= seuil_poubelles:
            if criticite_max and criticite_max >= seuil_criticite_max or \
               criticite_moy and criticite_moy >= seuil_criticite_moyenne:
                alerts.append({
                    'quartier': quartier,
                    'nb_dirty': nb_dirty,
                    'criticite_moy': round(criticite_moy, 2) if criticite_moy else None,
                    'criticite_max': criticite_max,
                    'latitude': lat,
                    'longitude': lon
                })

    return jsonify({'alertes': alerts, 'seuil_poubelles': seuil_poubelles})


# === Ajouter un groupe de règles ===
@routes.route('/api/rule-groups', methods=['POST'])
def add_rule_group():
    data = request.get_json()
    nom = data.get('nom')
    description = data.get('description', '')

    if not nom:
        return jsonify({'error': 'Le champ nom est obligatoire'}), 400

    groupe = GroupeRegles(nom=nom, description=description)
    db.session.add(groupe)
    db.session.commit()
    return jsonify({'message': 'Groupe ajouté', 'id': groupe.id}), 201

# === Modifier un groupe de règles ===
@routes.route('/api/rule-groups/<int:group_id>', methods=['PUT'])
def update_rule_group(group_id):
    groupe = GroupeRegles.query.get(group_id)
    if not groupe:
        return jsonify({'error': 'Groupe non trouvé'}), 404

    data = request.get_json()
    groupe.nom = data.get('nom', groupe.nom)
    groupe.description = data.get('description', groupe.description)
    db.session.commit()
    return jsonify({'message': 'Groupe mis à jour'})

# === Supprimer un groupe de règles ===
@routes.route('/api/rule-groups/<int:group_id>', methods=['DELETE'])
def delete_rule_group(group_id):
    groupe = GroupeRegles.query.get(group_id)
    if not groupe:
        return jsonify({'error': 'Groupe non trouvé'}), 404

    # Optionnel : supprimer toutes les règles associées
    for regle in groupe.regles:
        db.session.delete(regle)
    db.session.delete(groupe)
    db.session.commit()
    return jsonify({'message': 'Groupe et règles associées supprimés'})


# === Lister les règles d’un groupe ===
@routes.route('/api/rule-groups/<int:group_id>/rules', methods=['GET'])
def get_rules_by_group(group_id):
    regles = RegleClassification.query.filter_by(groupe_id=group_id).all()
    return jsonify([{
        'id': r.id,
        'nom': r.nom_regle,
        'condition': r.condition_rc,
        'description': r.description_rc,
        'active': r.active
    } for r in regles])

# === Ajouter une règle dans un groupe ===
@routes.route('/api/rule-groups/<int:group_id>/rules', methods=['POST'])
def add_rule_to_group(group_id):
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
        active=active,
        groupe_id=group_id
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({'message': 'Règle ajoutée', 'id': rule.id}), 201

@routes.route('/export/custom', methods=['GET'])
def export_custom():
    tables = request.args.get('tables', '').split(',')
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    etat = request.args.get('etat')
    source = request.args.get('source')
    quartier = request.args.get('quartier')

    # Base query
    query = db.session.query(Image)\
        .outerjoin(CaracteristiquesImage)\
        .outerjoin(Localisation)\
        .outerjoin(Utilisateur)

    if date_min and date_max:
        try:
            dmin = datetime.strptime(date_min, '%Y-%m-%d').date()
            dmax = datetime.strptime(date_max, '%Y-%m-%d').date()
            query = query.filter(and_(
                db.func.date(Image.date_upload) >= dmin,
                db.func.date(Image.date_upload) <= dmax
            ))
        except:
            return jsonify({'error': 'Format de date invalide'}), 400

    if etat:
        query = query.filter(Image.etat_annot == etat)

    if source:
        query = query.filter(Image.source == source)
    if quartier:
        query = query.join(Localisation).filter(Localisation.quartier.ilike(f"%{quartier}%"))

    images = query.all()

    # Génération CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Définir les colonnes selon les tables cochées
    header = []
    if 'image' in tables:
        header += ['image_id', 'fichier_nom', 'etat_annot', 'date_upload']
    if 'caracteristiques' in tables:
        header += ['taille_ko', 'hauteur', 'largeur', 'moyenne_rouge', 'luminance_moyenne']
    if 'localisation' in tables:
        header += ['quartier', 'latitude', 'longitude', 'ville', 'code_postal']
    if 'utilisateur' in tables:
        header += ['utilisateur_id', 'nom_utilisateur', 'email', 'role']

    writer.writerow(header)

    for img in images:
        row = []

        if 'image' in tables:
            row += [img.id, img.fichier_nom, img.etat_annot, img.date_upload.isoformat()]

        if 'caracteristiques' in tables:
            c = img.caracteristiques
            row += [
                c.taille_ko if c else '',
                c.hauteur if c else '',
                c.largeur if c else '',
                c.moyenne_rouge if c else '',
                c.luminance_moyenne if c else ''
            ]

        if 'localisation' in tables:
            l = img.localisation
            row += [
                l.quartier if l else '',
                l.latitude if l else '',
                l.longitude if l else '',
                l.ville if l else '',
                l.code_postal if l else ''
            ]

        if 'utilisateur' in tables:
            u = img.utilisateur
            row += [
                u.id if u else '',
                u.nom_utilisateur if u else '',
                u.email if u else '',
                u.role if u else ''
            ]

        writer.writerow(row)

    output.seek(0)
    return Response(output, mimetype='text/csv', headers={
        "Content-Disposition": "attachment; filename=export_custom.csv"
    })

# ============================================================================

@routes.route('/')
def home():
    return "<h1>Binsight</h1>" \
    "<h2>Bienvenue sur l'API de suivi intelligent des poubelles</h2>"

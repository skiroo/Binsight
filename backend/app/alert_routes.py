from flask import Blueprint, jsonify
from database.utils.db_model import db, Image, Localisation

alert_bp = Blueprint('alert_bp', __name__)

@alert_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    seuil = 2
    results = db.session.query(Localisation.quartier, db.func.count(Image.id))\
        .join(Image).filter(Image.etat_annot == 'dirty')\
        .group_by(Localisation.quartier).all()

    alertes = [{"quartier": q, "nb_dirty": count} for q, count in results if count >= seuil]

    return jsonify({'alertes': alertes, 'seuil': seuil})

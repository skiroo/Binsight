from app.app import create_app
from database.utils.db_model import db, Localisation
import requests
import time

def get_arrondissement(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {"User-Agent": "VISIO-Efrei/1.0"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            addr = data.get("address", {})
            return addr.get("suburb") or addr.get("city_district") or addr.get("municipality")
    except Exception as e:
        print(f"❌ Erreur géocodage ({lat}, {lon}):", e)
    return None

def update_localisation_quartiers():
    app = create_app()
    with app.app_context():
        localisations = Localisation.query.filter(
            Localisation.latitude.isnot(None),
            Localisation.longitude.isnot(None),
            (Localisation.quartier.is_(None) | (Localisation.quartier == ''))
        ).all()

        print(f"🔍 {len(localisations)} localisations à mettre à jour...")

        for loc in localisations:
            arrondissement = get_arrondissement(loc.latitude, loc.longitude)
            if arrondissement:
                loc.quartier = arrondissement
                db.session.commit()
                print(f"✅ image_id={loc.image_id} → quartier='{arrondissement}'")
            else:
                print(f"⚠️ image_id={loc.image_id} : arrondissement non trouvé")

            time.sleep(1)  # Respect des règles Nominatim (1 req/sec max)

if __name__ == "__main__":
    update_localisation_quartiers()

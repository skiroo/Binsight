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
            Localisation.longitude.isnot(None)
        ).all()

        print(f"🔍 {len(localisations)} localisations à vérifier...")

        for loc in localisations:
            arrondissement = get_arrondissement(loc.latitude, loc.longitude)
            updated = False

            if arrondissement and loc.quartier != arrondissement:
                loc.quartier = arrondissement
                updated = True

            if not loc.ville or loc.ville.strip() == "":
                loc.ville = "Paris"
                updated = True

            if updated:
                db.session.commit()
                print(f"✅ image_id={loc.image_id} → quartier='{loc.quartier}' | ville='{loc.ville}'")
            else:
                print(f"⏭️ image_id={loc.image_id} déjà à jour")

            time.sleep(1)  # Respect Nominatim : 1 requête/sec

if __name__ == "__main__":
    update_localisation_quartiers()

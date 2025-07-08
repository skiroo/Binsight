import random
from datetime import datetime, timedelta
from flask import Flask
from database.utils.db_model import db, Localisation, Image

# Configuration Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://poubelle_db_pd0z_user:phy1gGsk1Wgrhx0TtbZOlJGnUVORGXVT@dpg-d1i4bundiees738toq1g-a.frankfurt-postgres.render.com/poubelle_db_pd0z'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Paramètres
ARRONDISSEMENTS = [f"Paris {i}e" for i in range(1, 21)]
NB_SEMAINES = 4
NB_PAR_ARR_SEMAINE = 7  # 7 images/arrondissement/semaine
DATE_DEBUT = datetime(2025, 6, 10)

def random_latlon():
    lat = round(random.uniform(48.82, 48.90), 6)
    lon = round(random.uniform(2.27, 2.41), 6)
    return lat, lon

def date_in_week(week_index):
    monday = DATE_DEBUT + timedelta(weeks=week_index)
    return monday + timedelta(days=random.randint(0, 6))

# Logique
with app.app_context():
    # Récupérer les localisations concernées
    locs = Localisation.query.filter(Localisation.image_id >= 106).order_by(Localisation.image_id).all()
    total = len(locs)
    random.shuffle(locs)

    max_images = NB_SEMAINES * len(ARRONDISSEMENTS) * NB_PAR_ARR_SEMAINE
    locs = locs[:max_images]
    
    index = 0
    compteur = 0

    for week in range(NB_SEMAINES):
        for arrondissement in ARRONDISSEMENTS:
            for _ in range(NB_PAR_ARR_SEMAINE):
                if index >= len(locs):
                    break
                loc = locs[index]
                loc.quartier = arrondissement
                loc.ville = "Paris"
                loc.latitude, loc.longitude = random_latlon()

                # mettre à jour la date de l'image liée
                image = Image.query.get(loc.image_id)
                if image:
                    image.date_upload = date_in_week(week)

                index += 1
                compteur += 1

    db.session.commit()
    print(f"✅ {compteur} localisations réparties équitablement sur 4 semaines et 20 arrondissements.")

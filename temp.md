# Binsight - Code et Explications

---

## 1. Route Flask `/upload`

Cette route gère l’upload d’image, sa conversion en format WEBP, sa sauvegarde temporaire, puis la classification automatique selon les règles configurables. Elle enregistre aussi la localisation et les annotations manuelles si présentes.

```python
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

        return jsonify({
            'message': msg,
            'image_id': image_id,
            'classification_auto': label,
            'quartier': quartier
        })

    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
```

---

## 2. Fonction appliquer_regles_sur_image

Cette fonction applique les règles actives (configurables) sur les caractéristiques extraites de l’image pour déterminer sa classification automatique.

```python
from database.utils.db_model import db, CaracteristiquesImage, RegleClassification, Image

def appliquer_regles_sur_image(image_id, groupe_id=None):
    caracteristiques = CaracteristiquesImage.query.get(image_id)
    if not caracteristiques:
        return None, "Caractéristiques non trouvées pour cette image."

    variables = {
        'taille_ko': caracteristiques.taille_ko,
        'hauteur': caracteristiques.hauteur,
        'largeur': caracteristiques.largeur,
        'moyenne_rouge': caracteristiques.moyenne_rouge,
        'moyenne_vert': caracteristiques.moyenne_vert,
        'moyenne_bleu': caracteristiques.moyenne_bleu,
        'contraste': caracteristiques.contraste or 0,
        'luminance_moyenne': caracteristiques.luminance_moyenne or 0,
        'dark_pixel_ratio': caracteristiques.dark_pixel_ratio or 0,
        'texture_score': caracteristiques.texture_score or 0,
    }

    if groupe_id:
        regles = RegleClassification.query.filter_by(active=True, groupe_id=groupe_id).all()
    else:
        regles = RegleClassification.query.filter_by(active=True).all()

    if not regles:
        return None, "Aucune règle active trouvée."

    for regle in regles:
        try:
            if eval(regle.condition_rc, {}, variables):
                image = Image.query.get(image_id)
                image.classification_auto = regle.nom_regle.lower()
                db.session.commit()
                return regle.nom_regle.lower(), f"Classification : {regle.nom_regle}"
        except Exception as e:
            print(f"Erreur lors de l'évaluation de la règle {regle.nom_regle}: {e}")
            continue

    image = Image.query.get(image_id)
    image.classification_auto = "non déterminé"
    db.session.commit()
    return "non déterminé", "Aucune règle applicable."
```

---

## 3. Routes Flask pour la gestion des règles

- Récupérer toutes les règles
- Ajouter, modifier, supprimer une règle

```python
@routes.route('/rules', methods=['GET'])
def get_rules():
    regles = RegleClassification.query.all()
    return jsonify([{
        'id': r.id,
        'nom': r.nom_regle,
        'condition': r.condition_rc,
        'active': r.active
    } for r in regles])

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

@routes.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    rule = RegleClassification.query.get(rule_id)
    if not rule:
        return jsonify({'error': 'Règle non trouvée'}), 404

    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': 'Règle supprimée'})
```

---

## 4. Extraction des caractéristiques (extrait de code Python)

Cette fonction analyse une image pour extraire des caractéristiques telles que moyennes RGB, luminance, texture, contraste, etc.

```python
def extraire_caracteristiques(image_path):
    with PILImage.open(image_path) as img:
        img = img.convert('RGB')
        np_img = np.array(img)
        largeur, hauteur = img.size
        taille_ko = round(os.path.getsize(image_path) / 1024, 2)

        moyenne_rouge = int(np.mean(np_img[:, :, 0]))
        moyenne_vert = int(np.mean(np_img[:, :, 1]))
        moyenne_bleu = int(np.mean(np_img[:, :, 2]))

        contraste = float(np.max(np_img) - np.min(np_img))

        hist_r = cv2.calcHist([np_img], [0], None, [256], [0, 256]).flatten().tolist()
        hist_g = cv2.calcHist([np_img], [1], None, [256], [0, 256]).flatten().tolist()
        hist_b = cv2.calcHist([np_img], [2], None, [256], [0, 256]).flatten().tolist()
        histogramme = json.dumps({'r': hist_r, 'g': hist_g, 'b': hist_b})

        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours_detectes = bool(np.sum(edges) > 0)

        luminance = np.mean(0.2126 * np_img[:, :, 0] + 0.7152 * np_img[:, :, 1] + 0.0722 * np_img[:, :, 2])

        dark_ratio = np.sum(gray < 50) / gray.size

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = np.var(laplacian)

        return {
            'taille_ko': taille_ko,
            'hauteur': hauteur,
            'largeur': largeur,
            'moyenne_rouge': moyenne_rouge,
            'moyenne_vert': moyenne_vert,
            'moyenne_bleu': moyenne_bleu,
            'contraste': contraste,
            'histogramme': histogramme,
            'contours_detectes': contours_detectes,
            'luminance_moyenne': round(float(luminance), 2),
            'dark_pixel_ratio': round(float(dark_ratio), 4),
            'texture_score': round(float(texture_score), 2)
        }
```

---

# 5. Exemple Vue.js de visualisation des caractéristiques

Composant affichant une courbe d’évolution du nombre d’images annotées pleines et vides par date.

```python
<template>
  <div class="chart-container">
    <h2 class="chart-title">{{ t("Évolution des déchets", "Trash evolution") }}</h2>
    <canvas ref="trendChart" height="300"></canvas>
  </div>
</template>

<script>
import { getLocalisations } from '@/services/api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ChartTrend',
  props: {
    lang: { type: String, default: 'fr' }
  },
  data() {
    return {
      chartInstance: null
    }
  },
  methods: {
    t(fr, en) {
      return this.lang === 'fr' ? fr : en;
    }
  },
  async mounted() {
    try {
      const res = await getLocalisations();
      const data = res.data || [];

      const countsByDate = {};

      data.forEach(item => {
        const date = item.date_upload.split('T')[0];
        if (!countsByDate[date]) {
          countsByDate[date] = { clean: 0, dirty: 0 };
        }
        if (item.etat_annot === 'clean') countsByDate[date].clean++;
        if (item.etat_annot === 'dirty') countsByDate[date].dirty++;
      });

      const labels = Object.keys(countsByDate).sort();
      const cleanData = labels.map(d => countsByDate[d].clean);
      const dirtyData = labels.map(d => countsByDate[d].dirty);

      const ctx = this.$refs.trendChart.getContext('2d');
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: this.t('Propres', 'Clean'),
              data: cleanData,
              borderColor: 'green',
              backgroundColor: 'rgba(0,128,0,0.1)',
              fill: true
            },
            {
              label: this.t('Pleines', 'Full'),
              data: dirtyData,
              borderColor: 'red',
              backgroundColor: 'rgba(255,0,0,0.1)',
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    } catch (err) {
      console.error("Erreur ChartTrend :", err);
    }
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }
}
</script>
```

---

# 6. Route Flask /api/alerts et gestion frontend

Cette route calcule et renvoie les zones où le nombre de poubelles pleines dépasse un seuil critique.

```python
@routes.route('/api/alerts', methods=['GET'])
def get_alerts():
    seuil = 5
    alerts = []

    periode = request.args.get('periode', 'all')  # 'all' = aucune restriction de date
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')

    query = db.session.query(
        Localisation.quartier,
        db.func.count(Image.id),
        db.func.avg(Localisation.latitude),
        db.func.avg(Localisation.longitude)
    ).join(Image).filter(Image.etat_annot == 'dirty')

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
            return jsonify({'alertes': [], 'seuil': seuil})
    elif periode == 'all':
        pass  # aucune restriction

    results = query.group_by(Localisation.quartier).all()

    for quartier, count, lat_avg, lon_avg in results:
        if quartier and count >= seuil and lat_avg and lon_avg:
            alerts.append({
                'quartier': quartier,
                'nb_dirty': count,
                'latitude': float(lat_avg),
                'longitude': float(lon_avg)
            })

    return jsonify({'alertes': alerts, 'seuil': seuil})
```

---

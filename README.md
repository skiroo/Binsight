<h1>
  <img src="frontend/public/favicon.ico" alt="Logo" width="40" style="vertical-align: middle; margin-right: 10px;">
  Binsight
</h1>

Plateforme intelligente de suivi et d’identification des déchets publics via analyse d’image, géolocalisation et tableaux de bord interactifs.

---

## 🚀 Lancer le projet

### 🖥️ Backend (Flask)
```bash
cd backend
python run.py
```

### Frontend (Vue + Vite)
```bash
cd frontend
npm install
npm run dev
```

L’application sera disponible sur :
- http://localhost:5173 (frontend)
- http://localhost:5000 (backend API)

---

## 👤 Comptes de démonstration / Demo Accounts

| Rôle    | Email            | Mot de passe |
|---------|------------------|--------------|
| Admin   | admin@mail.com    | admin     |
| Agent   | agent@mail.com    | agent     |
| Citoyen | test@mail.com  | test   |

> ℹ️ Chaque rôle dispose de droits différents :
> - **Admin** : accès total (génération de clés, gestion des groupes et règles)
> - **Agent** : gestion des règles, accès citoyen
> - **Citoyen** : dépôt d’image, accès à la carte dynamique, accès au dashboard.

---

## 📦 Fonctionnalités

- 📤 Dépôt d’images avec localisation
- 🤖 Analyse automatique (classification) des déchets
- 🗺️ Carte dynamique des alertes
- 📊 Dashboard interactif (filtres, statistiques, courbes)
- ⚙️ Gestion des groupes de règles (admin/agent)
- 🔐 Authentification avec rôles
- 🔑 Génération de clés d’accès pour agents

---

## 🛠️ Technologies utilisées

- **Frontend** : Vue 3, Vite, Chart.js, Leaflet
- **Backend** : Flask, SQLAlchemy, MySQL
- **Autres** : Axios, Flask-CORS, Flask-Bcrypt

---

## 🧪 API principales

| Endpoint                   | Description                         |
|----------------------------|-------------------------------------|
| `POST /login`              | Connexion utilisateur               |
| `POST /register`           | Inscription (avec clé optionnelle) |
| `POST /generate-agent-key`| Générer une clé d’accès (admin)     |
| `GET /api/rule-groups`     | Liste des groupes de règles         |
| `GET /api/stats`           | Statistiques pour dashboard         |
| `GET /api/localisations`   | Alertes géolocalisées               |

---

## 📌 Auteurs

Projet réalisé par le groupe 4D – Mastercamp Solution Factory – EFREI Paris.  

- Bastien FRANJA
- Inès MEHADHEBI
- Kiroshan SIVAKUMAR
- Maël LE BRIS
- Zelie DEVULDER

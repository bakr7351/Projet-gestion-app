# Structure du Projet OpUnit

## 📁 Structure Finale (Minimale)

```
new/
├── app.py                # Point d'entrée principal
│
├── backend/              # Backend Flask
│   ├── middlewares/      # Guards et sécurité
│   ├── models/           # Modèles SQLAlchemy
│   ├── routes/           # Routes API
│   │   └── api/          # API REST
│   ├── services/         # Logique métier
│   ├── templates/        # Templates Jinja2
│   │   └── sechage/      # Templates séchage
│   ├── utils/            # Utilitaires
│   ├── config.py         # Configuration
│   ├── extensions.py     # Extensions Flask
│   └── swagger_config.py # Documentation API
│
├── frontend/             # Interface web
│   ├── admin/            # Panneau admin
│   ├── public/           # Pages publiques
│   ├── user/             # Espace utilisateur
│   ├── css/              # Styles
│   └── js/               # Scripts
│
├── database/             # Base de données
│   ├── absorption.db     # SQLite database
│   └── README.md         # Documentation
│
├── static/               # Fichiers générés
│   └── sechage/          # Diagrammes psychrométriques
│
├── .venv/                # Environnement virtuel
├── .git/                 # Git repository
│
├── .env                  # Configuration (non versionné)
├── .env.example          # Template de configuration
├── .gitignore            # Fichiers ignorés par git
├── README.md             # Documentation principale
├── requirements.txt      # Dépendances Python
└── start.bat             # Script de démarrage
```

## 📊 Statistiques

- **Fichiers essentiels:** ~122 fichiers
- **Lignes de code backend:** ~10,000+
- **Lignes de code frontend:** ~15,000+
- **Templates:** 50+ fichiers HTML
- **Modules:** 5 modules principaux

## 🗑️ Supprimé

### Dossiers
- ✅ `__pycache__/` - Cache Python
- ✅ `.pytest_cache/` - Cache pytest
- ✅ `.vscode/` - Configuration IDE
- ✅ `tests/` - Tests (non essentiels en production)
- ✅ `docs/` - Documentation extensive
- ✅ `backend/config/` - Dossier vide

### Fichiers
- ✅ `test_*.py` - Scripts de test
- ✅ `BRANCHES.md` - Documentation branches
- ✅ `CHANGELOG.md` - Historique
- ✅ `QUICKSTART.md` - Guide rapide
- ✅ `requirements-dev.txt` - Dépendances dev
- ✅ `start_server.ps1` - Script doublon
- ✅ `start_server.bat` - Script doublon
- ✅ Fichiers database: `view_database.py`, `query_database.bat`, etc.

## ✅ Conservé (Essentiel)

### Racine
- `README.md` - Documentation minimale
- `.env.example` - Template configuration
- `.gitignore` - Git ignore
- `requirements.txt` - Dépendances
- `start.bat` - Script de démarrage

### Backend
- Tous les fichiers de code source
- Templates Jinja2
- Configuration Flask

### Frontend
- Toutes les pages HTML
- CSS et JavaScript
- Assets (images, etc.)

### Database
- `absorption.db` - Base de données
- `README.md` - Documentation minimale

## 🚀 Utilisation

```bash
# Démarrage simple
start.bat

# URL
http://localhost:5000
```

## 📦 Modules Disponibles

1. **Absorption/Désorption** - `/public/absorption.html`
2. **McCabe-Thiele** - `/public/mccabe_simulator.html`
3. **Séchage** - `/sechage`
4. **Admin** - `/admin/`
5. **API** - `/api/docs/`

---

**Version:** 1.0.0 - Minimal & Clean  
**Fichiers:** ~122 (hors .venv et .git)  
**Prêt pour:** Production

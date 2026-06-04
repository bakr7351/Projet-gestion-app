# OpUnit - Application de Génie des Procédés

Application web Flask pour les opérations unitaires en génie chimique.

## 🚀 Démarrage

```bash
# Installation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configuration
copy .env.example .env
# Éditer .env avec vos paramètres

# Lancement
start.bat
```

Ouvrir: **http://localhost:5000**

## 📦 Modules

- **Absorption / Désorption** - Calculs contre-courant et courant croisé
- **McCabe-Thiele** - Simulateur graphique interactif
- **Séchage Psychrométrique** - Calculs et diagrammes psychrométriques

## 🛠️ Technologies

Flask 3.1 • SQLAlchemy • Plotly • Matplotlib • Psychrolib

## 📁 Structure

```
backend/     # API Flask
frontend/    # Interface web
database/    # SQLite
static/      # Fichiers générés
```

## 👥 Équipe

- Backend: [@bakr7351](https://github.com/bakr7351)
- Frontend Admin: [@hajjaje](https://github.com/hajjaje)
- Database: [@Aicha233](https://github.com/Aicha233)
- Frontend User: [@IlhamElkhatibi](https://github.com/IlhamElkhatibi)

**Support:** lesinss323@gmail.com

---

**Version:** 1.0.0 • © 2026 OpUnit

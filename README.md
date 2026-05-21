# 🔬 Système d'Absorption et Désorption

Application web complète pour les calculs d'absorption et de désorption avec interface utilisateur moderne et export Excel.

## ✨ Fonctionnalités

### 🧮 Calculs Scientifiques
- **Absorption** : Contre-courant et courant croisé
- **Désorption** : Contre-courant et courant croisé  
- **Diagrammes McCabe-Thiele** : Génération automatique
- **Graphiques** : Profils de concentration
- **Export Excel** : Données numériques (résumé, paramètres, étages)

### 👥 Gestion Utilisateurs
- **Authentification** : Inscription, connexion, vérification email
- **Historique** : Sauvegarde et rechargement des calculs
- **Profils** : Gestion des comptes utilisateurs
- **Administration** : Panel admin complet

### 🎨 Interface Moderne
- **Design responsive** : Compatible mobile/desktop
- **Thème sombre/clair** : Basculement automatique
- **Notifications** : Feedback utilisateur en temps réel
- **Navigation intuitive** : UX optimisée

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- pip

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd absorption-system

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Lancer l'application
python app.py
```

### Accès
- **Application** : http://127.0.0.1:5000
- **Pages publiques** : http://127.0.0.1:5000/public/
- **Interface utilisateur** : http://127.0.0.1:5000/user/
- **Administration** : http://127.0.0.1:5000/admin/

## 📁 Structure du Projet

```
├── app.py                 # Point d'entrée principal
├── requirements.txt       # Dépendances Python
├── backend/               # API Flask, services, templates
├── frontend/              # Pages HTML, CSS, JavaScript
├── database/              # absorption.db (SQLite)
└── tests/                 # Tests pytest
```

## ⚙️ Configuration

### Variables d'Environnement (.env)
```env
# Base de données
DATABASE_TYPE=sqlite
DATABASE_PATH=database/absorption.db

# Email (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Sécurité
SECRET_KEY=votre-clé-secrète-très-longue
JWT_SECRET_KEY=votre-clé-jwt-secrète
```

### Configuration Email
1. Activer l'authentification à 2 facteurs sur Gmail
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans `SMTP_PASSWORD`

## 🔧 Utilisation

### Calculs d'Absorption
1. Accéder à `/user/absorption.html`
2. Sélectionner le type de courant (contre-courant/croisé)
3. Saisir les paramètres (G', L', m, y₀, x₀, y_objectif)
4. Cliquer sur "Calculer"
5. Visualiser les résultats et diagrammes
6. Exporter en Excel si nécessaire

### Calculs de Désorption
1. Accéder à `/user/desorption.html`
2. Sélectionner le type de courant
3. Saisir les paramètres (G, L, m, x₀, y₀, x_objectif)
4. Suivre le même processus

### Export Excel
- Export des feuilles Résumé, Paramètres et Étages
- Les diagrammes McCabe-Thiele restent disponibles dans l'interface web
- Format professionnel avec mise en forme

## 🛡️ Sécurité

- **Authentification JWT** : Tokens sécurisés
- **Validation des entrées** : Protection contre les injections
- **Rate limiting** : Protection contre les attaques
- **CORS configuré** : Sécurité cross-origin
- **Headers de sécurité** : Protection navigateur

## 📊 Technologies

### Backend
- **Flask** : Framework web Python
- **SQLite** : Base de données légère
- **JWT** : Authentification
- **xlsxwriter** : Export Excel
- **Plotly** : Génération graphiques

### Frontend
- **HTML5/CSS3** : Interface moderne
- **JavaScript ES6+** : Logique client
- **Plotly.js** : Visualisations interactives
- **Font Awesome** : Icônes

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation intégrée
- Vérifier les logs de l'application
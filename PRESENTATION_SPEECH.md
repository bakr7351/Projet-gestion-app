# 🎤 Guide de Présentation - OpUnit

## 📋 Introduction Générale du Projet

**"Bonjour à tous, je vous présente aujourd'hui OpUnit, une application web complète dédiée au génie des procédés et aux opérations unitaires en génie chimique. Cette plateforme permet aux ingénieurs, étudiants et professionnels de réaliser des calculs complexes de manière intuitive et professionnelle."**

---

## 🌐 PARTIE 1 : INTERFACES PUBLIQUES

### 1. Page d'Accueil (`/public/index.html`)

**Speech de présentation :**

*"Commençons par la page d'accueil, la vitrine de notre application. Ici, nous accueillons les visiteurs avec une présentation claire et professionnelle d'OpUnit.*

*Cette interface présente :*
- *Nos trois modules principaux : Absorption/Désorption, McCabe-Thiele, et Séchage Psychrométrique*
- *Un accès rapide aux fonctionnalités via des boutons d'action clairs*
- *Un design moderne et responsive qui s'adapte à tous les écrans*
- *Une navigation intuitive vers les pages publiques et l'espace de connexion*

*L'objectif est de donner immédiatement confiance aux utilisateurs et de leur montrer la valeur ajoutée de notre plateforme.*"

---

### 2. Module Absorption (`/public/absorption.html`)

**Speech de présentation :**

*"Passons maintenant au premier module technique : l'Absorption en contre-courant.*

*Cette interface permet de :*
- *Calculer les paramètres d'une colonne d'absorption gaz-liquide*
- *Saisir les débits, concentrations et coefficients de transfert*
- *Obtenir instantanément le nombre d'étages théoriques nécessaires*
- *Visualiser les résultats avec des graphiques interactifs Plotly*
- *Exporter les résultats en PDF ou Excel pour vos rapports*

*Les calculs sont basés sur les équations fondamentales du génie chimique, avec validation automatique des données d'entrée. Même en mode public, les utilisateurs peuvent tester les fonctionnalités pour découvrir la puissance de l'outil.*"

---

### 3. Module Désorption (`/public/desorption.html`)

**Speech de présentation :**

*"Le module Désorption est le complément naturel de l'absorption.*

*Il permet de :*
- *Calculer les opérations de désorption (stripping) en contre-courant*
- *Déterminer les paramètres pour éliminer un soluté d'un liquide*
- *Optimiser les conditions opératoires*
- *Générer des diagrammes d'équilibre et de ligne opératoire*

*L'interface est conçue pour être symétrique à celle de l'absorption, facilitant ainsi la compréhension et l'utilisation pour les ingénieurs qui travaillent sur les deux opérations.*"

---

### 4. Simulateur McCabe-Thiele (`/public/mccabe_simulator.html` & `/public/mccabe_thiele.html`)

**Speech de présentation :**

*"Le simulateur McCabe-Thiele est l'un des modules les plus avancés de notre plateforme.*

*Cette interface interactive permet de :*
- *Simuler une colonne de distillation binaire en temps réel*
- *Tracer automatiquement le diagramme McCabe-Thiele*
- *Visualiser la courbe d'équilibre et les lignes opératoires*
- *Compter les plateaux théoriques graphiquement*
- *Ajuster dynamiquement les paramètres : taux de reflux, qualité d'alimentation, compositions*
- *Observer l'impact instantané de chaque modification sur le diagramme*

*C'est un véritable outil pédagogique ET professionnel. Les étudiants peuvent comprendre visuellement les concepts de distillation, tandis que les ingénieurs peuvent dimensionner rapidement leurs colonnes.*"

---

### 5. Page À Propos (`/public/about.html`)

**Speech de présentation :**

*"La page À propos présente notre vision et notre équipe.*

*Elle contient :*
- *L'histoire et la mission d'OpUnit*
- *La présentation de l'équipe de développement avec les rôles de chacun*
- *Les technologies utilisées : Flask, SQLAlchemy, Plotly, Psychrolib*
- *Nos coordonnées pour le support et les partenariats*

*Cela humanise notre application et renforce la confiance des utilisateurs professionnels.*"

---

## 👤 PARTIE 2 : ESPACE UTILISATEUR

### 6. Connexion (`/user/login.html`)

**Speech de présentation :**

*"L'interface de connexion est le portail d'entrée vers les fonctionnalités avancées.*

*Elle propose :*
- *Un formulaire sécurisé avec email et mot de passe*
- *La gestion des erreurs en temps réel*
- *Un lien vers la récupération de mot de passe*
- *Un lien vers la création de compte*
- *Une protection contre les attaques par force brute grâce au rate limiting*

*La sécurité est notre priorité : JWT pour l'authentification, hashage bcrypt des mots de passe, et monitoring des tentatives suspectes.*"

---

### 7. Inscription (`/user/signup.html`)

**Speech de présentation :**

*"Le processus d'inscription est simple et sécurisé.*

*L'utilisateur doit fournir :*
- *Son nom complet*
- *Son email professionnel*
- *Un mot de passe fort (validation côté client et serveur)*
- *Son organisation (optionnel)*

*Après inscription :*
- *Un email de vérification est envoyé automatiquement*
- *Le compte est créé mais reste inactif jusqu'à validation*
- *L'utilisateur est redirigé vers une page de confirmation*

*Cette approche évite les inscriptions frauduleuses et garantit la qualité de notre base utilisateurs.*"

---

### 8. Tableau de Bord Utilisateur (`/user/dashboard.html`)

**Speech de présentation :**

*"Le tableau de bord utilisateur est le hub central après connexion.*

*Il affiche :*
- *Un aperçu des calculs récents de l'utilisateur*
- *Des statistiques d'utilisation : nombre de calculs, modules favoris*
- *Des raccourcis vers les trois modules principaux*
- *Les notifications importantes (nouvelles fonctionnalités, maintenance)*
- *Un widget de statut système (temps de réponse de l'API)*

*Tout est conçu pour permettre à l'utilisateur de reprendre son travail rapidement et efficacement.*"

---

### 9. Module Absorption Utilisateur (`/user/absorption.html`)

**Speech de présentation :**

*"La version authentifiée du module Absorption offre des fonctionnalités supplémentaires :*

- *Sauvegarde automatique des calculs dans l'historique personnel*
- *Export avancé avec logo personnalisé*
- *Accès aux templates de calculs pré-enregistrés*
- *Calculs en lot (batch) pour traiter plusieurs scénarios*
- *Comparaison de résultats entre différentes simulations*
- *Annotations personnelles sur les projets*

*Ces fonctionnalités transforment l'outil en véritable assistant de projet pour les ingénieurs.*"

---

### 10. Module Désorption Utilisateur (`/user/desorption.html`)

**Speech de présentation :**

*"De la même manière, le module Désorption authentifié ajoute :*

- *Tout l'historique des calculs de désorption*
- *Synchronisation avec les calculs d'absorption pour une vue d'ensemble*
- *Exportation de rapports techniques complets*
- *Intégration avec l'assistant IA pour suggestions d'optimisation*"

---

### 11. Historique (`/user/history.html`)

**Speech de présentation :**

*"L'historique est une fonctionnalité essentielle pour les utilisateurs professionnels.*

*Cette interface permet de :*
- *Consulter tous les calculs passés avec date et heure*
- *Filtrer par module (Absorption, McCabe-Thiele, Séchage)*
- *Rechercher par nom de projet ou mots-clés*
- *Recharger un ancien calcul pour le modifier*
- *Supprimer des entrées obsolètes*
- *Exporter l'historique complet en CSV*

*C'est un véritable journal de bord des projets d'ingénierie, indispensable pour la traçabilité et les audits.*"

---

### 12. Assistant IA (`/user/assistant.html`)

**Speech de présentation :**

*"L'assistant IA est une innovation majeure d'OpUnit.*

*Fonctionnalités :*
- *Chat intelligent avec contexte sur le génie des procédés*
- *Suggestions d'optimisation basées sur vos calculs*
- *Explication des résultats complexes*
- *Recommandations de paramètres selon les meilleures pratiques*
- *Réponses aux questions techniques avec citations de références*

*L'assistant utilise l'API OpenAI avec un prompt spécialisé en génie chimique. Il connaît vos projets et peut analyser vos résultats pour proposer des améliorations.*"

---

### 13. Profil Utilisateur (`/user/profile.html`)

**Speech de présentation :**

*"La page de profil permet à chaque utilisateur de gérer ses informations.*

*Options disponibles :*
- *Modification du nom et email*
- *Changement du mot de passe*
- *Paramètres de notification (email, dans l'app)*
- *Préférences d'unités (SI, impériales)*
- *Thème de l'interface (clair, sombre)*
- *Gestion des clés API pour l'intégration externe*
- *Suppression du compte (avec confirmation)*

*L'utilisateur garde le contrôle total de ses données.*"

---

### 14. Notifications (`/user/notifications.html`)

**Speech de présentation :**

*"Le centre de notifications informe l'utilisateur en temps réel.*

*Types de notifications :*
- *Calculs terminés (pour les traitements longs)*
- *Nouvelles fonctionnalités disponibles*
- *Alertes de sécurité (connexion depuis un nouvel appareil)*
- *Messages de l'équipe support*
- *Mises à jour importantes*

*Chaque notification peut être marquée comme lue ou supprimée. Un badge sur l'icône indique les non-lues.*"

---

### 15. Récupération de Mot de Passe (`/user/forgot-password.html` & `/user/reset-password.html`)

**Speech de présentation :**

*"Le processus de récupération de mot de passe est sécurisé et simple :*

**Étape 1 - Demande :**
- *L'utilisateur entre son email*
- *Un token unique et temporaire est généré*
- *Un email avec lien de réinitialisation est envoyé*
- *Le token expire après 1 heure*

**Étape 2 - Réinitialisation :**
- *L'utilisateur clique sur le lien dans l'email*
- *Il définit un nouveau mot de passe (avec validation)*
- *Le token est invalidé immédiatement après utilisation*
- *Une confirmation est envoyée par email*

*Cette approche empêche toute exploitation malveillante.*"

---

### 16. Vérification d'Email (`/user/verify-email.html`)

**Speech de présentation :**

*"La vérification d'email est obligatoire avant l'activation complète du compte.*

*Processus :*
- *Après inscription, un email avec lien de vérification est envoyé*
- *L'utilisateur clique sur le lien*
- *Le compte passe de "pending" à "active"*
- *L'utilisateur peut alors se connecter et utiliser toutes les fonctionnalités*

*Un bouton permet de renvoyer l'email si nécessaire. Cette étape réduit drastiquement les faux comptes.*"

---

## 🛡️ PARTIE 3 : PANNEAU ADMINISTRATEUR

### 17. Connexion Admin (`/admin/login.html`)

**Speech de présentation :**

*"L'accès administrateur est séparé et ultra-sécurisé.*

*Particularités :*
- *URL dédiée (/admin/)*
- *Vérification du rôle en base de données*
- *Logs de toutes les tentatives de connexion*
- *2FA optionnelle pour les super-admins*
- *Monitoring en temps réel des connexions admin*

*Seuls les utilisateurs avec le rôle 'admin' peuvent accéder à cette zone.*"

---

### 18. Tableau de Bord Admin (`/admin/dashboard.html`)

**Speech de présentation :**

*"Le dashboard admin offre une vue d'ensemble complète de la plateforme.*

*Métriques clés affichées :*
- *Nombre total d'utilisateurs (actifs, inactifs, bannis)*
- *Nombre de calculs effectués aujourd'hui, cette semaine, ce mois*
- *Statistiques d'utilisation par module*
- *Performance du serveur : CPU, mémoire, temps de réponse*
- *Graphiques d'évolution sur 30 jours*
- *Top 10 des utilisateurs les plus actifs*
- *Alertes système (erreurs, tentatives de connexion suspectes)*

*Tout est visualisé avec des graphiques Plotly interactifs et des indicateurs colorés (vert/orange/rouge) pour identifier rapidement les problèmes.*"

---

### 19. Gestion des Utilisateurs (`/admin/users.html`)

**Speech de présentation :**

*"Cette interface est le cœur de la gestion administrative.*

*Fonctionnalités :*
- *Liste complète des utilisateurs avec recherche et filtres*
- *Détails de chaque compte : email, date d'inscription, dernière connexion*
- *Actions disponibles par utilisateur :*
  - *Activer / Désactiver le compte*
  - *Promouvoir en admin / Rétrograder*
  - *Bannir temporairement ou définitivement*
  - *Voir l'historique complet des calculs*
  - *Supprimer le compte (avec confirmation double)*
- *Exportation de la liste en CSV ou Excel*
- *Envoi d'emails groupés aux utilisateurs sélectionnés*

*L'admin a un contrôle total mais toutes ses actions sont tracées dans les logs d'audit.*"

---

### 20. Journal d'Audit (`/admin/audit.html`)

**Speech de présentation :**

*"Le journal d'audit est crucial pour la sécurité et la conformité.*

*Il enregistre :*
- *Toutes les connexions et déconnexions*
- *Les modifications de comptes (création, édition, suppression)*
- *Les accès aux modules sensibles*
- *Les exportations de données*
- *Les actions administratives*
- *Les tentatives de connexion échouées*
- *Les modifications de paramètres système*

*Chaque ligne contient :*
- *Date et heure exacte*
- *Utilisateur concerné*
- *Action effectuée*
- *Adresse IP source*
- *Résultat (succès/échec)*

*Les logs sont immutables et conservés pendant 2 ans minimum. Ils peuvent être filtrés, recherchés et exportés.*"

---

### 21. Gestion des IP (`/admin/ip.html`)

**Speech de présentation :**

*"La gestion des IP protège la plateforme contre les attaques.*

*Fonctionnalités :*
- *Liste des IP bannies avec raison et date*
- *Ajout manuel d'IP à la blacklist*
- *Whitelist pour les IP de confiance (entreprises partenaires)*
- *Statistiques des tentatives par IP*
- *Débannissement temporaire ou permanent*
- *Détection automatique des comportements suspects :*
  - *Trop de tentatives de connexion*
  - *Scraping excessif*
  - *Requêtes anormales*

*Le système peut bannir automatiquement une IP après 5 tentatives échouées en 10 minutes. L'admin peut ajuster ces seuils.*"

---

### 22. Archive des Utilisateurs (`/admin/archive.html`)

**Speech de présentation :**

*"L'archive conserve les données des comptes supprimés pour conformité légale.*

*Contenu :*
- *Utilisateurs supprimés avec date de suppression*
- *Raison de la suppression (demande utilisateur, bannissement, inactivité)*
- *Statistiques d'utilisation avant suppression*
- *Possibilité de restauration dans les 30 jours*
- *Purge définitive après la période légale*

*Cela permet de respecter le RGPD (droit à l'oubli) tout en gardant une traçabilité.*"

---

### 23. Inscription Admin (`/admin/signup.html`)

**Speech de présentation :**

*"La création de comptes admin est ultra-contrôlée.*

*Processus :*
- *Seul un super-admin peut créer un nouvel admin*
- *Vérifications multiples (email, token d'invitation)*
- *Définition des permissions spécifiques*
- *Notification immédiate à tous les super-admins*
- *Log complet de la création*

*Cette interface n'est pas accessible en mode self-service. Elle nécessite une invitation par token.*"

---

## 🔧 PARTIE 4 : MODULE SÉCHAGE PSYCHROMÉTRIQUE

### 24. Interface Séchage (`/sechage`)

**Speech de présentation :**

*"Le module Séchage Psychrométrique est une exclusivité d'OpUnit.*

*Il permet de :*
- *Calculer les propriétés de l'air humide*
- *Tracer des diagrammes psychrométriques interactifs*
- *Simuler des opérations de séchage industriel*
- *Déterminer les conditions optimales de séchage*
- *Visualiser les transformations sur le diagramme*

*Points calculables :*
- *Température sèche et humide*
- *Humidité absolue et relative*
- *Enthalpie et volume spécifique*
- *Point de rosée*

*Les diagrammes sont générés dynamiquement avec Matplotlib et sauvegardés pour réutilisation. L'interface propose aussi des templates pour différents types de séchoirs.*"

---

## 🔌 PARTIE 5 : API REST

### 25. Documentation API (`/api/docs/`)

**Speech de présentation :**

*"OpUnit expose une API REST complète documentée avec Swagger.*

*Endpoints disponibles :*

**Authentification :**
- `POST /api/login` - Connexion
- `POST /api/signup` - Inscription
- `POST /api/refresh` - Renouvellement token
- `POST /api/logout` - Déconnexion

**Calculs :**
- `POST /api/calculations/absorption` - Calcul absorption
- `POST /api/calculations/desorption` - Calcul désorption
- `POST /api/mccabe/simulate` - Simulation McCabe-Thiele

**Historique :**
- `GET /api/history` - Récupérer l'historique
- `DELETE /api/history/{id}` - Supprimer un calcul

**Admin :**
- `GET /api/admin/users` - Liste utilisateurs
- `PUT /api/admin/users/{id}` - Modifier utilisateur
- `DELETE /api/admin/users/{id}` - Supprimer utilisateur

*Tous les endpoints sont sécurisés par JWT et rate-limited. La documentation Swagger est interactive : vous pouvez tester les endpoints directement depuis le navigateur.*"

---

## 🔒 PARTIE 6 : SÉCURITÉ ET ARCHITECTURE

### 26. Sécurité Multi-Couches

**Speech de présentation :**

*"La sécurité d'OpUnit repose sur plusieurs couches de protection :*

**1. Authentification :**
- *JWT avec expiration courte (30 min)*
- *Refresh tokens pour renouvellement*
- *Hashage bcrypt des mots de passe (coût 12)*

**2. Middlewares :**
- *Rate limiting (100 req/min par IP)*
- *CORS configuré strictement*
- *Protection CSRF*
- *Headers de sécurité (CSP, X-Frame-Options)*

**3. Guards :**
- *AuthGuard : vérification token sur routes protégées*
- *AccessGuard : vérification des permissions par rôle*
- *IPBanGuard : blocage des IP bannies*

**4. Monitoring :**
- *Logs d'audit immutables*
- *Détection d'anomalies en temps réel*
- *Alertes automatiques aux admins*

**5. Base de données :**
- *Requêtes paramétrées (protection SQL injection)*
- *Chiffrement des données sensibles*
- *Sauvegardes automatiques quotidiennes*

*Cette architecture multicouche rend la plateforme robuste face aux attaques courantes.*"

---

### 27. Architecture Technique

**Speech de présentation :**

*"OpUnit suit une architecture moderne et scalable :*

**Backend :**
- *Flask 3.1 avec blueprints modulaires*
- *SQLAlchemy ORM pour la base de données*
- *Pattern Service Layer pour la logique métier*
- *Séparation stricte routes/services/models*

**Frontend :**
- *Vanilla JavaScript (pas de framework lourd)*
- *CSS moderne avec variables et grid*
- *Fetch API pour les appels asynchrones*
- *Responsive design mobile-first*

**Base de données :**
- *SQLite pour développement et démos*
- *PostgreSQL recommandé en production*
- *Migrations Alembic pour la gestion du schéma*

**Visualisations :**
- *Plotly.js pour graphiques interactifs*
- *Matplotlib pour diagrammes psychrométriques*
- *Export PNG/SVG/PDF*

**Déploiement :**
- *Compatible Docker*
- *Prêt pour Gunicorn/Nginx*
- *Variables d'environnement pour configuration*
- *Monitoring avec Flask-Profiler*

*Le code est propre, documenté et suit les conventions PEP 8 pour Python.*"

---

## 📊 PARTIE 7 : STATISTIQUES ET PERFORMANCES

### 28. Performances

**Speech de présentation :**

*"OpUnit est optimisé pour la performance :*

**Temps de réponse :**
- *Authentification : < 100ms*
- *Calculs simples : < 200ms*
- *Simulations complexes : < 2s*
- *Génération graphiques : < 500ms*

**Optimisations :**
- *Cache Redis pour résultats fréquents*
- *Calculs asynchrones pour opérations longues*
- *Pagination des listes (50 items/page)*
- *Compression gzip des réponses*
- *CDN pour assets statiques*

**Scalabilité :**
- *Architecture stateless (JWT)*
- *Prêt pour load balancing horizontal*
- *Queue Celery pour tâches asynchrones*
- *Peut gérer 1000+ utilisateurs simultanés*

*Des tests de charge réguliers garantissent ces performances.*"

---

## 🎯 CONCLUSION GÉNÉRALE

**Speech de conclusion :**

*"En résumé, OpUnit est une plateforme complète qui combine :*

✅ **Puissance technique** : calculs précis basés sur les équations fondamentales  
✅ **Interface intuitive** : utilisable par débutants et experts  
✅ **Sécurité** : protection multicouche et conformité RGPD  
✅ **Modularité** : trois modules complémentaires  
✅ **Professionnalisme** : historique, exports, API  
✅ **Innovation** : assistant IA, visualisations interactives  
✅ **Pédagogie** : mode public pour apprentissage  

*OpUnit s'adresse aux :*
- *Étudiants en génie chimique (apprentissage)*
- *Ingénieurs de procédés (dimensionnement)*
- *Bureaux d'études (projets industriels)*
- *Enseignants (support de cours)*

*Notre ambition : devenir LA référence francophone pour les calculs d'opérations unitaires en ligne.*

*Merci de votre attention. Des questions ?*"

---

## 📌 CONSEILS POUR LA PRÉSENTATION

### Ordre recommandé :
1. **Introduction** (2 min)
2. **Démo interfaces publiques** (5 min) - Montrer les calculs
3. **Démo espace utilisateur** (5 min) - Montrer historique et assistant
4. **Démo panneau admin** (3 min) - Montrer contrôle et monitoring
5. **Explication technique** (3 min) - Architecture et sécurité
6. **Conclusion** (2 min)

### Astuces :
- 🎯 Préparez des données de démo réalistes
- 📊 Ayez des graphiques impressionnants prêts
- ⏱️ Chronométrez chaque partie
- 💡 Prévoyez des réponses aux questions fréquentes
- 🖥️ Testez tout en conditions réelles avant

### Points forts à mettre en avant :
- Assistant IA (innovation)
- Visualisations interactives (pédagogie)
- Sécurité multicouche (professionnalisme)
- API REST complète (intégration)
- Module Séchage (exclusivité)

---

**Bonne présentation ! 🚀**

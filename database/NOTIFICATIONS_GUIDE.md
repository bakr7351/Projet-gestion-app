# 📬 Guide des Notifications - OpUnit

## 🎯 Comment Voir les Notifications

### Pour les Utilisateurs

#### 1️⃣ Accès à la Page Notifications

**URL directe:**
```
http://localhost:5000/user/notifications.html
```

**Ou via le menu:**
1. Se connecter à l'espace utilisateur
2. Cliquer sur "Notifications" dans la barre de navigation

#### 2️⃣ Fonctionnalités Disponibles

**Filtres:**
- **Toutes**: Affiche toutes les notifications
- **Non lues**: Affiche uniquement les notifications non lues

**Actions:**
- ✅ **Marquer comme lu**: Cliquer sur l'icône ✓
- 🗑️ **Supprimer**: Cliquer sur l'icône poubelle
- ✔️✔️ **Tout marquer comme lu**: Bouton en haut à droite
- 🔄 **Actualiser**: Recharger les notifications

#### 3️⃣ Types de Notifications

**Admin Message** 🔴
- Messages envoyés par l'administrateur
- Priorité: Haute
- Badge rouge

**Système** 🟠
- Alertes système
- Mises à jour
- Badge orange

**Calcul Terminé** 🟢
- Notification de fin de calcul
- Badge vert

---

## 🔧 Pour les Administrateurs

### Comment Envoyer une Notification

#### Via l'Interface Admin

1. Se connecter en tant qu'admin
2. Aller dans la gestion des utilisateurs
3. Sélectionner un utilisateur
4. Cliquer sur "Envoyer une notification"
5. Saisir le message
6. Envoyer

#### Via l'API

```bash
POST /api/admin/user/<user_id>/notification
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "content": "Votre message ici"
}
```

**Exemple avec curl:**
```bash
curl -X POST http://localhost:5000/api/admin/user/2/notification \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Important: Votre compte nécessite une mise à jour"}'
```

---

## 📊 Structure de la Notification

### Champs de la Notification

```json
{
  "id": 1,
  "user_id": 2,
  "type": "admin_message",
  "title": "Message de l'administrateur",
  "message": "Votre message ici",
  "priority": "high",
  "is_read": false,
  "created_at": "2026-06-04T15:30:00",
  "read_at": null
}
```

### Types de Notifications

| Type | Description | Badge |
|------|-------------|-------|
| `admin_message` | Message de l'admin | Rouge 🔴 |
| `system_alert` | Alerte système | Orange 🟠 |
| `calculation_complete` | Calcul terminé | Vert 🟢 |
| `batch_complete` | Batch terminé | Vert 🟢 |
| `maintenance_alert` | Maintenance | Orange 🟠 |
| `security_alert` | Sécurité | Rouge 🔴 |

---

## 🔄 API Endpoints

### 1. Récupérer les Notifications

```
GET /api/notifications
Authorization: Bearer <token>

Query Parameters:
- unread_only: boolean (optionnel)
- limit: integer (défaut: 50)
```

**Réponse:**
```json
{
  "success": true,
  "notifications": [...],
  "unread_count": 3,
  "total": 10
}
```

### 2. Marquer comme Lu

```
PATCH /api/notifications
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "notification_ids": [1, 2, 3]
}

// Ou pour tout marquer:
{
  "mark_all": true
}
```

### 3. Supprimer des Notifications

```
DELETE /api/notifications
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "notification_ids": [1, 2, 3]
}
```

---

## 🎨 Apparence

### Notifications Non Lues
- Bordure gauche bleue
- Fond légèrement teinté
- Badge bleu en haut à droite
- Bouton "Marquer comme lu" visible

### Notifications Lues
- Bordure grise
- Fond normal
- Pas de badge
- Seulement le bouton supprimer

---

## 💡 Conseils d'Utilisation

### Pour les Utilisateurs

1. **Vérifiez régulièrement** vos notifications
2. **Marquez comme lu** les notifications traitées
3. **Supprimez** les notifications obsolètes
4. Les notifications importantes de l'admin sont en **rouge**

### Pour les Administrateurs

1. **Soyez clair et concis** dans vos messages
2. **N'abusez pas** des notifications
3. **Utilisez** les notifications pour:
   - Alertes de sécurité
   - Maintenances programmées
   - Informations importantes
4. **Évitez** pour:
   - Messages génériques
   - Spam administratif

---

## 🔔 Indicateurs Visuels

**Badge de notification:**
- Apparaît sur l'icône de bell dans le menu
- Affiche le nombre de notifications non lues
- Disparaît quand tout est lu

**Compteur:**
```
3 non lues sur 10 totales
```

**Horodatage:**
- "À l'instant" (< 1 min)
- "Il y a 5m" (< 1h)
- "Il y a 3h" (< 24h)
- "Il y a 2j" (< 7j)
- "15 déc" (> 7j)

---

## 🧪 Test

### Scénario de Test

1. **En tant qu'admin:**
   ```bash
   # Se connecter comme admin
   # Aller sur la page utilisateurs
   # Sélectionner un utilisateur
   # Envoyer une notification de test
   ```

2. **En tant qu'utilisateur:**
   ```bash
   # Se connecter
   # Aller sur /user/notifications.html
   # Voir la notification reçue
   # Marquer comme lue
   # Supprimer si nécessaire
   ```

---

## 🗄️ Base de Données

**Table:** `notifications`

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    read_at TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

---

## ✅ Checklist

- [x] API backend implémentée
- [x] Routes /api/notifications (GET, PATCH, DELETE)
- [x] Modèle Notification en base de données
- [x] Page frontend notifications.html créée
- [x] Fonction admin d'envoi de notifications
- [x] Système de filtres (toutes/non lues)
- [x] Actions (marquer lu, supprimer)
- [x] Design responsive et moderne
- [x] Horodatage relatif
- [x] Types de notifications avec badges colorés

---

## 🚀 Prochaines Améliorations

- [ ] Notifications en temps réel (WebSocket)
- [ ] Notifications push navigateur
- [ ] Préférences de notifications par type
- [ ] Archivage automatique après X jours
- [ ] Recherche dans les notifications
- [ ] Catégories personnalisées

---

**Date:** 4 juin 2026  
**Version:** 1.0.0  
**Status:** ✅ FONCTIONNEL

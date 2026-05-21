# Base de données — Absorption

## Fichiers

| Fichier | Description |
|---------|-------------|
| `schema.sqlite.sql` | Schéma SQLite (développement local) |
| `schema.sql` | Ancien schéma SQL Server (référence legacy) |
| `absorption.db` | Base locale générée par Flask — **ne pas committer** |

## Initialisation SQLite

```bash
# Depuis la racine du projet
sqlite3 database/absorption.db < database/schema.sqlite.sql
```

Ou laisser Flask créer les tables automatiquement :

```bash
python -c "from backend.app import create_app; from backend.extensions import db; app=create_app(); app.app_context().push(); db.create_all()"
```

## Branche Git

Pousser uniquement les fichiers `.sql` sur la branche `database` :

```bash
git checkout database
git add database/*.sql database/README.md
git commit -m "feat: schéma SQLite aligné sur les modèles"
git push origin database
```

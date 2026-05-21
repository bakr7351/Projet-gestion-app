# Guide branches — Projet-gestion-app

Remote : `https://github.com/bakr7351/Projet-gestion-app.git`

## Branches et responsabilités

| Branche | Contenu autorisé | Commande push |
|---------|------------------|---------------|
| `backend` | `backend/`, `app.py`, `requirements.txt`, `tests/` | `git push origin backend` |
| `database` | `database/*.sql` (pas les `.db`) | `git push origin database` |
| `frontend-admin` | `frontend/admin/`, `frontend/css/`, `frontend/js/` | `git push origin frontend-admin` |
| `frontend-user` | `frontend/user/`, `frontend/public/`, `frontend/css/`, `frontend/js/` | `git push origin frontend-user` |
| `main` | Fusion via Pull Request uniquement | — |

## Avant chaque push

```bash
git fetch origin
git checkout <ta-branche>
git pull origin <ta-branche>
git status
git push origin <ta-branche>
```

## Ne jamais committer

- `.env`, `.venv/`
- `database/*.db`
- `__pycache__/`, `.pytest_cache/`

## État des branches (à jour sur GitHub)

| Branche | Statut |
|---------|--------|
| `backend` | À jour |
| `database` | À jour (schema SQLite + legacy) |
| `frontend-admin` | À jour |
| `frontend-user` | À jour |
| `main` | Projet complet fusionné |

## Mettre à jour main après un changement sur une branche

```bash
git checkout main
git pull origin main
git merge backend   # ou frontend-admin, frontend-user, database
git push origin main
```

import json
from backend.extensions import db
from backend.models.user import User
from backend.models.archived_user import ArchivedUser
from backend.services import audit_service, email_service, token_service
from backend.utils.helpers import error_response, success_response

# The first admin created is the Admin_Principal (id=1 by convention)
ADMIN_PRINCIPAL_ID = 1


def _guard_principal(target_id: int) -> tuple | None:
    if target_id == ADMIN_PRINCIPAL_ID:
        return error_response("Cette action n'est pas autorisée sur ce compte"), 403
    return None


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    total     = User.query.count()
    actifs    = User.query.filter_by(statut="actif").count()
    desactive = User.query.filter_by(statut="desactive").count()
    bannis    = User.query.filter_by(statut="banni").count()
    return {"total": total, "actifs": actifs, "desactives": desactive, "bannis": bannis}


# ── User list ─────────────────────────────────────────────────────────────────

def list_users(search: str = None) -> list:
    query = User.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                User.nom.ilike(like),
                User.prenom.ilike(like),
                User.email.ilike(like),
            )
        )
    return [u.to_dict() for u in query.all()]


def get_user(user_id: int) -> tuple:
    user = User.query.get(user_id)
    if not user:
        return error_response("Ressource introuvable"), 404
    return success_response("OK", {"user": user.to_dict()}), 200


# ── Status management ─────────────────────────────────────────────────────────

def update_status(admin_id: int, target_id: int, new_status: str) -> tuple:
    guard = _guard_principal(target_id)
    if guard:
        return guard

    user = User.query.get(target_id)
    if not user:
        return error_response("Ressource introuvable"), 404

    user.statut = new_status
    db.session.commit()

    # Invalidate all JWT sessions by marking tokens as used
    if new_status in ("desactive", "banni"):
        token_service.invalidate_all_tokens(target_id, "email_verification")
        token_service.invalidate_all_tokens(target_id, "password_reset")

    audit_service.log_action(f"statut_{new_status}", target_id=target_id, author_id=admin_id)
    email_service.send_status_change(user, new_status)

    return success_response("Statut mis à jour."), 200


# ── Promotion ─────────────────────────────────────────────────────────────────

def promote_to_admin(admin_id: int, target_id: int) -> tuple:
    user = User.query.get(target_id)
    if not user:
        return error_response("Ressource introuvable"), 404

    user.role = "admin"
    user.promoted_by = admin_id
    db.session.commit()

    audit_service.log_action("promotion_admin", target_id=target_id, author_id=admin_id)
    return success_response("Utilisateur promu administrateur."), 200


# ── Delete / Archive ──────────────────────────────────────────────────────────

def delete_user(admin_id: int, target_id: int) -> tuple:
    guard = _guard_principal(target_id)
    if guard:
        return guard

    user = User.query.get(target_id)
    if not user:
        return error_response("Ressource introuvable"), 404

    # Archive snapshot
    snapshot = json.dumps(user.to_dict())
    archive = ArchivedUser(original_id=user.id, data_snapshot=snapshot, deleted_by=admin_id)
    db.session.add(archive)

    audit_service.log_action("suppression", target_id=target_id, author_id=admin_id)
    db.session.delete(user)
    db.session.commit()

    return success_response("Compte supprimé et archivé."), 200


# ── Notification ──────────────────────────────────────────────────────────────

def send_notification(admin_id: int, target_id: int, content: str) -> tuple:
    user = User.query.get(target_id)
    if not user:
        return error_response("Ressource introuvable"), 404

    email_service.send_notification(user, content)
    audit_service.log_action("notification", target_id=target_id, author_id=admin_id, details=content)
    return success_response("Notification envoyée."), 200

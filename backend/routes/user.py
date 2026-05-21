from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.extensions import db
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.models.login_history import LoginHistory
from backend.middlewares.auth_guard import jwt_required_guard
from backend.utils.helpers import error_response, success_response
from backend.utils.security import hash_password, verify_password

user_bp = Blueprint("user", __name__)


@user_bp.get("/user/dashboard")
@jwt_required_guard
def dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "Ressource introuvable"}), 404
    return jsonify({
        "success": True,
        "user": user.to_dict(),
        "absorption_calculator": {"message": "Modules de calcul disponibles"},
    }), 200


@user_bp.get("/user/profile")
@jwt_required_guard
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "Ressource introuvable"}), 404
    return jsonify({"success": True, "user": user.to_dict()}), 200


@user_bp.put("/user/profile")
@jwt_required_guard
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "Ressource introuvable"}), 404

    data = request.get_json() or {}
    if "nom" in data and data["nom"].strip():
        user.nom = data["nom"].strip()
    if "prenom" in data and data["prenom"].strip():
        user.prenom = data["prenom"].strip()
    db.session.commit()

    return jsonify({"success": True, "message": "Profil mis à jour.", "user": user.to_dict()}), 200


@user_bp.put("/user/change-password")
@jwt_required_guard
def change_password():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify(error_response("Ressource introuvable")), 404

    data = request.get_json() or {}
    current_pw  = data.get("current_password", "")
    new_pw      = data.get("new_password", "")
    confirm_pw  = data.get("confirm_password", "")

    if not verify_password(user.password_hash, current_pw):
        return jsonify(error_response("Mot de passe actuel incorrect")), 400
    if len(new_pw) < 8:
        return jsonify(error_response("Le nouveau mot de passe doit contenir au moins 8 caractères")), 400
    if new_pw != confirm_pw:
        return jsonify(error_response("Les mots de passe ne correspondent pas")), 400

    user.password_hash = hash_password(new_pw)
    db.session.commit()

    from backend.services import audit_service, email_service
    audit_service.log_action("password_change", target_id=user.id, author_id=user.id)
    email_service.send_password_changed(user)

    return jsonify(success_response("Mot de passe modifié avec succès.")), 200


@user_bp.get("/user/login-history")
@jwt_required_guard
def login_history():
    user_id = int(get_jwt_identity())
    logs = (LoginHistory.query
            .filter_by(user_id=user_id)
            .order_by(LoginHistory.created_at.desc())
            .limit(20)
            .all())
    return jsonify({"success": True, "history": [l.to_dict() for l in logs]}), 200


@user_bp.get("/user/history")
@jwt_required_guard
def history():
    user_id = int(get_jwt_identity())
    logs = AuditLog.query.filter_by(target_id=user_id).order_by(AuditLog.created_at.desc()).all()
    return jsonify({"success": True, "history": [l.to_dict() for l in logs]}), 200


@user_bp.post("/user/logout-all")
@jwt_required_guard
def logout_all():
    """Invalidate all active tokens for this user"""
    user_id = int(get_jwt_identity())
    from backend.services import token_service, audit_service
    token_service.invalidate_all_tokens(user_id, "email_verification")
    token_service.invalidate_all_tokens(user_id, "password_reset")
    audit_service.log_action("logout_all", target_id=user_id, author_id=user_id)
    return jsonify(success_response("Toutes les sessions ont été déconnectées.")), 200

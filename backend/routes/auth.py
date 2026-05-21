from flask import Blueprint, request, jsonify
from backend.services import auth_service
from backend.middlewares.ip_ban_guard import ip_ban_check
from backend.extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/signup")
@ip_ban_check
@limiter.limit("5 per minute; 20 per hour")
def signup():
    data = request.get_json() or {}
    resp, status = auth_service.register(
        nom=data.get("nom", "").strip(),
        prenom=data.get("prenom", "").strip(),
        email=data.get("email", "").strip(),
        password=data.get("password", ""),
        confirm=data.get("confirm_password", ""),
        ip=request.remote_addr,
    )
    return jsonify(resp), status


@auth_bp.post("/auth/login")
@ip_ban_check
@limiter.limit("10 per minute; 50 per hour")
def login():
    data = request.get_json() or {}
    resp, status = auth_service.login(
        email=data.get("email", "").strip(),
        password=data.get("password", ""),
        ip=request.remote_addr,
    )
    return jsonify(resp), status


@auth_bp.post("/auth/verify-email")
def verify_email():
    token = request.args.get("token") or (request.get_json() or {}).get("token", "")
    resp, status = auth_service.verify_email(token)
    return jsonify(resp), status


@auth_bp.post("/auth/resend-verification")
def resend_verification():
    data = request.get_json() or {}
    resp, status = auth_service.resend_verification(data.get("email", "").strip())
    return jsonify(resp), status


@auth_bp.post("/auth/forgot-password")
def forgot_password():
    data = request.get_json() or {}
    resp, status = auth_service.forgot_password(data.get("email", "").strip())
    return jsonify(resp), status


@auth_bp.post("/auth/reset-password")
def reset_password():
    data = request.get_json() or {}
    resp, status = auth_service.reset_password(
        token_str=data.get("token", ""),
        new_password=data.get("password", ""),
    )
    return jsonify(resp), status


@auth_bp.get("/auth/security-status")
@limiter.limit("20 per minute")
def check_security_status():
    """
    Vérifie le statut de sécurité pour un email/IP donné
    Permet au frontend d'afficher des avertissements avant le blocage
    """
    from backend.services.login_security_service import login_security_service
    
    email = request.args.get("email", "").strip()
    ip = request.remote_addr
    
    if not email:
        return jsonify({"success": False, "message": "Email requis"}), 400
    
    try:
        status = login_security_service.get_security_status(email, ip)
        
        # Déterminer si un avertissement doit être affiché
        email_info = status.get('email', {})
        ip_info = status.get('ip', {})
        
        warning = None
        if email_info.get('is_blocked') or ip_info.get('is_blocked'):
            # Bloqué actuellement
            blocked_info = email_info if email_info.get('is_blocked') else ip_info
            warning = {
                'type': 'blocked',
                'message': f"Compte temporairement bloqué. Réessayez dans {blocked_info.get('remaining_time_formatted', 'quelques instants')}.",
                'remaining_seconds': blocked_info.get('remaining_seconds', 0)
            }
        elif email_info.get('failed_attempts', 0) >= 2 or ip_info.get('failed_attempts', 0) >= 2:
            # Proche du blocage
            remaining = min(
                email_info.get('attempts_remaining', 3),
                ip_info.get('attempts_remaining', 3)
            )
            warning = {
                'type': 'warning',
                'message': f"Attention: {remaining} tentative(s) restante(s) avant blocage temporaire.",
                'attempts_remaining': remaining
            }
        
        return jsonify({
            "success": True,
            "status": status,
            "warning": warning
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Erreur lors de la vérification du statut de sécurité"
        }), 500

from flask_jwt_extended import create_access_token
from backend.extensions import db
from backend.models.user import User
from backend.utils.helpers import is_valid_email, is_strong_password, error_response, success_response
from backend.utils.security import hash_password, verify_password
from backend.services import token_service, audit_service, ip_monitor, email_service
from backend.services.login_security_service import login_security_service
from backend.config import Config


# ── Registration ──────────────────────────────────────────────────────────────

def register(nom: str, prenom: str, email: str, password: str, confirm: str, ip: str) -> tuple:
    """Register a new user. Returns (response_dict, http_status)."""
    # Validate required fields
    if not all([nom, prenom, email, password, confirm]):
        return error_response("Tous les champs obligatoires doivent être renseignés"), 400

    # Validate email format
    if not is_valid_email(email):
        return error_response("Format d'email invalide"), 400

    # Validate password length
    if not is_strong_password(password):
        return error_response("Le mot de passe doit contenir au moins 8 caractères"), 400

    # Validate password confirmation
    if password != confirm:
        return error_response("Les mots de passe ne correspondent pas"), 400

    # Check email uniqueness
    if User.query.filter_by(email=email).first():
        return error_response("Cette adresse email est déjà utilisée"), 409

    # Create user
    user = User(
        nom=nom,
        prenom=prenom,
        email=email,
        password_hash=hash_password(password),
        role="user",
        statut="non_verifie",
        ip_inscription=ip,
    )
    db.session.add(user)
    db.session.commit()

    # Record IP
    ip_monitor.record_ip(ip, user.id, "signup")

    # Audit log
    audit_service.log_action("creation", target_id=user.id, author_id=user.id)

    # Send verification email
    token = token_service.generate_token(user.id, "email_verification", Config.EMAIL_TOKEN_EXPIRES)
    email_service.send_verification(user, token)

    return success_response("Inscription réussie. Vérifiez votre boîte mail pour activer votre compte."), 201


# ── Email verification ────────────────────────────────────────────────────────

def verify_email(token_str: str) -> tuple:
    token = token_service.validate_token(token_str, "email_verification")
    if not token:
        return error_response("Ce lien est expiré ou invalide"), 400

    user = User.query.get(token.user_id)
    if not user:
        return error_response("Utilisateur introuvable"), 404

    user.statut = "actif"
    token_service.invalidate_token(token_str)
    db.session.commit()

    audit_service.log_action("activation", target_id=user.id)
    email_service.send_activation_confirmation(user)
    email_service.send_welcome(user)

    return success_response("Compte activé avec succès."), 200


def resend_verification(email: str) -> tuple:
    user = User.query.filter_by(email=email).first()
    if not user or user.statut != "non_verifie":
        return success_response("Si ce compte existe, un email a été envoyé."), 200

    token_service.invalidate_all_tokens(user.id, "email_verification")
    token = token_service.generate_token(user.id, "email_verification", Config.EMAIL_TOKEN_EXPIRES)
    email_service.send_verification(user, token)

    return success_response("Email de vérification renvoyé."), 200


# ── Login ─────────────────────────────────────────────────────────────────────

def login(email: str, password: str, ip: str) -> tuple:
    """
    Authentifie un utilisateur avec protection contre les attaques par force brute
    Implémente un système de blocage progressif après 3 tentatives échouées
    """
    # Vérifier si la connexion est autorisée (pas de blocage en cours)
    is_allowed, security_info = login_security_service.check_login_allowed(email, ip)
    
    if not is_allowed:
        # Utilisateur ou IP bloqué temporairement
        audit_service.log_action(
            "login_blocked", 
            target_id=None, 
            author_id=None,
            details=f"Login blocked for {email} from {ip} - {security_info.get('reason', 'unknown')}"
        )
        return error_response(security_info['message']), 423  # 423 Locked
    
    # Rechercher l'utilisateur
    user = User.query.filter_by(email=email).first()

    # Vérifier les identifiants
    if not user or not verify_password(user.password_hash, password):
        # Enregistrer la tentative échouée
        failed_info = login_security_service.record_failed_login(email, ip)
        
        # Log de l'audit pour tentative échouée
        audit_service.log_action(
            "login_failed", 
            target_id=user.id if user else None, 
            author_id=user.id if user else None,
            details=f"Failed login attempt from {ip}"
        )
        
        # Enregistrer dans l'historique si l'utilisateur existe
        if user:
            from backend.models.login_history import LoginHistory
            db.session.add(LoginHistory(user_id=user.id, ip_address=ip, success=False))
            db.session.commit()
        
        # Retourner le message approprié (avec avertissement si proche du blocage)
        status_code = 423 if failed_info.get('blocked', False) else 401
        return error_response(failed_info['message']), status_code

    # Vérifier le statut du compte
    if user.statut == "non_verifie":
        return error_response("Votre compte n'a pas encore été activé. Vérifiez votre boîte mail."), 403
    if user.statut in ("desactive", "banni"):
        return error_response("Votre compte est désactivé ou banni. Contactez l'administrateur."), 403

    # Connexion réussie - réinitialiser les compteurs de sécurité
    login_security_service.record_successful_login(email, ip)

    # Enregistrer la connexion réussie
    from backend.models.login_history import LoginHistory
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.add(LoginHistory(user_id=user.id, ip_address=ip, success=True))
    db.session.commit()

    # Logs et monitoring
    ip_monitor.record_ip(ip, user.id, "login")
    audit_service.log_action("login_success", target_id=user.id, author_id=user.id)
    
    # Générer le token JWT
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role, 
            "prenom": user.prenom, 
            "nom": user.nom,
            "email": user.email
        }
    )

    return success_response(
        "Connexion réussie.", 
        {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "prenom": user.prenom,
                "nom": user.nom,
                "role": user.role
            }
        }
    ), 200


# ── Password reset ────────────────────────────────────────────────────────────

def forgot_password(email: str) -> tuple:
    """Always return the same response regardless of whether email exists."""
    user = User.query.filter_by(email=email).first()
    if user and user.statut == "actif":
        token = token_service.generate_token(user.id, "password_reset", Config.RESET_TOKEN_EXPIRES)
        email_service.send_password_reset(user, token)
    return success_response("Si ce compte existe, un lien de réinitialisation a été envoyé."), 200


def reset_password(token_str: str, new_password: str) -> tuple:
    if not is_strong_password(new_password):
        return error_response("Le mot de passe doit contenir au moins 8 caractères"), 400

    token = token_service.validate_token(token_str, "password_reset")
    if not token:
        return error_response("Ce lien est expiré ou invalide"), 400

    user = User.query.get(token.user_id)
    if not user:
        return error_response("Utilisateur introuvable"), 404

    user.password_hash = hash_password(new_password)
    token_service.invalidate_token(token_str)
    db.session.commit()

    audit_service.log_action("password_reset", target_id=user.id)
    email_service.send_password_changed(user)

    return success_response("Mot de passe réinitialisé avec succès."), 200

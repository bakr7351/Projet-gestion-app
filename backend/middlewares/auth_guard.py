from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def jwt_required_guard(f):
    """Decorator: requires a valid JWT. Returns 401 if missing or invalid."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"success": False, "message": "Authentification requise"}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required_guard(f):
    """Decorator: requires a valid JWT with role=admin. Returns 403 otherwise."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"success": False, "message": "Authentification requise"}), 401

        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"success": False, "message": "Accès refusé"}), 403

        return f(*args, **kwargs)
    return decorated

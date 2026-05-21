from functools import wraps
from flask import request, jsonify
from backend.services.ip_monitor import is_banned


def ip_ban_check(f):
    """Decorator: blocks requests from banned IP addresses with 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr
        if is_banned(ip):
            return jsonify({"success": False, "message": "Accès bloqué"}), 403
        return f(*args, **kwargs)
    return decorated

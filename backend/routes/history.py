"""
History Blueprint
Exposes REST endpoints for managing user calculation history.
All endpoints require a valid JWT via @jwt_required_guard.
"""

import math
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.middlewares.auth_guard import jwt_required_guard
from backend.services.history_service import history_service

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
@jwt_required_guard
def list_entries():
    """GET /api/history — paginated, filterable list of history entries."""
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    calc_type = request.args.get("calc_type", None)

    entries, total = history_service.get_entries(user_id, calc_type, page, per_page)
    pages = math.ceil(total / per_page) if per_page > 0 else 0

    return jsonify({
        "success": True,
        "entries": [entry.to_dict() for entry in entries],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        },
    }), 200


@history_bp.get("/history/<entry_id>")
@jwt_required_guard
def get_entry(entry_id):
    """GET /api/history/<entry_id> — retrieve a single history entry."""
    user_id = int(get_jwt_identity())

    entry = history_service.get_entry(entry_id, user_id)
    if entry is None:
        return jsonify({"success": False, "message": "Entrée introuvable"}), 404

    return jsonify({"success": True, "entry": entry.to_dict()}), 200


@history_bp.patch("/history/<entry_id>")
@jwt_required_guard
def rename_entry(entry_id):
    """PATCH /api/history/<entry_id> — rename a history entry."""
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    name = data.get("name", "")

    try:
        entry = history_service.update_name(entry_id, user_id, name)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 403

    return jsonify({"success": True, "entry": entry.to_dict()}), 200


@history_bp.delete("/history/<entry_id>")
@jwt_required_guard
def delete_entry(entry_id):
    """DELETE /api/history/<entry_id> — delete a single history entry."""
    user_id = int(get_jwt_identity())

    try:
        history_service.delete_entry(entry_id, user_id)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 403

    return jsonify({"success": True, "message": "Entrée supprimée"}), 200


@history_bp.delete("/history")
@jwt_required_guard
def delete_all_entries():
    """DELETE /api/history — delete all history entries for the current user."""
    user_id = int(get_jwt_identity())

    deleted_count = history_service.delete_all_entries(user_id)

    return jsonify({
        "success": True,
        "message": "Historique supprimé",
        "deleted_count": deleted_count,
    }), 200

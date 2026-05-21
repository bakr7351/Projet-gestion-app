from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from backend.middlewares.auth_guard import admin_required_guard
from backend.models.audit_log import AuditLog
from backend.models.archived_user import ArchivedUser
from backend.services import admin_service
from backend.services.ip_monitor import ban_ip, get_suspicious_ips
from backend.services.system_service import get_dashboard_metrics, system_metrics
from backend.services.analytics_service import get_dashboard_analytics
import io
import csv
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/dashboard")
@admin_required_guard
def dashboard():
    stats = admin_service.get_dashboard_stats()
    users = admin_service.list_users()
    system_data = get_dashboard_metrics()
    analytics_data = get_dashboard_analytics()
    return jsonify({
        "success": True,
        "stats": stats,
        "users": users,
        "system": system_data,
        "activity": analytics_data,
    }), 200


@admin_bp.get("/admin/export/excel")
@admin_required_guard
def export_excel():
    """Export users as a real .xlsx file using xlsxwriter"""
    try:
        import xlsxwriter

        users = admin_service.list_users()

        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True})
        ws = wb.add_worksheet("Utilisateurs")

        # ── Header style ──────────────────────────────────────────
        header_fmt = wb.add_format({
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#6366F1",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "font_size": 11,
        })
        alt_fmt = wb.add_format({
            "bg_color": "#F1F5F9",
            "border": 1,
            "valign": "vcenter",
        })
        normal_fmt = wb.add_format({
            "border": 1,
            "valign": "vcenter",
        })

        headers = ["ID", "Nom", "Prénom", "Email", "Rôle", "Statut",
                   "Date d'inscription", "Dernière connexion", "IP inscription"]

        for col_idx, header in enumerate(headers):
            ws.write(0, col_idx, header, header_fmt)

        # ── Data rows ─────────────────────────────────────────────
        for row_idx, user in enumerate(users, start=1):
            row_fmt = alt_fmt if row_idx % 2 == 0 else normal_fmt
            row_data = [
                user.get("id", ""),
                user.get("nom", ""),
                user.get("prenom", ""),
                user.get("email", ""),
                user.get("role", ""),
                user.get("statut", ""),
                user.get("created_at", ""),
                user.get("last_login", "") or "Jamais",
                user.get("ip_inscription", "") or "",
            ]
            for col_idx, value in enumerate(row_data):
                ws.write(row_idx, col_idx, value, row_fmt)

        # ── Column widths ─────────────────────────────────────────
        col_widths = [6, 15, 15, 30, 12, 14, 22, 22, 18]
        for i, width in enumerate(col_widths):
            ws.set_column(i, i, width)

        ws.set_row(0, 28)

        wb.close()
        buf.seek(0)

        filename = f"utilisateurs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.get("/admin/export/csv")
@admin_required_guard
def export_csv():
    """Export users as CSV"""
    users = admin_service.list_users()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Nom", "Prénom", "Email", "Rôle", "Statut",
                     "Date d'inscription", "Dernière connexion"])
    for u in users:
        writer.writerow([
            u.get("id", ""),
            u.get("nom", ""),
            u.get("prenom", ""),
            u.get("email", ""),
            u.get("role", ""),
            u.get("statut", ""),
            u.get("created_at", ""),
            u.get("last_login", "") or "Jamais",
        ])

    buf.seek(0)
    filename = f"utilisateurs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    return send_file(
        io.BytesIO(buf.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )


@admin_bp.get("/admin/system-metrics")
@admin_required_guard
def get_system_metrics():
    """Get real-time system metrics"""
    try:
        metrics = system_metrics.get_all_metrics()
        health = system_metrics.get_health_status()
        app_metrics = system_metrics.get_app_metrics()

        return jsonify({
            "success": True,
            "metrics": metrics,
            "health": health,
            "app": app_metrics,
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la récupération des métriques: {str(e)}"
        }), 500


@admin_bp.get("/admin/users")
@admin_required_guard
def list_users():
    search = request.args.get("search", "").strip() or None
    users = admin_service.list_users(search)
    return jsonify({"success": True, "users": users}), 200


@admin_bp.get("/admin/users/<int:user_id>")
@admin_required_guard
def get_user(user_id):
    resp, status = admin_service.get_user(user_id)
    return jsonify(resp), status


@admin_bp.put("/admin/users/<int:user_id>/status")
@admin_required_guard
def update_status(user_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}
    resp, status = admin_service.update_status(admin_id, user_id, data.get("statut", ""))
    return jsonify(resp), status


@admin_bp.put("/admin/users/<int:user_id>/promote")
@admin_required_guard
def promote(user_id):
    admin_id = int(get_jwt_identity())
    resp, status = admin_service.promote_to_admin(admin_id, user_id)
    return jsonify(resp), status


@admin_bp.delete("/admin/users/<int:user_id>")
@admin_required_guard
def delete_user(user_id):
    admin_id = int(get_jwt_identity())
    resp, status = admin_service.delete_user(admin_id, user_id)
    return jsonify(resp), status


@admin_bp.post("/admin/users/<int:user_id>/notify")
@admin_required_guard
def notify_user(user_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}
    resp, status = admin_service.send_notification(admin_id, user_id, data.get("content", ""))
    return jsonify(resp), status


@admin_bp.get("/admin/audit-log")
@admin_required_guard
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return jsonify({"success": True, "logs": [l.to_dict() for l in logs]}), 200


@admin_bp.get("/admin/archive")
@admin_required_guard
def archive():
    archived = ArchivedUser.query.order_by(ArchivedUser.deleted_at.desc()).all()
    result = [
        {
            "id": a.id,
            "original_id": a.original_id,
            "data_snapshot": a.data_snapshot,
            "deleted_by": a.deleted_by,
            "deleted_at": a.deleted_at.isoformat() if a.deleted_at else None,
        }
        for a in archived
    ]
    return jsonify({"success": True, "archive": result}), 200


@admin_bp.get("/admin/ip-records")
@admin_required_guard
def ip_records():
    suspicious = get_suspicious_ips()
    return jsonify({"success": True, "suspicious_ips": suspicious}), 200


@admin_bp.post("/admin/ip/ban")
@admin_required_guard
def ban_ip_route():
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}
    ip = data.get("ip", "").strip()
    if not ip:
        return jsonify({"success": False, "message": "Adresse IP requise"}), 400
    ban_ip(ip, admin_id)
    return jsonify({"success": True, "message": f"IP {ip} bannie avec succès."}), 200

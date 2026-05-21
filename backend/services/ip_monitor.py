from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.ip_record import IPRecord, BannedIP
from backend.models.user import User


def record_ip(ip: str, user_id: int, event_type: str) -> None:
    """Record an IP address for a signup or login event."""
    record = IPRecord(ip_address=ip, user_id=user_id, event_type=event_type)
    db.session.add(record)
    db.session.commit()


def is_banned(ip: str) -> bool:
    """Return True if the IP is in the banned list."""
    return BannedIP.query.filter_by(ip_address=ip).first() is not None


def ban_ip(ip: str, admin_id: int) -> None:
    """Ban an IP and set all associated accounts to 'banni'."""
    # Add to banned list (ignore if already banned)
    if not BannedIP.query.filter_by(ip_address=ip).first():
        banned = BannedIP(ip_address=ip, banned_by=admin_id)
        db.session.add(banned)

    # Ban all users registered from this IP
    User.query.filter_by(ip_inscription=ip).update({"statut": "banni"})
    db.session.commit()


def get_suspicious_ips() -> list:
    """Return IPs with more than 3 signups in the last 24 hours."""
    threshold = datetime.utcnow() - timedelta(hours=24)
    from sqlalchemy import func
    results = (
        db.session.query(IPRecord.ip_address, func.count(IPRecord.id).label("count"))
        .filter(IPRecord.event_type == "signup", IPRecord.created_at >= threshold)
        .group_by(IPRecord.ip_address)
        .having(func.count(IPRecord.id) > 3)
        .all()
    )
    return [{"ip": r.ip_address, "count": r.count} for r in results]

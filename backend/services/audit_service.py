from datetime import datetime
from backend.extensions import db
from backend.models.audit_log import AuditLog


def log_action(action: str, target_id: int, author_id: int = None, details: str = None) -> AuditLog:
    """Create an audit log entry for any account action."""
    entry = AuditLog(
        action=action,
        target_id=target_id,
        author_id=author_id,
        details=details,
        created_at=datetime.utcnow(),
    )
    db.session.add(entry)
    db.session.commit()
    return entry

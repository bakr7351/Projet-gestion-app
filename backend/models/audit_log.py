from datetime import datetime
from backend.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id         = db.Column(db.Integer, primary_key=True)
    action     = db.Column(db.String(100), nullable=False)
    target_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details    = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "target_id": self.target_id,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "details": self.details,
        }

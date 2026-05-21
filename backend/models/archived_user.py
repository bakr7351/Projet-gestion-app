from datetime import datetime
from backend.extensions import db


class ArchivedUser(db.Model):
    __tablename__ = "archived_users"

    id            = db.Column(db.Integer, primary_key=True)
    original_id   = db.Column(db.Integer, nullable=False)
    data_snapshot = db.Column(db.Text, nullable=False)  # JSON snapshot
    deleted_by    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    deleted_at    = db.Column(db.DateTime, default=datetime.utcnow)

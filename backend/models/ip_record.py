from datetime import datetime
from backend.extensions import db


class IPRecord(db.Model):
    __tablename__ = "ip_records"

    id         = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event_type = db.Column(db.Enum("signup", "login", name="ip_event_enum"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BannedIP(db.Model):
    __tablename__ = "banned_ips"

    id         = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    banned_by  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

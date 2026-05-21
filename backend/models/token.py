from datetime import datetime
from backend.extensions import db


class Token(db.Model):
    __tablename__ = "tokens"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token      = db.Column(db.String(255), unique=True, nullable=False)
    type       = db.Column(
        db.Enum("email_verification", "password_reset", name="token_type_enum"),
        nullable=False
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

from datetime import datetime
from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id             = db.Column(db.Integer, primary_key=True)
    nom            = db.Column(db.String(100), nullable=False)
    prenom         = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(255), unique=True, nullable=False)
    password_hash  = db.Column(db.String(255), nullable=False)
    role           = db.Column(db.Enum("user", "admin", name="role_enum"), default="user", nullable=False)
    statut         = db.Column(
        db.Enum("non_verifie", "actif", "desactive", "banni", name="statut_enum"),
        default="non_verifie",
        nullable=False
    )
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    last_login     = db.Column(db.DateTime, nullable=True)
    ip_inscription = db.Column(db.String(45), nullable=True)
    promoted_by    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    # New API-related fields
    api_access_enabled = db.Column(db.Boolean, default=False)
    api_rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    last_api_access = db.Column(db.DateTime)
    derniere_connexion = db.Column(db.DateTime)  # For compatibility

    tokens         = db.relationship("Token", backref="user", lazy=True, foreign_keys="Token.user_id")
    audit_targets  = db.relationship("AuditLog", backref="target", lazy=True, foreign_keys="AuditLog.target_id")
    audit_actions  = db.relationship("AuditLog", backref="author", lazy=True, foreign_keys="AuditLog.author_id")
    login_history  = db.relationship("LoginHistory", backref="user", lazy=True, foreign_keys="LoginHistory.user_id")

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "role": self.role,
            "statut": self.statut,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "derniere_connexion": self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            "ip_inscription": self.ip_inscription,
            "api_access_enabled": self.api_access_enabled,
            "api_rate_limit": self.api_rate_limit,
            "last_api_access": self.last_api_access.isoformat() if self.last_api_access else None,
        }

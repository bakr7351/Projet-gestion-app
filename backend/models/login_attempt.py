"""
Modèle pour gérer les tentatives de connexion et le blocage progressif
"""
from datetime import datetime, timedelta
from backend.extensions import db


class LoginAttempt(db.Model):
    """
    Modèle pour traquer les tentatives de connexion échouées
    et implémenter un système de blocage progressif
    """
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False, index=True)  # Email ou IP
    identifier_type = db.Column(db.String(20), nullable=False)  # 'email' ou 'ip'
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    block_level = db.Column(db.Integer, default=0, nullable=False)  # Niveau de blocage (0, 1, 2, 3...)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<LoginAttempt {self.identifier_type}:{self.identifier} - {self.failed_attempts} attempts>'
    
    @classmethod
    def get_or_create(cls, identifier: str, identifier_type: str):
        """
        Récupère ou crée un enregistrement de tentatives de connexion
        """
        attempt = cls.query.filter_by(
            identifier=identifier,
            identifier_type=identifier_type
        ).first()
        
        if not attempt:
            attempt = cls(
                identifier=identifier,
                identifier_type=identifier_type,
                failed_attempts=0,
                block_level=0
            )
            db.session.add(attempt)
            db.session.commit()
        
        return attempt
    
    def is_blocked(self) -> bool:
        """
        Vérifie si l'identifiant est actuellement bloqué
        """
        if not self.blocked_until:
            return False
        
        return datetime.utcnow() < self.blocked_until
    
    def get_remaining_block_time(self) -> int:
        """
        Retourne le temps restant de blocage en secondes
        """
        if not self.is_blocked():
            return 0
        
        remaining = self.blocked_until - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
    
    def record_failed_attempt(self):
        """
        Enregistre une tentative échouée et applique le blocage si nécessaire
        """
        self.failed_attempts += 1
        self.last_attempt = datetime.utcnow()
        
        # Blocage après 3 tentatives échouées
        if self.failed_attempts >= 3:
            self._apply_progressive_block()
        
        db.session.commit()
    
    def record_successful_login(self):
        """
        Réinitialise le compteur après une connexion réussie
        """
        self.failed_attempts = 0
        self.blocked_until = None
        self.block_level = 0
        self.last_attempt = datetime.utcnow()
        db.session.commit()
    
    def _apply_progressive_block(self):
        """
        Applique un blocage progressif basé sur le niveau de blocage
        """
        # Calcul du temps de blocage : 30s * 2^block_level
        base_block_time = 30  # 30 secondes de base
        block_duration = base_block_time * (2 ** self.block_level)
        
        # Limite maximale de 24 heures (86400 secondes)
        max_block_time = 24 * 60 * 60
        block_duration = min(block_duration, max_block_time)
        
        self.blocked_until = datetime.utcnow() + timedelta(seconds=block_duration)
        self.block_level += 1
        
        # Réinitialise le compteur de tentatives pour le prochain cycle
        self.failed_attempts = 0
    
    def get_block_info(self) -> dict:
        """
        Retourne les informations de blocage pour l'utilisateur
        """
        if not self.is_blocked():
            return {
                'is_blocked': False,
                'failed_attempts': self.failed_attempts,
                'attempts_remaining': max(0, 3 - self.failed_attempts)
            }
        
        remaining_time = self.get_remaining_block_time()
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        
        return {
            'is_blocked': True,
            'remaining_seconds': remaining_time,
            'remaining_time_formatted': f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s",
            'block_level': self.block_level,
            'failed_attempts': self.failed_attempts
        }
    
    @classmethod
    def cleanup_expired_blocks(cls):
        """
        Nettoie les anciens enregistrements de blocage expirés
        Méthode utilitaire pour maintenance
        """
        # Supprime les enregistrements de plus de 30 jours sans activité
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        expired_attempts = cls.query.filter(
            cls.last_attempt < cutoff_date,
            cls.blocked_until < datetime.utcnow()
        ).all()
        
        for attempt in expired_attempts:
            db.session.delete(attempt)
        
        db.session.commit()
        return len(expired_attempts)
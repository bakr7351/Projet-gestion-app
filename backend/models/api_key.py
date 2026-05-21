"""
API Key Model
Manages API keys for service-to-service authentication
"""

from datetime import datetime
from backend.extensions import db
import json

class APIKey(db.Model):
    """API Key model for authentication"""
    
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permissions = db.Column(db.Text)  # JSON array of allowed endpoints
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='api_keys')
    
    def __init__(self, **kwargs):
        super(APIKey, self).__init__(**kwargs)
        if isinstance(self.permissions, list):
            self.permissions = json.dumps(self.permissions)
    
    @property
    def permissions_list(self):
        """Get permissions as a list"""
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @permissions_list.setter
    def permissions_list(self, value):
        """Set permissions from a list"""
        if isinstance(value, list):
            self.permissions = json.dumps(value)
        else:
            self.permissions = json.dumps([])
    
    def has_permission(self, endpoint):
        """Check if API key has permission for specific endpoint"""
        permissions = self.permissions_list
        
        # If no permissions set, allow all (for backward compatibility)
        if not permissions:
            return True
        
        # Check for exact match or wildcard
        for permission in permissions:
            if permission == '*' or permission == endpoint:
                return True
            # Check for prefix match (e.g., '/api/v1/calculations/*')
            if permission.endswith('*') and endpoint.startswith(permission[:-1]):
                return True
        
        return False
    
    def is_expired(self):
        """Check if API key is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'permissions': self.permissions_list,
            'rate_limit': self.rate_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def __repr__(self):
        return f'<APIKey {self.name} for user {self.user_id}>'
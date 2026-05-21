"""
Calculation Cache Model
Caches calculation results for performance optimization
"""

from datetime import datetime, timedelta
from backend.extensions import db
import json
import hashlib
import uuid

class CalculationCache(db.Model):
    """Calculation results cache model"""
    
    __tablename__ = 'calculation_cache'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous
    calculation_type = db.Column(db.String(20), nullable=False)  # absorption, desorption
    parameters_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA256 of parameters
    results_data = db.Column(db.Text, nullable=False)  # JSON results
    graphics_data = db.Column(db.Text)  # JSON 3D graphics data (Phase 3)
    hit_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='calculation_cache')
    
    @property
    def results(self):
        """Get results as dict"""
        if self.results_data:
            try:
                return json.loads(self.results_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @results.setter
    def results(self, value):
        """Set results from dict"""
        if isinstance(value, dict):
            self.results_data = json.dumps(value)
        else:
            self.results_data = json.dumps({})
    
    @property
    def graphics(self):
        """Get graphics data as dict"""
        if self.graphics_data:
            try:
                return json.loads(self.graphics_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @graphics.setter
    def graphics(self, value):
        """Set graphics data from dict"""
        if isinstance(value, dict):
            self.graphics_data = json.dumps(value)
        else:
            self.graphics_data = json.dumps({})
    
    @classmethod
    def generate_parameters_hash(cls, calculation_type, parameters):
        """Generate hash for calculation parameters"""
        # Create a consistent string representation of parameters
        param_str = f"{calculation_type}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(param_str.encode()).hexdigest()
    
    @classmethod
    def get_cached_result(cls, calculation_type, parameters, user_id=None):
        """Get cached result if available"""
        params_hash = cls.generate_parameters_hash(calculation_type, parameters)
        
        # Look for exact match first (same user or anonymous)
        cache_entry = cls.query.filter_by(
            calculation_type=calculation_type,
            parameters_hash=params_hash,
            user_id=user_id
        ).first()
        
        # If not found and user is authenticated, try anonymous cache
        if not cache_entry and user_id:
            cache_entry = cls.query.filter_by(
                calculation_type=calculation_type,
                parameters_hash=params_hash,
                user_id=None
            ).first()
        
        # Check if cache entry is still valid
        if cache_entry:
            if cache_entry.expires_at and datetime.utcnow() > cache_entry.expires_at:
                # Cache expired, delete it
                db.session.delete(cache_entry)
                db.session.commit()
                return None
            
            # Update access time and hit count
            cache_entry.accessed_at = datetime.utcnow()
            cache_entry.hit_count += 1
            db.session.commit()
            
            return cache_entry
        
        return None
    
    @classmethod
    def cache_result(cls, calculation_type, parameters, results, user_id=None, graphics_data=None, ttl_hours=24):
        """Cache calculation result"""
        params_hash = cls.generate_parameters_hash(calculation_type, parameters)
        
        # Check if entry already exists
        existing = cls.query.filter_by(
            calculation_type=calculation_type,
            parameters_hash=params_hash,
            user_id=user_id
        ).first()
        
        if existing:
            # Update existing entry
            existing.results = results
            if graphics_data:
                existing.graphics = graphics_data
            existing.accessed_at = datetime.utcnow()
            existing.hit_count += 1
            if ttl_hours:
                existing.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            cache_entry = existing
        else:
            # Create new entry
            cache_entry = cls(
                user_id=user_id,
                calculation_type=calculation_type,
                parameters_hash=params_hash
            )
            cache_entry.results = results
            if graphics_data:
                cache_entry.graphics = graphics_data
            if ttl_hours:
                cache_entry.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            
            db.session.add(cache_entry)
        
        db.session.commit()
        return cache_entry
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired cache entries"""
        expired_count = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
        return expired_count
    
    @classmethod
    def cleanup_old_entries(cls, days=30):
        """Remove old cache entries"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_count = cls.query.filter(
            cls.accessed_at < cutoff_date
        ).delete()
        db.session.commit()
        return old_count
    
    def is_expired(self):
        """Check if cache entry is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'calculation_type': self.calculation_type,
            'parameters_hash': self.parameters_hash,
            'results': self.results,
            'graphics': self.graphics,
            'hit_count': self.hit_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accessed_at': self.accessed_at.isoformat() if self.accessed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }
    
    def __repr__(self):
        return f'<CalculationCache {self.id} - {self.calculation_type}>'
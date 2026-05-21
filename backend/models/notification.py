"""
Notification Model
Manages user notifications and preferences
"""

from datetime import datetime
from backend.extensions import db
import json

class Notification(db.Model):
    """User notification model"""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for system-wide notifications
    type = db.Column(db.String(50), nullable=False)  # calculation_complete, system_alert, batch_complete, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text)  # JSON data for rich notifications
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    @property
    def notification_data(self):
        """Get notification data as dict"""
        if self.data:
            try:
                return json.loads(self.data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @notification_data.setter
    def notification_data(self, value):
        """Set notification data from dict"""
        if isinstance(value, dict):
            self.data = json.dumps(value)
        else:
            self.data = json.dumps({})
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def is_expired(self):
        """Check if notification is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_notification(cls, user_id, notification_type, title, message, data=None, priority='normal'):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority
        )
        
        if data:
            notification.notification_data = data
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @classmethod
    def create_system_notification(cls, notification_type, title, message, data=None, priority='normal'):
        """Create a system-wide notification"""
        return cls.create_notification(None, notification_type, title, message, data, priority)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.notification_data,
            'priority': self.priority,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.type}>'

class NotificationPreferences(db.Model):
    """User notification preferences model"""
    
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    calculation_complete = db.Column(db.Boolean, default=True)
    batch_complete = db.Column(db.Boolean, default=True)
    system_alerts = db.Column(db.Boolean, default=True)
    maintenance_alerts = db.Column(db.Boolean, default=True)
    security_alerts = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='notification_preferences')
    
    @classmethod
    def get_or_create_for_user(cls, user_id):
        """Get or create notification preferences for user"""
        prefs = cls.query.filter_by(user_id=user_id).first()
        if not prefs:
            prefs = cls(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()
        return prefs
    
    def should_notify(self, notification_type):
        """Check if user should receive notification of given type"""
        type_mapping = {
            'calculation_complete': self.calculation_complete,
            'batch_complete': self.batch_complete,
            'system_alert': self.system_alerts,
            'maintenance_alert': self.maintenance_alerts,
            'security_alert': self.security_alerts,
        }
        
        return type_mapping.get(notification_type, True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_notifications': self.email_notifications,
            'push_notifications': self.push_notifications,
            'calculation_complete': self.calculation_complete,
            'batch_complete': self.batch_complete,
            'system_alerts': self.system_alerts,
            'maintenance_alerts': self.maintenance_alerts,
            'security_alerts': self.security_alerts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<NotificationPreferences for user {self.user_id}>'
"""
System Metrics Model
Tracks system performance and usage metrics
"""

from datetime import datetime, timedelta
from backend.extensions import db
import json

class SystemMetrics(db.Model):
    """System performance metrics model"""
    
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(50), nullable=False, index=True)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))  # %, ms, MB, count, etc.
    metric_data = db.Column(db.Text)  # JSON additional data
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @property
    def additional_data(self):
        """Get additional metric data as dict"""
        if self.metric_data:
            try:
                return json.loads(self.metric_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @additional_data.setter
    def additional_data(self, value):
        """Set additional metric data from dict"""
        if isinstance(value, dict):
            self.metric_data = json.dumps(value)
        else:
            self.metric_data = json.dumps({})
    
    @classmethod
    def record_metric(cls, name, value, unit=None, additional_data=None):
        """Record a system metric"""
        metric = cls(
            metric_name=name,
            metric_value=value,
            metric_unit=unit
        )
        
        if additional_data:
            metric.additional_data = additional_data
        
        db.session.add(metric)
        db.session.commit()
        return metric
    
    @classmethod
    def get_latest_metric(cls, name):
        """Get the latest value for a metric"""
        return cls.query.filter_by(metric_name=name).order_by(cls.recorded_at.desc()).first()
    
    @classmethod
    def get_metric_history(cls, name, hours=24):
        """Get metric history for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.metric_name == name,
            cls.recorded_at >= cutoff_time
        ).order_by(cls.recorded_at.asc()).all()
    
    @classmethod
    def get_average_metric(cls, name, hours=24):
        """Get average metric value over time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = db.session.query(db.func.avg(cls.metric_value)).filter(
            cls.metric_name == name,
            cls.recorded_at >= cutoff_time
        ).scalar()
        return result or 0
    
    @classmethod
    def cleanup_old_metrics(cls, days=30):
        """Remove old metric entries"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_count = cls.query.filter(cls.recorded_at < cutoff_date).delete()
        db.session.commit()
        return old_count
    
    @classmethod
    def get_system_summary(cls):
        """Get summary of current system metrics"""
        summary = {}
        
        # Get latest values for key metrics
        key_metrics = [
            'cpu_usage_percent',
            'memory_usage_mb',
            'memory_usage_percent',
            'active_users',
            'api_requests_per_hour',
            'calculation_requests_per_hour',
            'average_response_time_ms',
            'cache_hit_rate_percent'
        ]
        
        for metric_name in key_metrics:
            latest = cls.get_latest_metric(metric_name)
            if latest:
                summary[metric_name] = {
                    'value': latest.metric_value,
                    'unit': latest.metric_unit,
                    'recorded_at': latest.recorded_at.isoformat(),
                    'additional_data': latest.additional_data
                }
        
        return summary
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'additional_data': self.additional_data,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }
    
    def __repr__(self):
        return f'<SystemMetrics {self.metric_name}: {self.metric_value}>'

class RateLimitTracking(db.Model):
    """Rate limiting tracking model"""
    
    __tablename__ = 'rate_limit_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'))
    client_ip = db.Column(db.String(45))
    endpoint = db.Column(db.String(100), nullable=False)
    request_count = db.Column(db.Integer, default=1)
    window_start = db.Column(db.DateTime, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='rate_limit_tracking')
    api_key = db.relationship('APIKey', backref='rate_limit_tracking')
    
    @classmethod
    def cleanup_old_tracking(cls, hours=24):
        """Remove old rate limit tracking entries"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        old_count = cls.query.filter(cls.window_start < cutoff_time).delete()
        db.session.commit()
        return old_count
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'api_key_id': self.api_key_id,
            'client_ip': self.client_ip,
            'endpoint': self.endpoint,
            'request_count': self.request_count,
            'window_start': self.window_start.isoformat() if self.window_start else None,
        }
    
    def __repr__(self):
        return f'<RateLimitTracking {self.endpoint}: {self.request_count}>'
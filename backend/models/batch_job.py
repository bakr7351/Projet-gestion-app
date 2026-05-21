"""
Batch Job Model
Manages batch processing jobs for calculations
"""

from datetime import datetime
from backend.extensions import db
import json
import uuid

class BatchJob(db.Model):
    """Batch processing job model"""
    
    __tablename__ = 'batch_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    calculation_type = db.Column(db.String(20), nullable=False)  # absorption, desorption
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed, cancelled
    total_calculations = db.Column(db.Integer, default=0)
    completed_calculations = db.Column(db.Integer, default=0)
    failed_calculations = db.Column(db.Integer, default=0)
    results_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    progress_data = db.Column(db.Text)  # JSON progress information
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    scheduled_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='batch_jobs')
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_calculations == 0:
            return 0
        return (self.completed_calculations / self.total_calculations) * 100
    
    @property
    def progress_info(self):
        """Get progress information as dict"""
        if self.progress_data:
            try:
                return json.loads(self.progress_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @progress_info.setter
    def progress_info(self, value):
        """Set progress information from dict"""
        if isinstance(value, dict):
            self.progress_data = json.dumps(value)
        else:
            self.progress_data = json.dumps({})
    
    def update_progress(self, completed=None, failed=None, info=None):
        """Update job progress"""
        if completed is not None:
            self.completed_calculations = completed
        if failed is not None:
            self.failed_calculations = failed
        if info is not None:
            self.progress_info = info
        
        # Update status based on progress
        if self.completed_calculations + self.failed_calculations >= self.total_calculations:
            if self.failed_calculations == 0:
                self.status = 'completed'
                self.completed_at = datetime.utcnow()
            else:
                self.status = 'completed_with_errors'
                self.completed_at = datetime.utcnow()
    
    def start_processing(self):
        """Mark job as started"""
        self.status = 'processing'
        self.started_at = datetime.utcnow()
    
    def mark_failed(self, error_message):
        """Mark job as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel the job"""
        if self.status in ['pending', 'processing']:
            self.status = 'cancelled'
            self.completed_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'calculation_type': self.calculation_type,
            'status': self.status,
            'total_calculations': self.total_calculations,
            'completed_calculations': self.completed_calculations,
            'failed_calculations': self.failed_calculations,
            'progress_percentage': self.progress_percentage,
            'progress_info': self.progress_info,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
        }
    
    def __repr__(self):
        return f'<BatchJob {self.id} - {self.status}>'
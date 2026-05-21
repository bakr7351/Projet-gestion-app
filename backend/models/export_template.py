"""
Export Template Model
Manages customizable export templates for different formats
"""

from datetime import datetime
from backend.extensions import db
import json

class ExportTemplate(db.Model):
    """Export template model for customizable reports"""
    
    __tablename__ = 'export_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    format_type = db.Column(db.String(20), nullable=False)  # pdf, excel, csv, json
    template_data = db.Column(db.Text, nullable=False)  # JSON template configuration
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)  # System templates cannot be deleted
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    creator = db.relationship('User', backref='export_templates')
    
    @property
    def template_config(self):
        """Get template configuration as dict"""
        if self.template_data:
            try:
                return json.loads(self.template_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @template_config.setter
    def template_config(self, value):
        """Set template configuration from dict"""
        if isinstance(value, dict):
            self.template_data = json.dumps(value, indent=2)
        else:
            self.template_data = json.dumps({})
    
    @classmethod
    def get_default_template(cls, format_type):
        """Get default template for format type"""
        return cls.query.filter_by(
            format_type=format_type,
            is_default=True,
            is_active=True
        ).first()
    
    @classmethod
    def get_templates_for_format(cls, format_type, user_id=None):
        """Get all available templates for format type"""
        query = cls.query.filter_by(format_type=format_type, is_active=True)
        
        if user_id:
            # Include system templates and user's own templates
            query = query.filter(
                db.or_(
                    cls.is_system == True,
                    cls.created_by == user_id
                )
            )
        else:
            # Only system templates for anonymous users
            query = query.filter_by(is_system=True)
        
        return query.all()
    
    @classmethod
    def create_default_templates(cls):
        """Create default system templates"""
        default_templates = [
            {
                'name': 'Standard PDF Report',
                'format_type': 'pdf',
                'description': 'Standard PDF report with charts and tables',
                'template_data': {
                    'include_header': True,
                    'include_parameters': True,
                    'include_results_table': True,
                    'include_charts': True,
                    'include_performance_metrics': True,
                    'page_orientation': 'portrait',
                    'font_size': 12,
                    'chart_size': 'medium'
                }
            },
            {
                'name': 'Detailed Excel Workbook',
                'format_type': 'excel',
                'description': 'Multi-sheet Excel workbook with detailed data',
                'template_data': {
                    'sheets': ['Parameters', 'Results', 'Charts', 'Performance'],
                    'include_formulas': True,
                    'include_charts': True,
                    'auto_fit_columns': True,
                    'freeze_headers': True
                }
            },
            {
                'name': 'Data Analysis CSV',
                'format_type': 'csv',
                'description': 'CSV format optimized for data analysis',
                'template_data': {
                    'delimiter': ',',
                    'include_headers': True,
                    'include_metadata': False,
                    'flatten_nested_data': True
                }
            },
            {
                'name': 'API Integration JSON',
                'format_type': 'json',
                'description': 'JSON format for API integrations',
                'template_data': {
                    'pretty_print': True,
                    'include_metadata': True,
                    'include_performance': True,
                    'nested_structure': True
                }
            }
        ]
        
        for template_data in default_templates:
            existing = cls.query.filter_by(
                name=template_data['name'],
                format_type=template_data['format_type']
            ).first()
            
            if not existing:
                template = cls(
                    name=template_data['name'],
                    format_type=template_data['format_type'],
                    description=template_data['description'],
                    is_default=True,
                    is_system=True
                )
                template.template_config = template_data['template_data']
                
                db.session.add(template)
        
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'format_type': self.format_type,
            'description': self.description,
            'template_config': self.template_config,
            'is_default': self.is_default,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<ExportTemplate {self.name} ({self.format_type})>'
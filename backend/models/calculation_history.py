"""
Calculation History Model
Stores persistent calculation history entries for authenticated users.
"""

from datetime import datetime
from backend.extensions import db
import json
import uuid


class CalculationHistory(db.Model):
    """Persistent calculation history record for a user."""

    __tablename__ = 'calculation_history'

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    calculation_type = db.Column(
        db.Enum('absorption', 'desorption', 'mccabe_thiele', 'sechage', name='calc_type_enum'),
        nullable=False
    )
    custom_name = db.Column(db.String(100), nullable=True)
    input_parameters = db.Column(db.Text, nullable=False)   # JSON
    result_summary = db.Column(db.Text, nullable=False)     # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Composite index on (user_id, created_at) for efficient per-user queries
    __table_args__ = (
        db.Index('ix_calculation_history_user_created', 'user_id', 'created_at'),
    )

    # Relationship to User
    user = db.relationship('User', backref='calculation_history')

    # ------------------------------------------------------------------
    # JSON property helpers (mirrors CalculationCache pattern)
    # ------------------------------------------------------------------

    @property
    def input_params_dict(self):
        """Return input_parameters as a Python dict."""
        if self.input_parameters:
            try:
                return json.loads(self.input_parameters)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @input_params_dict.setter
    def input_params_dict(self, value):
        """Set input_parameters from a Python dict."""
        if isinstance(value, dict):
            self.input_parameters = json.dumps(value)
        else:
            self.input_parameters = json.dumps({})

    @property
    def result_summary_dict(self):
        """Return result_summary as a Python dict."""
        if self.result_summary:
            try:
                return json.loads(self.result_summary)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @result_summary_dict.setter
    def result_summary_dict(self, value):
        """Set result_summary from a Python dict."""
        if isinstance(value, dict):
            self.result_summary = json.dumps(value)
        else:
            self.result_summary = json.dumps({})

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self):
        """Convert to dictionary for JSON serialisation.

        Note: user_id is intentionally excluded (Requirement 7.4).
        """
        return {
            'id': self.id,
            'calculation_type': self.calculation_type,
            'custom_name': self.custom_name,
            'input_parameters': self.input_params_dict,
            'result_summary': self.result_summary_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<CalculationHistory {self.id} - {self.calculation_type}>'

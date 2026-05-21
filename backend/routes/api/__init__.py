"""
API Routes Package
Structured REST API with versioning support
"""

from flask import Blueprint
from flask_restful import Api

# Create API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1 = Api(api_v1_bp)

# Import and register API resources
from .auth import AuthResource, TokenRefreshResource, APIKeyResource
from .calculations import CalculationResource, BatchCalculationResource
from .exports import ExportResource
from .notifications import NotificationResource
from .admin import AdminResource

# Register API resources with endpoints
api_v1.add_resource(AuthResource, '/auth/login')
api_v1.add_resource(TokenRefreshResource, '/auth/refresh')
api_v1.add_resource(APIKeyResource, '/auth/api-keys')
api_v1.add_resource(CalculationResource, '/calculations/<string:calc_type>')
api_v1.add_resource(BatchCalculationResource, '/calculations/batch')
api_v1.add_resource(ExportResource, '/exports/<string:format_type>')
api_v1.add_resource(NotificationResource, '/notifications')
api_v1.add_resource(AdminResource, '/admin/<string:resource>')

def register_api_routes(app):
    """Register API blueprints with the Flask app"""
    app.register_blueprint(api_v1_bp)
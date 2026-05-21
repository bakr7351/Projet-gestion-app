"""
API Admin Resources
REST API endpoints for system administration
"""

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User

class AdminResource(Resource):
    """Resource for administrative operations"""
    
    @jwt_required()
    def get(self, resource):
        """
        Get administrative data
        ---
        tags:
          - Administration
        security:
          - JWT: []
        parameters:
          - in: path
            name: resource
            type: string
            enum: [users, system, monitoring]
            required: true
        responses:
          200:
            description: Administrative data retrieved
          403:
            description: Insufficient permissions
        """
        user_id = int(get_jwt_identity())  # Convert to int
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return {
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Admin access required'
                }
            }, 403
        
        if resource == 'users':
            users = User.query.all()
            return {
                'success': True,
                'users': [user.to_dict() for user in users]
            }, 200
        
        elif resource == 'system':
            return {
                'success': True,
                'system_info': {
                    'version': '2.0.0',
                    'features': ['REST API', 'JWT Auth', 'Rate Limiting'],
                    'status': 'operational'
                }
            }, 200
        
        elif resource == 'monitoring':
            return {
                'success': True,
                'metrics': {
                    'active_users': User.query.filter_by(statut='actif').count(),
                    'total_users': User.query.count(),
                    'api_enabled_users': User.query.filter_by(api_access_enabled=True).count()
                }
            }, 200
        
        else:
            return {
                'success': False,
                'error': {
                    'code': 'INVALID_RESOURCE',
                    'message': f'Invalid admin resource: {resource}'
                }
            }, 404
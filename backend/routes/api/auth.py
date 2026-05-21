"""
API Authentication Resources
JWT token-based authentication for REST API
"""

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from werkzeug.security import check_password_hash
import hashlib
import secrets
from datetime import datetime, timedelta

from backend.models.user import User
from backend.models.api_key import APIKey
from backend.extensions import db
from backend.middlewares.rate_limiter import require_rate_limit
from backend.middlewares.security_middleware import require_input_validation

class LoginSchema(Schema):
    """Schema for login request validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class APIKeySchema(Schema):
    """Schema for API key creation"""
    name = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    permissions = fields.List(fields.Str(), load_default=[])
    rate_limit = fields.Int(load_default=1000, validate=lambda x: x > 0)
    expires_days = fields.Int(load_default=365, validate=lambda x: 0 < x <= 365)

class AuthResource(Resource):
    """Authentication resource for login and API key management"""
    
    @require_rate_limit('auth_login')
    @require_input_validation()
    def post(self):
        """
        Login endpoint - returns JWT tokens
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: credentials
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 6
        responses:
          200:
            description: Login successful
            schema:
              type: object
              properties:
                success:
                  type: boolean
                access_token:
                  type: string
                refresh_token:
                  type: string
                user:
                  type: object
          400:
            description: Invalid input
          401:
            description: Invalid credentials
        """
        schema = LoginSchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid input parameters',
                    'details': err.messages
                }
            }, 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {
                'success': False,
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password'
                }
            }, 401
        
        # Check if user is active
        if user.statut != 'actif':
            return {
                'success': False,
                'error': {
                    'code': 'ACCOUNT_INACTIVE',
                    'message': 'Account is not active'
                }
            }, 401
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string for JWT
            expires_delta=timedelta(minutes=15)  # Short-lived access token
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),  # Convert to string for JWT
            expires_delta=timedelta(days=30)  # Long-lived refresh token
        )
        
        # Update last login
        user.derniere_connexion = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.nom,
                'prenom': user.prenom,
                'role': user.role
            }
        }, 200

class TokenRefreshResource(Resource):
    """Token refresh resource"""
    
    @jwt_required(refresh=True)
    @require_rate_limit('auth_refresh')
    def post(self):
        """
        Refresh access token
        ---
        tags:
          - Authentication
        security:
          - JWT: []
        responses:
          200:
            description: Token refreshed successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                access_token:
                  type: string
          401:
            description: Invalid refresh token
        """
        current_user_id = get_jwt_identity()
        
        # Verify user still exists and is active
        user = User.query.get(int(current_user_id))  # Convert back to int for database
        if not user or user.statut != 'actif':
            return {
                'success': False,
                'error': {
                    'code': 'INVALID_USER',
                    'message': 'User not found or inactive'
                }
            }, 401
        
        # Create new access token
        access_token = create_access_token(
            identity=current_user_id,  # Already a string
            expires_delta=timedelta(minutes=15)
        )
        
        return {
            'success': True,
            'access_token': access_token
        }, 200

class APIKeyResource(Resource):
    """API Key management resource"""
    
    @jwt_required()
    @require_rate_limit('api_key_create')
    def post(self):
        """
        Create new API key
        ---
        tags:
          - Authentication
        security:
          - JWT: []
        parameters:
          - in: body
            name: api_key_data
            schema:
              type: object
              required:
                - name
              properties:
                name:
                  type: string
                  minLength: 3
                permissions:
                  type: array
                  items:
                    type: string
                rate_limit:
                  type: integer
                  minimum: 1
                expires_days:
                  type: integer
                  minimum: 1
                  maximum: 365
        responses:
          201:
            description: API key created successfully
          400:
            description: Invalid input
          403:
            description: Insufficient permissions
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))  # Convert to int
        
        # Check if user has API access enabled
        if not user.api_access_enabled:
            return {
                'success': False,
                'error': {
                    'code': 'API_ACCESS_DISABLED',
                    'message': 'API access not enabled for this user'
                }
            }, 403
        
        schema = APIKeySchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid input parameters',
                    'details': err.messages
                }
            }, 400
        
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Create API key record
        api_key_record = APIKey(
            key_hash=key_hash,
            name=data['name'],
            user_id=int(current_user_id),  # Convert to int
            permissions=data['permissions'],
            rate_limit=data['rate_limit'],
            expires_at=datetime.utcnow() + timedelta(days=data['expires_days'])
        )
        
        db.session.add(api_key_record)
        db.session.commit()
        
        return {
            'success': True,
            'api_key': api_key,  # Only returned once!
            'key_id': api_key_record.id,
            'name': api_key_record.name,
            'rate_limit': api_key_record.rate_limit,
            'expires_at': api_key_record.expires_at.isoformat()
        }, 201
    
    @jwt_required()
    @require_rate_limit('api_key_list')
    def get(self):
        """
        List user's API keys
        ---
        tags:
          - Authentication
        security:
          - JWT: []
        responses:
          200:
            description: API keys retrieved successfully
        """
        current_user_id = get_jwt_identity()
        
        api_keys = APIKey.query.filter_by(
            user_id=int(current_user_id),  # Convert to int
            is_active=True
        ).all()
        
        return {
            'success': True,
            'api_keys': [{
                'id': key.id,
                'name': key.name,
                'rate_limit': key.rate_limit,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'permissions': key.permissions
            } for key in api_keys]
        }, 200
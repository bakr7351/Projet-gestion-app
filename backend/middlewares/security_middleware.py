"""
Advanced Security Middleware
Comprehensive security measures for API endpoints
"""

import re
import hashlib
import hmac
import secrets
from functools import wraps
from flask import request, jsonify, g
from backend.models.api_key import APIKey

def safe_str_cmp(a, b):
    """Safe string comparison to prevent timing attacks"""
    return secrets.compare_digest(str(a), str(b))

class SecurityMiddleware:
    """Advanced security middleware for API protection"""
    
    def __init__(self):
        # Suspicious patterns for input validation
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
        ]
        
        # Blocked user agents (bots, scanners)
        self.blocked_user_agents = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"masscan",
            r"nessus",
            r"openvas",
        ]
    
    def validate_input(self, data):
        """Validate input data for security threats"""
        if not data:
            return True, None
        
        # Convert to string for pattern matching
        data_str = str(data).lower()
        
        # Check for SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return False, f"Potential SQL injection detected: {pattern}"
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return False, f"Potential XSS attack detected: {pattern}"
        
        return True, None
    
    def validate_user_agent(self, user_agent):
        """Check if user agent is suspicious"""
        if not user_agent:
            return True, None
        
        user_agent_lower = user_agent.lower()
        
        for pattern in self.blocked_user_agents:
            if re.search(pattern, user_agent_lower):
                return False, f"Blocked user agent: {pattern}"
        
        return True, None
    
    def validate_api_key(self, api_key):
        """Validate API key and check permissions"""
        if not api_key:
            return False, None, "API key required"
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Find the API key in database
        api_key_record = APIKey.query.filter_by(
            key_hash=key_hash,
            is_active=True
        ).first()
        
        if not api_key_record:
            return False, None, "Invalid API key"
        
        if api_key_record.is_expired():
            return False, None, "API key expired"
        
        # Update last used timestamp
        api_key_record.update_last_used()
        
        return True, api_key_record, None
    
    def check_request_signature(self, signature, payload, secret):
        """Verify HMAC request signature for sensitive operations"""
        if not signature or not secret:
            return False
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures safely
        return safe_str_cmp(signature, expected_signature)
    
    def get_client_fingerprint(self):
        """Generate client fingerprint for tracking"""
        components = [
            request.remote_addr or '',
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            request.headers.get('Accept-Encoding', ''),
        ]
        
        fingerprint_data = '|'.join(components)
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

# Global security middleware instance
security_middleware = SecurityMiddleware()

def require_input_validation():
    """Decorator to validate request input for security threats"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate JSON data
            if request.is_json:
                json_data = request.get_json()
                is_valid, error_msg = security_middleware.validate_input(json_data)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'SECURITY_VIOLATION',
                            'message': 'Request blocked for security reasons',
                            'details': error_msg
                        }
                    }), 400
            
            # Validate query parameters
            for key, value in request.args.items():
                is_valid, error_msg = security_middleware.validate_input(value)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'SECURITY_VIOLATION',
                            'message': 'Request blocked for security reasons',
                            'details': f'Invalid parameter {key}: {error_msg}'
                        }
                    }), 400
            
            # Validate User-Agent
            user_agent = request.headers.get('User-Agent')
            is_valid, error_msg = security_middleware.validate_user_agent(user_agent)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'BLOCKED_USER_AGENT',
                        'message': 'Request blocked: suspicious user agent',
                        'details': error_msg
                    }
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_api_key_auth(permissions=None):
    """Decorator to require API key authentication with optional permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'API_KEY_REQUIRED',
                        'message': 'API key required for this endpoint'
                    }
                }), 401
            
            is_valid, api_key_record, error_msg = security_middleware.validate_api_key(api_key)
            
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_API_KEY',
                        'message': error_msg
                    }
                }), 401
            
            # Check permissions if specified
            if permissions:
                endpoint = request.endpoint or 'unknown'
                if not api_key_record.has_permission(endpoint):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INSUFFICIENT_PERMISSIONS',
                            'message': f'API key does not have permission for {endpoint}'
                        }
                    }), 403
            
            # Store API key info in g for use in the endpoint
            g.api_key = api_key_record
            g.api_key_user = api_key_record.user
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_request_signature(secret_key_func):
    """Decorator to require HMAC request signature for sensitive operations"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get('X-Signature')
            
            if not signature:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'SIGNATURE_REQUIRED',
                        'message': 'Request signature required for this operation'
                    }
                }), 401
            
            # Get the secret key (could be from user, API key, etc.)
            secret = secret_key_func()
            
            if not secret:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'SIGNATURE_VALIDATION_ERROR',
                        'message': 'Unable to validate request signature'
                    }
                }), 500
            
            # Get request payload
            payload = request.get_data(as_text=True)
            
            # Verify signature
            if not security_middleware.check_request_signature(signature, payload, secret):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_SIGNATURE',
                        'message': 'Request signature verification failed'
                    }
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_ip_whitelist(allowed_ips):
    """Decorator to restrict access to specific IP addresses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            
            if client_ip not in allowed_ips:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'IP_NOT_ALLOWED',
                        'message': f'Access denied for IP address: {client_ip}'
                    }
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def init_security_middleware(app):
    """Initialize security middleware with Flask app"""
    
    @app.before_request
    def security_checks():
        """Run security checks on all requests"""
        # Skip security checks for static files
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # Generate and store client fingerprint
        g.client_fingerprint = security_middleware.get_client_fingerprint()
        
        # Add security headers will be handled in after_request
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "connect-src 'self';"
        )
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS for HTTPS (only add if using HTTPS)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    return security_middleware
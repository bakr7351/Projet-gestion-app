"""
Rate Limiting Middleware
Advanced rate limiting with Redis backend and sliding window algorithm
"""

import hashlib
import logging
import time
from functools import wraps

import redis
from flask import g, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from backend.models.api_key import APIKey
from backend.models.user import User

logger = logging.getLogger(__name__)


class RateLimiter:
    """Advanced rate limiter with Redis backend"""
    
    def __init__(self, redis_url='redis://localhost:6379/0'):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis connected for rate limiting")
        except Exception as e:
            logger.warning("Redis not available, using in-memory fallback: %s", e)
            self.redis_available = False
            self.memory_store = {}
    
    def _get_client_id(self):
        """Get unique client identifier"""
        # Try JWT token first
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                return f"user:{user_id}"
        except:
            pass
        
        # Try API key
        api_key = request.headers.get('X-API-Key')
        if api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            return f"api_key:{key_hash}"
        
        # Fallback to IP address
        return f"ip:{request.remote_addr}"
    
    def _get_rate_limit_for_client(self, client_id):
        """Get rate limit configuration for client"""
        if client_id.startswith('user:'):
            user_id = int(client_id.split(':')[1])
            user = User.query.get(user_id)
            if user:
                return user.api_rate_limit or 1000
        
        elif client_id.startswith('api_key:'):
            key_hash = client_id.split(':')[1]
            api_key = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
            if api_key and not api_key.is_expired():
                return api_key.rate_limit
        
        # Default rate limit for IP addresses
        return 100  # requests per hour
    
    def _sliding_window_check(self, client_id, endpoint, limit, window_seconds=3600):
        """Sliding window rate limiting algorithm"""
        key = f"rate_limit:{client_id}:{endpoint}"
        now = time.time()
        window_start = now - window_seconds
        
        if self.redis_available:
            # Redis implementation
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_count = results[1] + 1  # +1 for the request we just added
            
        else:
            # In-memory fallback
            if key not in self.memory_store:
                self.memory_store[key] = []
            
            # Remove old entries
            self.memory_store[key] = [
                timestamp for timestamp in self.memory_store[key]
                if timestamp > window_start
            ]
            
            # Add current request
            self.memory_store[key].append(now)
            current_count = len(self.memory_store[key])
        
        return current_count, limit
    
    def check_rate_limit(self, endpoint=None):
        """Check if request is within rate limit"""
        client_id = self._get_client_id()
        endpoint = endpoint or request.endpoint or 'unknown'
        limit = self._get_rate_limit_for_client(client_id)
        
        current_count, limit = self._sliding_window_check(client_id, endpoint, limit)
        
        # Store in g for response headers
        g.rate_limit_current = current_count
        g.rate_limit_limit = limit
        g.rate_limit_remaining = max(0, limit - current_count)
        g.rate_limit_reset = int(time.time() + 3600)  # Reset in 1 hour
        
        return current_count <= limit
    
    def get_remaining_requests(self, client_id):
        """Get remaining requests for client"""
        limit = self._get_rate_limit_for_client(client_id)
        current_count, _ = self._sliding_window_check(client_id, 'check', limit)
        return max(0, limit - current_count)
    
    def reset_rate_limit(self, client_id):
        """Reset rate limit for client (admin function)"""
        if self.redis_available:
            keys = self.redis_client.keys(f"rate_limit:{client_id}:*")
            if keys:
                self.redis_client.delete(*keys)
        else:
            keys_to_remove = [k for k in self.memory_store.keys() if k.startswith(f"rate_limit:{client_id}:")]
            for key in keys_to_remove:
                del self.memory_store[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def require_rate_limit(endpoint=None):
    """Decorator to enforce rate limiting on endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not rate_limiter.check_rate_limit(endpoint):
                response = jsonify({
                    'success': False,
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Rate limit exceeded. Please try again later.',
                        'details': {
                            'limit': g.rate_limit_limit,
                            'current': g.rate_limit_current,
                            'reset_at': g.rate_limit_reset
                        }
                    }
                })
                response.status_code = 429
                
                # Add rate limit headers
                response.headers['X-RateLimit-Limit'] = str(g.rate_limit_limit)
                response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
                response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
                response.headers['Retry-After'] = '3600'  # 1 hour
                
                return response
            
            # Execute the original function
            result = f(*args, **kwargs)
            
            # Add rate limit headers to successful responses
            if hasattr(result, 'headers'):
                result.headers['X-RateLimit-Limit'] = str(g.rate_limit_limit)
                result.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
                result.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
            
            return result
        
        return decorated_function
    return decorator

def init_rate_limiter(app):
    """Initialize rate limiter with Flask app"""
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    global rate_limiter
    rate_limiter = RateLimiter(redis_url)
    
    @app.after_request
    def add_rate_limit_headers(response):
        """Add rate limit headers to all API responses"""
        if hasattr(g, 'rate_limit_limit') and request.path.startswith('/api/'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit_limit)
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
            response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
        return response
    
    return rate_limiter
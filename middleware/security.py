"""
Security middleware for Flask application.
Provides rate limiting, input validation, and security headers.
"""
from functools import wraps
from flask import request, jsonify, g
import time
import re
from collections import defaultdict

# In-memory rate limiting storage (use Redis in production)
rate_limit_storage = defaultdict(list)

def get_client_ip():
    """Get client IP address, handling proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def rate_limit(max_requests=100, window_seconds=3600):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_client_ip()
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Clean old entries
            rate_limit_storage[client_ip] = [
                t for t in rate_limit_storage[client_ip] 
                if t > window_start
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({
                    'status': 429,
                    'message': 'Rate limit exceeded. Please try again later.'
                }), 429
            
            # Record this request
            rate_limit_storage[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_required(f):
    """Decorator to require JSON content type for POST/PUT requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT'] and not request.is_json:
            return jsonify({
                'status': 400,
                'message': 'Content-Type must be application/json'
            }), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_positive_number(value, param_name):
    """Validate that a value is a positive number."""
    try:
        num = float(value)
        if num <= 0:
            return None, f"Invalid {param_name}: must be positive"
        return num, None
    except (TypeError, ValueError):
        return None, f"Invalid {param_name}: must be a number"

def validate_non_negative_number(value, param_name):
    """Validate that a value is a non-negative number."""
    try:
        num = float(value)
        if num < 0:
            return None, f"Invalid {param_name}: must be non-negative"
        return num, None
    except (TypeError, ValueError):
        return None, f"Invalid {param_name}: must be a number"

def validate_integer(value, param_name, min_val=None, max_val=None):
    """Validate that a value is an integer within optional bounds."""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            return None, f"Invalid {param_name}: must be at least {min_val}"
        if max_val is not None and num > max_val:
            return None, f"Invalid {param_name}: must be at most {max_val}"
        return num, None
    except (TypeError, ValueError):
        return None, f"Invalid {param_name}: must be an integer"

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal."""
    from werkzeug.utils import secure_filename
    if not filename:
        return None
    
    # Use werkzeug's secure_filename
    safe_name = secure_filename(filename)
    
    # Additional checks
    if not safe_name or '.' not in safe_name:
        return None
    
    # Limit filename length
    if len(safe_name) > 255:
        name, ext = safe_name.rsplit('.', 1)
        safe_name = name[:250] + '.' + ext
    
    return safe_name

def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    return response

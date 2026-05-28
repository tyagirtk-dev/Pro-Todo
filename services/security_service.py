"""
Security service for rate limiting, input validation, and security headers.
"""
from functools import wraps
from flask import request, current_app, make_response
from datetime import datetime, timedelta
from collections import defaultdict
import re
import bleach

class SecurityService:
    """Security service for rate limiting and input sanitization."""
    
    # Rate limiting storage (in production, use Redis)
    _rate_limit_storage = defaultdict(list)
    
    @classmethod
    def check_rate_limit(cls, key, action, limit=None, window=None):
        """
        Check if action exceeds rate limit.
        
        Args:
            key: Identifier for rate limiting (e.g., IP address)
            action: Action being performed (e.g., 'login')
            limit: Maximum number of attempts
            window: Time window in seconds
            
        Returns:
            bool: True if under limit, False if exceeded
        """
        if limit is None:
            limit = 5  # Default 5 attempts
        if window is None:
            window = 300  # Default 5 minutes
        
        storage_key = f"{key}:{action}"
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)
        
        # Clean old entries
        cls._rate_limit_storage[storage_key] = [
            timestamp for timestamp in cls._rate_limit_storage[storage_key]
            if timestamp > cutoff
        ]
        
        # Check limit
        if len(cls._rate_limit_storage[storage_key]) >= limit:
            return False
        
        return True
    
    @classmethod
    def record_failed_attempt(cls, key, action):
        """
        Record a failed attempt for rate limiting.
        
        Args:
            key: Identifier for rate limiting
            action: Action being performed
        """
        storage_key = f"{key}:{action}"
        cls._rate_limit_storage[storage_key].append(datetime.utcnow())
    
    @classmethod
    def clear_rate_limit(cls, key, action):
        """
        Clear rate limit for successful actions.
        
        Args:
            key: Identifier for rate limiting
            action: Action being performed
        """
        storage_key = f"{key}:{action}"
        cls._rate_limit_storage[storage_key] = []
    
    @classmethod
    def sanitize_input(cls, text, allow_html=False):
        """
        Sanitize user input to prevent XSS.
        
        Args:
            text: Input text to sanitize
            allow_html: Whether to allow safe HTML
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        if allow_html:
            # Allow safe HTML tags
            allowed_tags = [
                'p', 'br', 'b', 'i', 'u', 'em', 'strong', 'a',
                'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'blockquote', 'code', 'pre', 'img', 'span', 'div'
            ]
            allowed_attrs = {
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'title'],
                'span': ['style', 'class'],
                'div': ['style', 'class']
            }
            return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs)
        else:
            # Strip all HTML
            return bleach.clean(text, tags=[], attributes={}, strip=True)
    
    @classmethod
    def add_security_headers(cls, response):
        """
        Add security headers to HTTP response.
        
        Args:
            response: Flask response object
            
        Returns:
            Response with added headers
        """
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        
        return response
    
    @classmethod
    def validate_password_strength(cls, password):
        """
        Check password strength.
        
        Args:
            password: Password to check
            
        Returns:
            tuple: (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @classmethod
    def allowed_file(cls, filename, allowed_extensions):
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions
            
        Returns:
            bool: True if allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

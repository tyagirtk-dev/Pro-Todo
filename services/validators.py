"""
Validation utilities for user input.
"""
import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError

def validate_username(username):
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    # Username can contain letters, numbers, dots, and underscores
    pattern = r'^[a-zA-Z0-9._]+$'
    return bool(re.match(pattern, username))

def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate_email_lib(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        bool: True if strong enough, False otherwise
    """
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_full_name(name):
    """
    Validate full name.
    
    Args:
        name: Full name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name) < 2 or len(name) > 100:
        return False
    
    # Name can contain letters, spaces, dots, hyphens, and apostrophes
    pattern = r'^[a-zA-Z\s\.\-\']+$'
    return bool(re.match(pattern, name))

def sanitize_html_content(content):
    """
    Basic HTML sanitization.
    
    Args:
        content: HTML content to sanitize
        
    Returns:
        str: Sanitized HTML
    """
    if not content:
        return ""
    
    # Remove script tags and javascript: protocols
    content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    content = re.sub(r'on\w+="[^"]*"', '', content, flags=re.IGNORECASE)
    content = re.sub(r'on\w+=\'[^\']*\'', '', content, flags=re.IGNORECASE)
    
    return content

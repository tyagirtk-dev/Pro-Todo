"""
Helper utility functions for common operations.
"""
from datetime import datetime
import json
import os

def format_datetime(dt, format_type='full'):
    """
    Format datetime object to readable string.
    
    Args:
        dt: datetime object
        format_type: 'full', 'date', 'time', or 'relative'
        
    Returns:
        str: Formatted datetime string
    """
    if not dt:
        return ""
    
    if format_type == 'full':
        return dt.strftime('%B %d, %Y at %I:%M %p')
    elif format_type == 'date':
        return dt.strftime('%B %d, %Y')
    elif format_type == 'time':
        return dt.strftime('%I:%M %p')
    elif format_type == 'relative':
        return get_relative_time(dt)
    
    return str(dt)

def get_relative_time(dt):
    """
    Get relative time string (e.g., "2 hours ago").
    
    Args:
        dt: datetime object
        
    Returns:
        str: Relative time description
    """
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds // 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds // 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"

def truncate_text(text, length=100, suffix='...'):
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix

def generate_slug(text):
    """
    Generate URL-friendly slug from text.
    
    Args:
        text: Text to convert to slug
        
    Returns:
        str: URL-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    
    return slug

def get_file_size(size_in_bytes):
    """
    Format file size to human-readable format.
    
    Args:
        size_in_bytes: Size in bytes
        
    Returns:
        str: Formatted file size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    
    return f"{size_in_bytes:.1f} TB"

def is_ajax_request():
    """
    Check if current request is AJAX.
    
    Returns:
        bool: True if AJAX request, False otherwise
    """
    from flask import request
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def json_response(data, status_code=200):
    """
    Create JSON response.
    
    Args:
        data: Data to serialize
        status_code: HTTP status code
        
    Returns:
        Flask response object
    """
    from flask import jsonify
    response = jsonify(data)
    response.status_code = status_code
    return response

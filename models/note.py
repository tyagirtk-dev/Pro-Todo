"""
Note model for storing user's notes with rich features.
Includes support for pinning, archiving, colors, and version tracking.
"""
from datetime import datetime
from app import db
from sqlalchemy import Index
import bleach

# List of allowed HTML tags for note content sanitization
ALLOWED_TAGS = [
    'p', 'br', 'b', 'i', 'u', 'em', 'strong', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre',
    'img', 'span', 'div', 'table', 'tr', 'td', 'th'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'span': ['style', 'class'],
    'div': ['style', 'class'],
    'p': ['style', 'class'],
    'table': ['class', 'border'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan']
}

class Note(db.Model):
    """Note model for user-generated content."""
    __tablename__ = 'notes'
    
    # Color options for notes
    COLORS = {
        'default': '#ffffff',
        'red': '#ffebee',
        'pink': '#fce4ec',
        'purple': '#f3e5f5',
        'deep-purple': '#ede7f6',
        'indigo': '#e8eaf6',
        'blue': '#e3f2fd',
        'light-blue': '#e1f5fe',
        'cyan': '#e0f7fa',
        'teal': '#e0f2f1',
        'green': '#e8f5e9',
        'light-green': '#f1f8e9',
        'lime': '#f9fbe7',
        'yellow': '#fffde7',
        'amber': '#fff8e1',
        'orange': '#fff3e0',
        'deep-orange': '#fbe9e7',
        'brown': '#efebe9',
        'grey': '#f5f5f5',
        'blue-grey': '#eceff1'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Content fields
    title = db.Column(db.String(200), nullable=False, default='Untitled')
    content = db.Column(db.Text, nullable=True)
    content_sanitized = db.Column(db.Text, nullable=True)  # Sanitized version for display
    
    # Metadata
    color = db.Column(db.String(50), nullable=False, default='default')
    is_pinned = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Statistics
    word_count = db.Column(db.Integer, default=0)
    character_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    author = relationship('User', back_populates='notes')
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_pinned_archived', 'user_id', 'is_pinned', 'is_archived'),
        Index('idx_user_updated', 'user_id', 'updated_at'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )
    
    def sanitize_content(self):
        """
        Sanitize HTML content to prevent XSS attacks.
        Uses bleach library to allow only safe HTML tags and attributes.
        """
        if self.content:
            self.content_sanitized = bleach.clean(
                self.content,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            )
            self.update_statistics()
    
    def update_statistics(self):
        """Calculate and update word count and character count."""
        if self.content:
            # Remove HTML tags for accurate counting
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.content, 'html.parser')
            text = soup.get_text()
            
            self.character_count = len(text)
            self.word_count = len(text.split())
        else:
            self.character_count = 0
            self.word_count = 0
    
    def toggle_pin(self):
        """Toggle pinned status of the note."""
        self.is_pinned = not self.is_pinned
        return self.is_pinned
    
    def toggle_archive(self):
        """Toggle archived status of the note."""
        self.is_archived = not self.is_archived
        # When archiving, automatically unpin
        if self.is_archived:
            self.is_pinned = False
        return self.is_archived
    
    def to_dict(self):
        """Convert note model to dictionary for API responses."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_sanitized': self.content_sanitized,
            'color': self.color,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Note {self.title} by User {self.user_id}>'

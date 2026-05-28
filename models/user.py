"""
User model for authentication and profile management.
Handles user data, password hashing, and verification status.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    """User account model with authentication and profile fields."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True, default='default-avatar.png')
    
    # Verification and status
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = relationship('Note', back_populates='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set user password using scrypt algorithm.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(
            password,
            method='scrypt',
            salt_length=16
        )
    
    def check_password(self, password):
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Mark user's email as verified."""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    def is_admin(self):
        """Check if user has admin privileges."""
        return False  # Implement admin logic if needed
    
    def to_dict(self):
        """Convert user model to dictionary for API responses."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

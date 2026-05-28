"""
Authentication routes for user registration, login, email verification,
and password management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import db
from models.user import User
from services.email_service import send_verification_email, send_password_reset_email
from services.security_service import SecurityService
from utils.validators import validate_password, validate_email, validate_username
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

# Initialize token serializer for secure token generation
def get_token_serializer():
    """Get token serializer for generating secure tokens."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Server-side validation
        errors = []
        
        if not full_name or len(full_name) < 2 or len(full_name) > 100:
            errors.append('Full name must be between 2 and 100 characters.')
        
        if not validate_username(username):
            errors.append('Username must be 3-50 characters and can only contain letters, numbers, dots, and underscores.')
        
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        
        if not validate_password(password):
            errors.append('Password must be at least 8 characters and contain uppercase, lowercase, number, and special character.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            full_name=full_name,
            username=username,
            email=email
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user)
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        # Rate limiting
        if not SecurityService.check_rate_limit(request.remote_addr, 'login'):
            flash('Too many login attempts. Please try again later.', 'danger')
            return render_template('login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_verified:
                # Resend verification email
                send_verification_email(user)
                flash('Please verify your email before logging in. A new verification email has been sent.', 'warning')
                return render_template('login.html')
            
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('login.html')
            
            # Login successful
            login_user(user, remember=remember)
            SecurityService.clear_rate_limit(request.remote_addr, 'login')
            
            # Update last login time
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard.home'))
        
        else:
            SecurityService.record_failed_attempt(request.remote_addr, 'login')
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user's email address using secure token."""
    serializer = get_token_serializer()
    
    try:
        # Load user email from token (expires in 24 hours)
        email = serializer.loads(token, max_age=86400)
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid verification link. Please register again.', 'danger')
            return redirect(url_for('auth.register'))
        
        if user.is_verified:
            flash('Email already verified. You can now log in.', 'info')
            return redirect(url_for('auth.login'))
        
        # Verify the user
        user.verify_email()
        db.session.commit()
        
        flash('Email verified successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    except SignatureExpired:
        flash('Verification link has expired. Please register again to receive a new link.', 'danger')
        return redirect(url_for('auth.register'))
    
    except BadSignature:
        flash('Invalid verification link.', 'danger')
        return redirect(url_for('auth.register'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # Rate limiting
        if not SecurityService.check_rate_limit(request.remote_addr, 'password_reset'):
            flash('Too many requests. Please try again later.', 'danger')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security (don't reveal if email exists)
        if user:
            send_password_reset_email(user)
            flash('If an account exists with that email, you will receive password reset instructions.', 'success')
        else:
            flash('If an account exists with that email, you will receive password reset instructions.', 'success')
        
        SecurityService.clear_rate_limit(request.remote_addr, 'password_reset')
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    serializer = get_token_serializer()
    
    try:
        # Load user email from token (expires in 30 minutes)
        email = serializer.loads(token, max_age=1800)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid reset link.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            errors = []
            
            if not validate_password(password):
                errors.append('Password must be at least 8 characters and contain uppercase, lowercase, number, and special character.')
            
            if password != confirm_password:
                errors.append('Passwords do not match.')
            
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('reset_password.html', token=token)
            
            # Update password
            user.set_password(password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Password reset successful! You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        
        return render_template('reset_password.html', token=token)
    
    except SignatureExpired:
        flash('Password reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    except BadSignature:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

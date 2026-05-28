"""
Dashboard routes for displaying user statistics, recent notes, and profile management.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.note import Note
from services.security_service import SecurityService
from utils.validators import validate_password, validate_username, validate_email
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def home():
    """Main dashboard view."""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    """Get user statistics for dashboard."""
    # Count total notes
    total_notes = Note.query.filter_by(user_id=current_user.id, is_archived=False).count()
    
    # Count pinned notes
    pinned_notes = Note.query.filter_by(user_id=current_user.id, is_pinned=True, is_archived=False).count()
    
    # Count archived notes
    archived_notes = Note.query.filter_by(user_id=current_user.id, is_archived=True).count()
    
    # Recent activity (notes created in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = Note.query.filter(
        and_(
            Note.user_id == current_user.id,
            Note.created_at >= week_ago
        )
    ).count()
    
    # Storage usage (approximate)
    total_size = db.session.query(func.sum(Note.character_count)).filter_by(user_id=current_user.id).scalar() or 0
    
    return jsonify({
        'total_notes': total_notes,
        'pinned_notes': pinned_notes,
        'archived_notes': archived_notes,
        'recent_activity': recent_activity,
        'storage_usage': total_size,
        'storage_limit': 10000000,  # 10MB limit for demo
        'storage_percentage': min(100, (total_size / 10000000) * 100)
    })

@dashboard_bp.route('/api/recent-notes')
@login_required
def get_recent_notes():
    """Get recent notes for dashboard."""
    limit = request.args.get('limit', 5, type=int)
    
    recent_notes = Note.query.filter_by(
        user_id=current_user.id,
        is_archived=False
    ).order_by(Note.updated_at.desc()).limit(limit).all()
    
    return jsonify({
        'notes': [note.to_dict() for note in recent_notes]
    })

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management page."""
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'update_profile':
            # Update profile information
            full_name = request.form.get('full_name', '').strip()
            username = request.form.get('username', '').strip().lower()
            email = request.form.get('email', '').strip().lower()
            
            errors = []
            
            if not full_name or len(full_name) < 2 or len(full_name) > 100:
                errors.append('Full name must be between 2 and 100 characters.')
            
            if username != current_user.username and not validate_username(username):
                errors.append('Invalid username format.')
            
            if username != current_user.username and User.query.filter_by(username=username).first():
                errors.append('Username already taken.')
            
            if email != current_user.email and not validate_email(email):
                errors.append('Invalid email address.')
            
            if email != current_user.email and User.query.filter_by(email=email).first():
                errors.append('Email already registered.')
            
            if errors:
                for error in errors:
                    flash(error, 'danger')
            else:
                current_user.full_name = full_name
                current_user.username = username
                current_user.email = email
                current_user.updated_at = datetime.utcnow()
                db.session.commit()
                flash('Profile updated successfully!', 'success')
        
        elif action == 'change_password':
            # Change password
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
            elif not validate_password(new_password):
                flash('New password must be at least 8 characters and contain uppercase, lowercase, number, and special character.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.set_password(new_password)
                current_user.updated_at = datetime.utcnow()
                db.session.commit()
                flash('Password changed successfully!', 'success')
        
        elif action == 'delete_account':
            # Delete account (requires confirmation)
            confirm_text = request.form.get('confirm_text', '')
            
            if confirm_text == 'DELETE MY ACCOUNT':
                # Delete all user notes first
                Note.query.filter_by(user_id=current_user.id).delete()
                db.session.delete(current_user)
                db.session.commit()
                
                from flask_login import logout_user
                logout_user()
                
                flash('Your account has been permanently deleted.', 'info')
                return redirect(url_for('auth.register'))
            else:
                flash('Please type DELETE MY ACCOUNT to confirm account deletion.', 'danger')
        
        return redirect(url_for('dashboard.profile'))
    
    return render_template('profile.html')

@dashboard_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Handle avatar upload."""
    if 'avatar' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    file = request.files['avatar']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    if file and SecurityService.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        filename = secure_filename(f"user_{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Resize and optimize image
        from PIL import Image
        img = Image.open(file)
        img.thumbnail((200, 200))
        img.save(filepath, optimize=True, quality=85)
        
        # Update user avatar
        current_user.avatar = filename
        db.session.commit()
        
        flash('Avatar updated successfully!', 'success')
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF.', 'danger')
    
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/archive')
@login_required
def archive():
    """View archived notes."""
    return render_template('archive.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    """Application settings page."""
    return render_template('settings.html')

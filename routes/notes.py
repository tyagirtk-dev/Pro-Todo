"""
Note management routes for CRUD operations, archiving, pinning, and search.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from models.note import Note
from services.security_service import SecurityService
from datetime import datetime
from sqlalchemy import or_, and_
import json

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

@notes_bp.route('/')
@login_required
def index():
    """Display notes index page."""
    return render_template('note_editor.html')

@notes_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """API endpoint to get user's notes with filtering."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    show_archived = request.args.get('archived', 'false').lower() == 'true'
    color = request.args.get('color', '')
    sort_by = request.args.get('sort_by', 'updated_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Base query
    query = Note.query.filter_by(user_id=current_user.id)
    
    # Filter archived/pinned
    if show_archived:
        query = query.filter_by(is_archived=True)
    else:
        query = query.filter_by(is_archived=False)
    
    # Search in title and content
    if search:
        query = query.filter(
            or_(
                Note.title.ilike(f'%{search}%'),
                Note.content.ilike(f'%{search}%')
            )
        )
    
    # Filter by color
    if color and color in Note.COLORS:
        query = query.filter_by(color=color)
    
    # Sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Note, sort_by).desc())
    else:
        query = query.order_by(getattr(Note, sort_by).asc())
    
    # Pagination
    paginated_notes = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'notes': [note.to_dict() for note in paginated_notes.items],
        'total': paginated_notes.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated_notes.pages
    })

@notes_bp.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    """Create a new note."""
    data = request.get_json()
    
    title = data.get('title', 'Untitled').strip()[:200]
    content = data.get('content', '')
    color = data.get('color', 'default')
    
    if color not in Note.COLORS:
        color = 'default'
    
    note = Note(
        user_id=current_user.id,
        title=title or 'Untitled',
        content=content,
        color=color
    )
    
    note.sanitize_content()
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'note': note.to_dict(),
        'message': 'Note created successfully'
    }), 201

@notes_bp.route('/api/notes/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """Get a specific note by ID."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return jsonify(note.to_dict())

@notes_bp.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """Update an existing note."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    
    if 'title' in data:
        note.title = data['title'].strip()[:200] or 'Untitled'
    
    if 'content' in data:
        note.content = data['content']
        note.sanitize_content()
    
    if 'color' in data and data['color'] in Note.COLORS:
        note.color = data['color']
    
    note.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'note': note.to_dict(),
        'message': 'Note updated successfully'
    })

@notes_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete a note permanently."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Note deleted successfully'
    })

@notes_bp.route('/api/notes/<int:note_id>/pin', methods=['POST'])
@login_required
def toggle_pin(note_id):
    """Toggle pin status of a note."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    is_pinned = note.toggle_pin()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_pinned': is_pinned,
        'message': 'Note pinned' if is_pinned else 'Note unpinned'
    })

@notes_bp.route('/api/notes/<int:note_id>/archive', methods=['POST'])
@login_required
def toggle_archive(note_id):
    """Toggle archive status of a note."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    is_archived = note.toggle_archive()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_archived': is_archived,
        'message': 'Note archived' if is_archived else 'Note restored'
    })

@notes_bp.route('/api/notes/bulk', methods=['POST'])
@login_required
def bulk_action():
    """Perform bulk actions on multiple notes."""
    data = request.get_json()
    note_ids = data.get('note_ids', [])
    action = data.get('action', '')
    
    if not note_ids:
        return jsonify({'error': 'No notes selected'}), 400
    
    notes = Note.query.filter(
        Note.id.in_(note_ids),
        Note.user_id == current_user.id
    ).all()
    
    if action == 'delete':
        for note in notes:
            db.session.delete(note)
        message = f'{len(notes)} notes deleted'
    
    elif action == 'archive':
        for note in notes:
            note.is_archived = True
            note.is_pinned = False
        message = f'{len(notes)} notes archived'
    
    elif action == 'restore':
        for note in notes:
            note.is_archived = False
        message = f'{len(notes)} notes restored'
    
    elif action == 'pin':
        for note in notes:
            if not note.is_archived:
                note.is_pinned = True
        message = f'{len(notes)} notes pinned'
    
    elif action == 'unpin':
        for note in notes:
            note.is_pinned = False
        message = f'{len(notes)} notes unpinned'
    
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message
    })

@notes_bp.route('/api/colors', methods=['GET'])
@login_required
def get_colors():
    """Get available note colors."""
    return jsonify({'colors': Note.COLORS})

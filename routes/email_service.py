"""
Email service for sending verification emails, password reset emails,
and other notifications using Flask-Mail.
"""
from flask import render_template, current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import mail
from threading import Thread
import logging

def send_async_email(app, msg):
    """
    Send email asynchronously to avoid blocking the request.
    
    Args:
        app: Flask application instance
        msg: Email message to send
    """
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")

def send_email(to, subject, template, **kwargs):
    """
    Send email using template.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        template: Template name to render
        **kwargs: Variables to pass to template
    """
    app = current_app._get_current_object()
    
    msg = Message(
        subject=subject,
        recipients=[to],
        html=render_template(template, **kwargs),
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Send email in background thread
    thr = Thread(target=send_async_email, args=(app, msg))
    thr.start()
    
    return thr

def generate_verification_token(email):
    """
    Generate secure token for email verification.
    
    Args:
        email: User's email address
        
    Returns:
        str: Secure token for email verification
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def confirm_verification_token(token, expiration=86400):
    """
    Confirm email verification token.
    
    Args:
        token: Token to verify
        expiration: Token expiration in seconds
        
    Returns:
        str or None: Email if token valid, None otherwise
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=expiration)
        return email
    except:
        return None

def send_verification_email(user):
    """
    Send email verification link to user.
    
    Args:
        user: User object to send verification to
    """
    token = generate_verification_token(user.email)
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    send_email(
        to=user.email,
        subject='Verify Your Email - MindVault Pro',
        template='emails/verification.html',
        user=user,
        verify_url=verify_url
    )
    
    current_app.logger.info(f"Verification email sent to {user.email}")

def generate_reset_token(email):
    """
    Generate secure token for password reset.
    
    Args:
        email: User's email address
        
    Returns:
        str: Secure token for password reset
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')

def confirm_reset_token(token, expiration=1800):
    """
    Confirm password reset token.
    
    Args:
        token: Token to verify
        expiration: Token expiration in seconds
        
    Returns:
        str or None: Email if token valid, None otherwise
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
        return email
    except:
        return None

def send_password_reset_email(user):
    """
    Send password reset link to user.
    
    Args:
        user: User object to send reset link to
    """
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    send_email(
        to=user.email,
        subject='Reset Your Password - MindVault Pro',
        template='emails/password_reset.html',
        user=user,
        reset_url=reset_url
    )
    
    current_app.logger.info(f"Password reset email sent to {user.email}")

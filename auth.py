from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from datetime import datetime, timedelta
import jwt

def generate_tokens(user_id):
    """Generate access and refresh tokens for a user"""
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    return access_token, refresh_token

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=["HS256"]
            )
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

def premium_required(f):
    """Decorator to require premium role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if current_user.role not in ['admin', 'premium']:
            return jsonify({'error': 'Premium access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

def rate_limit_by_user(f):
    """Decorator to implement rate limiting per user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            # Check user's rate limit
            user_id = current_user.id
            # Implement rate limiting logic here
            # For now, just allow all requests
            pass
        
        return f(*args, **kwargs)
    
    return decorated

def track_user_activity(f):
    """Decorator to track user activity"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            # Update last activity
            current_user.last_login = datetime.utcnow()
            db.session.commit()
        
        return f(*args, **kwargs)
    
    return decorated

def get_user_from_token(token):
    """Extract user from JWT token"""
    try:
        data = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=["HS256"]
        )
        user_id = data['user_id']
        return User.query.get(user_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def create_user_session(user, request_data):
    """Create a new user session for analytics"""
    from models import UserSession
    
    # Detect device type
    user_agent = request_data.get('user_agent', '')
    device_type = 'desktop'
    if 'Mobile' in user_agent:
        device_type = 'mobile'
    elif 'Tablet' in user_agent:
        device_type = 'tablet'
    
    # Detect browser
    browser = 'Unknown'
    if 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    
    # Detect OS
    os = 'Unknown'
    if 'Windows' in user_agent:
        os = 'Windows'
    elif 'Mac' in user_agent:
        os = 'macOS'
    elif 'Linux' in user_agent:
        os = 'Linux'
    elif 'Android' in user_agent:
        os = 'Android'
    elif 'iOS' in user_agent:
        os = 'iOS'
    
    session = UserSession(
        user_id=user.id,
        session_id=request_data.get('session_id'),
        ip_address=request_data.get('ip_address'),
        user_agent=user_agent,
        device_type=device_type,
        browser=browser,
        os=os,
        latitude=request_data.get('latitude'),
        longitude=request_data.get('longitude'),
        country=request_data.get('country'),
        city=request_data.get('city')
    )
    
    db.session.add(session)
    db.session.commit()
    
    return session

def update_session_metrics(session_id, **kwargs):
    """Update session metrics"""
    from models import UserSession
    
    session = UserSession.query.filter_by(session_id=session_id).first()
    if session:
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        db.session.commit()

def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR']
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ['REMOTE_ADDR']

def get_user_agent():
    """Get user agent from request"""
    return request.headers.get('User-Agent', '')

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text
    
    # Basic XSS prevention
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def log_security_event(event_type, user_id=None, details=None, ip_address=None):
    """Log security events for monitoring"""
    # In production, this would log to a security monitoring system
    current_app.logger.warning(
        f"Security Event: {event_type} | User: {user_id} | "
        f"IP: {ip_address or get_client_ip()} | Details: {details}"
    )

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_compress import Compress
from flask_talisman import Talisman
from prometheus_flask_exporter import PrometheusMetrics
import os
import json
from datetime import datetime, timedelta
import time
import requests
from dotenv import load_dotenv
import logging
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Import models and services
from models import db, User, Prediction, WeatherRequest, ModelPerformance, UserSession
from schemas import *
from auth import *
from ml_service import ml_service

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///agrismart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Redis configuration
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = app.config['REDIS_URL']

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cache = Cache(app)
Compress(app)
Talisman(app, content_security_policy=None)
metrics = PrometheusMetrics(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({'error': 'Validation error', 'message': 'Invalid input data'}), 422

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected'
    })

# API Routes

## Authentication Routes
@app.route('/api/v1/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = user_schema.validate(data)
        if errors:
            return jsonify({'error': 'Validation error', 'details': errors}), 422
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User already exists', 'message': 'Email is already registered'}), 409
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username taken', 'message': 'Username is already taken'}), 409
        
        # Validate password strength
        is_strong, message = validate_password_strength(data['password'])
        if not is_strong:
            return jsonify({'error': 'Weak password', 'message': message}), 422
        
        # Create user
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = user_login_schema.validate(data)
        if errors:
            return jsonify({'error': 'Validation error', 'details': errors}), 422
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials', 'message': 'Email or password is incorrect'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account disabled', 'message': 'Your account has been disabled'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Login user
        login_user(user)
        
        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)
        
        # Create session for analytics
        session_data = {
            'session_id': access_token[:20],
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent(),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude')
        }
        create_user_session(user, session_data)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500

@app.route('/api/v1/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed', 'message': str(e)}), 500

@app.route('/api/v1/auth/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed', 'message': str(e)}), 500

## User Management Routes
@app.route('/api/v1/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return jsonify({'error': 'Profile retrieval failed', 'message': str(e)}), 500

@app.route('/api/v1/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate input
        errors = user_update_schema.validate(data)
        if errors:
            return jsonify({'error': 'Validation error', 'details': errors}), 422
        
        # Update fields
        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Profile update failed', 'message': str(e)}), 500

## Crop Prediction Routes
@app.route('/api/v1/predictions', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def create_prediction():
    """Create a new crop prediction"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        # Validate input
        errors = prediction_input_schema.validate(data)
        if errors:
            return jsonify({'error': 'Validation error', 'details': errors}), 422
        
        # Make prediction using ML service
        prediction_result = ml_service.predict(data)
        
        # Store prediction in database
        prediction = Prediction(
            user_id=user.id,
            nitrogen=data['nitrogen'],
            phosphorus=data['phosphorus'],
            potassium=data['potassium'],
            temperature=data['temperature'],
            humidity=data['humidity'],
            ph=data['ph'],
            rainfall=data['rainfall'],
            predicted_crop=prediction_result['predicted_crop'],
            confidence_score=prediction_result['confidence_score'],
            alternative_crops=prediction_result['alternative_crops'],
            model_version=prediction_result['model_version'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            location_name=data.get('location_name'),
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        # Emit real-time update via WebSocket
        socketio.emit('prediction_created', {
            'user_id': user.id,
            'prediction': prediction.to_dict()
        })
        
        return jsonify({
            'success': True,
            'message': 'Prediction created successfully',
            'data': {
                'prediction': prediction.to_dict(),
                'ml_result': prediction_result
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Prediction creation error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

@app.route('/api/v1/predictions', methods=['GET'])
@jwt_required()
def get_predictions():
    """Get user's prediction history"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        predictions = Prediction.query.filter_by(user_id=user.id)\
            .order_by(Prediction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': [pred.to_dict() for pred in predictions.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': predictions.total,
                    'pages': predictions.pages,
                    'has_next': predictions.has_next,
                    'has_prev': predictions.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction retrieval error: {str(e)}")
        return jsonify({'error': 'Prediction retrieval failed', 'message': str(e)}), 500

@app.route('/api/v1/predictions/<int:prediction_id>', methods=['GET'])
@jwt_required()
def get_prediction(prediction_id):
    """Get specific prediction details"""
    try:
        current_user_id = get_jwt_identity()
        prediction = Prediction.query.filter_by(
            id=prediction_id, 
            user_id=current_user_id
        ).first()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        return jsonify({
            'success': True,
            'data': prediction.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction retrieval error: {str(e)}")
        return jsonify({'error': 'Prediction retrieval failed', 'message': str(e)}), 500

## Weather Routes
@app.route('/api/v1/weather/realtime', methods=['GET'])
@jwt_required()
@limiter.limit("30 per hour")
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_realtime_weather():
    """Get real-time weather data"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get coordinates from query params or user profile
        lat = request.args.get('lat', user.latitude or 20.5937, type=float)
        lon = request.args.get('lon', user.longitude or 78.9629, type=float)
        location_name = request.args.get('location_name', user.location or 'Unknown')
        
        start_time = time.time()
        
        # Fetch weather data (using existing logic from app.py)
        weather_data = fetch_weather_data(lat, lon)
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Store weather request for analytics
        weather_request = WeatherRequest(
            user_id=user.id,
            latitude=lat,
            longitude=lon,
            location_name=location_name,
            temperature=weather_data.get('temperature'),
            humidity=weather_data.get('humidity'),
            rainfall=weather_data.get('rainfall'),
            description=weather_data.get('description'),
            icon=weather_data.get('icon'),
            data_source=weather_data.get('data_source', 'Simulation'),
            api_status='success' if weather_data.get('success') else 'error',
            response_time=response_time,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        db.session.add(weather_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': weather_data
        }), 200
        
    except Exception as e:
        logger.error(f"Weather retrieval error: {str(e)}")
        return jsonify({'error': 'Weather retrieval failed', 'message': str(e)}), 500

## ML Model Routes
@app.route('/api/v1/ml/model/info', methods=['GET'])
@jwt_required()
def get_model_info():
    """Get ML model information"""
    try:
        model_info = ml_service.get_model_info()
        
        return jsonify({
            'success': True,
            'data': model_info
        }), 200
        
    except Exception as e:
        logger.error(f"Model info retrieval error: {str(e)}")
        return jsonify({'error': 'Model info retrieval failed', 'message': str(e)}), 500

@app.route('/api/v1/ml/model/evaluate', methods=['POST'])
@jwt_required()
@admin_required
def evaluate_model():
    """Evaluate ML model performance"""
    try:
        evaluation = ml_service.evaluate_model()
        
        # Store performance metrics
        performance = ModelPerformance(
            model_version=evaluation['model_version'],
            model_type=evaluation.get('model_type', 'RandomForest'),
            accuracy=evaluation['accuracy'],
            precision=evaluation.get('classification_report', {}).get('weighted avg', {}).get('precision'),
            recall=evaluation.get('classification_report', {}).get('weighted avg', {}).get('recall'),
            f1_score=evaluation.get('classification_report', {}).get('weighted avg', {}).get('f1-score'),
            confusion_matrix=evaluation['confusion_matrix'],
            training_date=datetime.fromisoformat(evaluation['evaluation_timestamp']),
            dataset_size=evaluation['test_samples'],
            features_used=evaluation.get('features_used', [])
        )
        
        db.session.add(performance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model evaluation completed',
            'data': evaluation
        }), 200
        
    except Exception as e:
        logger.error(f"Model evaluation error: {str(e)}")
        return jsonify({'error': 'Model evaluation failed', 'message': str(e)}), 500

@app.route('/api/v1/ml/model/retrain', methods=['POST'])
@jwt_required()
@admin_required
def retrain_model():
    """Retrain ML model"""
    try:
        # This is a long-running task, should be moved to Celery in production
        performance = ml_service.train_model()
        
        # Store performance metrics
        model_performance = ModelPerformance(
            model_version=performance['model_version'],
            model_type=performance['model_type'],
            accuracy=performance['accuracy'],
            precision=performance.get('classification_report', {}).get('weighted avg', {}).get('precision'),
            recall=performance.get('classification_report', {}).get('weighted avg', {}).get('recall'),
            f1_score=performance.get('classification_report', {}).get('weighted avg', {}).get('f1-score'),
            confusion_matrix=performance['confusion_matrix'],
            training_date=datetime.fromisoformat(performance['training_timestamp']),
            training_duration=performance['training_duration'],
            dataset_size=performance['dataset_size'],
            features_used=performance['features_used'],
            model_file_path=ml_service.model_path,
            model_file_size=os.path.getsize(ml_service.model_path) if os.path.exists(ml_service.model_path) else 0,
            scaler_file_path=ml_service.scaler_path
        )
        
        db.session.add(model_performance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model retraining completed',
            'data': performance
        }), 200
        
    except Exception as e:
        logger.error(f"Model retraining error: {str(e)}")
        return jsonify({'error': 'Model retraining failed', 'message': str(e)}), 500

## Analytics Routes
@app.route('/api/v1/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get user dashboard analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get user statistics
        total_predictions = Prediction.query.filter_by(user_id=user.id).count()
        recent_predictions = Prediction.query.filter_by(user_id=user.id)\
            .order_by(Prediction.created_at.desc())\
            .limit(5).all()
        
        # Get weather request statistics
        total_weather_requests = WeatherRequest.query.filter_by(user_id=user.id).count()
        recent_weather = WeatherRequest.query.filter_by(user_id=user.id)\
            .order_by(WeatherRequest.created_at.desc())\
            .limit(5).all()
        
        # Calculate success rate
        successful_predictions = Prediction.query.filter_by(
            user_id=user.id, 
            confidence_score__gte=0.7
        ).count()
        
        success_rate = (successful_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        analytics = {
            'user_stats': {
                'total_predictions': total_predictions,
                'success_rate': round(success_rate, 2),
                'total_weather_requests': total_weather_requests,
                'member_since': user.created_at.isoformat() if user.created_at else None
            },
            'recent_predictions': [pred.to_dict() for pred in recent_predictions],
            'recent_weather': [weather.to_dict() for weather in recent_weather],
            'model_info': ml_service.get_model_info()
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Analytics retrieval error: {str(e)}")
        return jsonify({'error': 'Analytics retrieval failed', 'message': str(e)}), 500

## WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Agrismart server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass

@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Join user-specific room for real-time updates"""
    user_id = data.get('user_id')
    if user_id:
        join_room(f'user_{user_id}')
        emit('joined_room', {'message': f'Joined user room {user_id}'})

## Legacy Routes (for backward compatibility)
@app.route('/')
def home():
    """Serve the modern React frontend"""
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
def legacy_predict():
    """Legacy prediction endpoint for backward compatibility"""
    try:
        data = request.get_json()
        
        # Make prediction using ML service
        prediction_result = ml_service.predict(data)
        
        return jsonify({
            'success': True,
            'predicted_crop': prediction_result['predicted_crop'],
            'confidence_score': prediction_result['confidence_score'],
            'alternative_crops': prediction_result['alternative_crops']
        }), 200
        
    except Exception as e:
        logger.error(f"Legacy prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

@app.route('/realtime-data')
def legacy_realtime_data():
    """Legacy real-time data endpoint for backward compatibility"""
    try:
        lat = request.args.get('lat', 20.5937, type=float)
        lon = request.args.get('lon', 78.9629, type=float)
        
        weather_data = fetch_weather_data(lat, lon)
        
        return jsonify(weather_data), 200
        
    except Exception as e:
        logger.error(f"Legacy weather error: {str(e)}")
        return jsonify({'error': 'Weather retrieval failed', 'message': str(e)}), 500

# Import weather functions from original app.py
def fetch_weather_data(lat, lon):
    """Fetch weather data from API or simulation"""
    # This function will be imported from the original app.py
    # For now, return a basic structure
    return {
        'success': True,
        'data_source': 'Simulation',
        'location': {'city': f'Location ({lat:.2f}, {lon:.2f})', 'lat': lat, 'lon': lon},
        'weather': {'temperature': 25.0, 'humidity': 70, 'rainfall': 0, 'description': 'Clear sky'},
        'soil': {'N': 70, 'P': 50, 'K': 100, 'ph': 6.5},
        'timestamp': datetime.now().isoformat()
    }

# Database initialization
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

# Main application entry point
if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

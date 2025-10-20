from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')  # user, admin, premium
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    weather_requests = db.relationship('WeatherRequest', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'role': self.role,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Prediction(db.Model):
    """Crop prediction model for storing prediction history"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Input parameters
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    
    # Prediction results
    predicted_crop = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    alternative_crops = db.Column(JSON)  # Store as JSON array
    model_version = db.Column(db.String(20), default='v1.0')
    
    # Location data
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'user_id': self.user_id,
            'input_parameters': {
                'nitrogen': self.nitrogen,
                'phosphorus': self.phosphorus,
                'potassium': self.potassium,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'ph': self.ph,
                'rainfall': self.rainfall
            },
            'prediction_results': {
                'predicted_crop': self.predicted_crop,
                'confidence_score': self.confidence_score,
                'alternative_crops': self.alternative_crops,
                'model_version': self.model_version
            },
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'location_name': self.location_name
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WeatherRequest(db.Model):
    """Weather data request model for analytics"""
    __tablename__ = 'weather_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Request details
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(100))
    
    # Weather data
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    description = db.Column(db.String(100))
    icon = db.Column(db.String(10))
    
    # API response details
    data_source = db.Column(db.String(50))  # 'OpenWeatherMap API' or 'Simulation'
    api_status = db.Column(db.String(20))  # 'success', 'error', 'rate_limited'
    response_time = db.Column(db.Float)  # in milliseconds
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        """Convert weather request to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'user_id': self.user_id,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'location_name': self.location_name
            },
            'weather_data': {
                'temperature': self.temperature,
                'humidity': self.humidity,
                'rainfall': self.rainfall,
                'description': self.description,
                'icon': self.icon
            },
            'api_details': {
                'data_source': self.data_source,
                'api_status': self.api_status,
                'response_time': self.response_time,
                'error_message': self.error_message
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ModelPerformance(db.Model):
    """Model performance tracking for ML model analytics"""
    __tablename__ = 'model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    
    # Model details
    model_version = db.Column(db.String(20), nullable=False, index=True)
    model_type = db.Column(db.String(50), default='RandomForest')
    
    # Performance metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    confusion_matrix = db.Column(JSON)
    
    # Training details
    training_date = db.Column(db.DateTime, default=datetime.utcnow)
    training_duration = db.Column(db.Float)  # in seconds
    dataset_size = db.Column(db.Integer)
    features_used = db.Column(JSON)
    
    # Model file info
    model_file_path = db.Column(db.String(255))
    model_file_size = db.Column(db.Integer)  # in bytes
    scaler_file_path = db.Column(db.String(255))
    
    def to_dict(self):
        """Convert model performance to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'model_details': {
                'version': self.model_version,
                'type': self.model_type
            },
            'performance_metrics': {
                'accuracy': self.accuracy,
                'precision': self.precision,
                'recall': self.recall,
                'f1_score': self.f1_score,
                'confusion_matrix': self.confusion_matrix
            },
            'training_details': {
                'training_date': self.training_date.isoformat() if self.training_date else None,
                'training_duration': self.training_duration,
                'dataset_size': self.dataset_size,
                'features_used': self.features_used
            },
            'model_files': {
                'model_file_path': self.model_file_path,
                'model_file_size': self.model_file_size,
                'scaler_file_path': self.scaler_file_path
            }
        }

class UserSession(db.Model):
    """User session tracking for analytics"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Session details
    session_id = db.Column(db.String(255), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    device_type = db.Column(db.String(20))  # 'desktop', 'mobile', 'tablet'
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    
    # Session metrics
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # in seconds
    page_views = db.Column(db.Integer, default=0)
    predictions_made = db.Column(db.Integer, default=0)
    
    # Location data
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    def to_dict(self):
        """Convert user session to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'user_id': self.user_id,
            'session_details': {
                'session_id': self.session_id,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'device_type': self.device_type,
                'browser': self.browser,
                'os': self.os
            },
            'session_metrics': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration': self.duration,
                'page_views': self.page_views,
                'predictions_made': self.predictions_made
            },
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'country': self.country,
                'city': self.city
            }
        }

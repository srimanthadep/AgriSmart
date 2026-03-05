from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Prediction, WeatherRequest, ModelPerformance, UserSession

class UserSchema(SQLAlchemyAutoSchema):
    """User schema for serialization/deserialization"""
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    location = fields.Str(validate=validate.Length(max=100))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))

class UserLoginSchema(Schema):
    """User login schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    """User update schema"""
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    location = fields.Str(validate=validate.Length(max=100))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))

class PredictionInputSchema(Schema):
    """Crop prediction input schema"""
    nitrogen = fields.Float(required=True, validate=validate.Range(min=0, max=1000))
    phosphorus = fields.Float(required=True, validate=validate.Range(min=0, max=1000))
    potassium = fields.Float(required=True, validate=validate.Range(min=0, max=1000))
    temperature = fields.Float(required=True, validate=validate.Range(min=-50, max=100))
    humidity = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    ph = fields.Float(required=True, validate=validate.Range(min=0, max=14))
    rainfall = fields.Float(required=True, validate=validate.Range(min=0, max=1000))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    location_name = fields.Str(validate=validate.Length(max=100))

class PredictionSchema(SQLAlchemyAutoSchema):
    """Prediction schema for serialization"""
    class Meta:
        model = Prediction
        load_instance = True
    
    user = fields.Nested(UserSchema, exclude=('predictions', 'weather_requests'))

class WeatherRequestSchema(Schema):
    """Weather request schema"""
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    location_name = fields.Str(validate=validate.Length(max=100))

class WeatherResponseSchema(Schema):
    """Weather response schema"""
    temperature = fields.Float()
    humidity = fields.Float()
    rainfall = fields.Float()
    description = fields.Str()
    icon = fields.Str()
    data_source = fields.Str()
    location = fields.Dict()
    timestamp = fields.DateTime()

class ModelPerformanceSchema(SQLAlchemyAutoSchema):
    """Model performance schema"""
    class Meta:
        model = ModelPerformance
        load_instance = True

class UserSessionSchema(SQLAlchemyAutoSchema):
    """User session schema"""
    class Meta:
        model = UserSession
        load_instance = True

class PaginationSchema(Schema):
    """Pagination schema for list endpoints"""
    page = fields.Int(validate=validate.Range(min=1), default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), default=20)
    total = fields.Int()
    pages = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()

class ErrorSchema(Schema):
    """Error response schema"""
    error = fields.Str(required=True)
    message = fields.Str(required=True)
    code = fields.Int()
    details = fields.Dict()

class SuccessSchema(Schema):
    """Success response schema"""
    success = fields.Bool(required=True)
    message = fields.Str()
    data = fields.Raw()

class CropRecommendationSchema(Schema):
    """Crop recommendation response schema"""
    predicted_crop = fields.Str(required=True)
    confidence_score = fields.Float(required=True)
    alternative_crops = fields.List(fields.Dict())
    model_version = fields.Str()
    input_parameters = fields.Dict()
    location = fields.Dict()
    timestamp = fields.DateTime()

# Schema instances for easy import
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_login_schema = UserLoginSchema()
user_update_schema = UserUpdateSchema()
prediction_input_schema = PredictionInputSchema()
prediction_schema = PredictionSchema()
predictions_schema = PredictionSchema(many=True)
weather_request_schema = WeatherRequestSchema()
weather_response_schema = WeatherResponseSchema()
model_performance_schema = ModelPerformanceSchema()
user_session_schema = UserSessionSchema()
pagination_schema = PaginationSchema()
error_schema = ErrorSchema()
success_schema = SuccessSchema()
crop_recommendation_schema = CropRecommendationSchema()

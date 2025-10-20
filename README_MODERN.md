# Agrismart - Modern Full-Stack Crop Recommendation System

A comprehensive, production-ready crop recommendation system built with modern technologies and best practices.

## 🚀 Features

### Core Functionality
- **ML-Powered Predictions**: Random Forest ensemble model for accurate crop recommendations
- **Real-time Weather Data**: Integration with OpenWeatherMap API for current weather conditions
- **Smart Fallbacks**: Intelligent simulated data when APIs are unavailable
- **Location-based Insights**: Automatic geolocation detection and location-specific recommendations

### Modern Architecture
- **Backend**: Flask with SQLAlchemy, JWT authentication, and RESTful APIs
- **Frontend**: React with TypeScript, Tailwind CSS, and modern state management
- **Database**: PostgreSQL with automated migrations
- **Caching**: Redis for performance optimization
- **Real-time**: WebSocket support for live updates
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Containerization**: Docker and Docker Compose for easy deployment

## 🏗️ Project Structure

```
agrismart/
├── app_modern.py              # Modern Flask application
├── models.py                  # SQLAlchemy ORM models
├── schemas.py                 # Marshmallow validation schemas
├── auth.py                    # Authentication utilities
├── ml_service.py              # ML model service
├── config.py                  # Configuration and API keys
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker services orchestration
├── Dockerfile                 # Flask app containerization
├── nginx.conf                 # Nginx reverse proxy config
├── prometheus.yml             # Monitoring configuration
├── init.sql                   # Database initialization
├── frontend/                  # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.cjs
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── stores/
│   │   ├── types/
│   │   └── index.css
│   └── index.html
└── grafana/                   # Monitoring dashboards
    ├── datasources/
    └── dashboards/
```

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local development)
- Node.js 16+ (for frontend development)

### 1. Environment Setup
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env with your configuration
# Add your OpenWeatherMap API key
OPENWEATHER_API_KEY=your_api_key_here
```

### 2. Start with Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
```

### 3. Local Development Setup
```bash
# Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app_modern.py

# Frontend
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key
- `JWT_SECRET_KEY`: Secret for JWT tokens

### API Keys
1. **OpenWeatherMap**: Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add to `config.py` or environment variables

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/profile` - Get user profile

### Crop Predictions
- `POST /api/v1/predictions/crop` - Get crop recommendation
- `GET /api/v1/predictions/history` - User prediction history
- `GET /api/v1/predictions/analytics` - Prediction analytics

### Weather Data
- `GET /api/v1/weather/realtime` - Real-time weather data
- `GET /api/v1/weather/history` - Weather request history

### Admin & ML Management
- `GET /api/v1/admin/users` - User management (admin only)
- `POST /api/v1/admin/model/retrain` - Retrain ML model
- `GET /api/v1/admin/model/performance` - Model performance metrics

## 🧠 Machine Learning

### Model Details
- **Algorithm**: Ensemble Random Forest Classifier
- **Features**: N, P, K, Temperature, Humidity, pH, Rainfall
- **Training Data**: Crop recommendation dataset
- **Performance**: High accuracy with cross-validation

### Model Management
- Automatic model persistence with joblib
- Performance monitoring and metrics
- Retraining capabilities via API
- Model versioning and rollback

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting and DDoS protection
- Input sanitization and validation
- CORS configuration
- Security headers (HSTS, CSP, etc.)
- SQL injection prevention
- XSS protection

## 📈 Monitoring & Observability

### Metrics Collected
- HTTP request rates and response times
- Error rates and status codes
- Database query performance
- ML model prediction accuracy
- User activity and sessions
- System resource usage

### Dashboards
- Application performance overview
- User engagement metrics
- ML model performance
- System health and alerts

## 🚀 Deployment

### Production Considerations
1. **SSL/TLS**: Configure HTTPS with proper certificates
2. **Environment**: Use production-grade environment variables
3. **Scaling**: Configure multiple app instances behind load balancer
4. **Backup**: Set up automated database backups
5. **Monitoring**: Configure alerting and incident response

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Backend Testing
```bash
# Run tests
pytest

# Coverage report
pytest --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

## 📝 Development Workflow

1. **Feature Development**: Create feature branches from `main`
2. **Code Quality**: Use pre-commit hooks for linting and formatting
3. **Testing**: Write tests for new features
4. **Documentation**: Update README and API docs
5. **Review**: Submit pull requests for code review
6. **Deployment**: Automated deployment on merge to main

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the docs folder for detailed guides
- **Community**: Join our discussions and Q&A sessions

## 🔄 Migration from Legacy

The modern version maintains backward compatibility with the original `agrismart_ui.html` and `app.py`. You can:

1. **Gradual Migration**: Use both versions simultaneously
2. **API Compatibility**: Legacy endpoints still work
3. **Data Migration**: Import existing data to new database
4. **Feature Parity**: All original features available in modern UI

---

**Built with ❤️ for modern agriculture technology**

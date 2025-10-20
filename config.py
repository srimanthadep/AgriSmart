# AgriSmart Configuration File
# Copy this file to config_local.py and add your actual API keys

# OpenWeatherMap API Configuration
# Get your free API key from: https://openweathermap.org/api
WEATHER_API_KEY = "80a157ac3828459be8ecd04f5dd5776a"

# Default location (India center)
DEFAULT_LAT = 20.5937
DEFAULT_LON = 78.9629

# API Settings
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
API_TIMEOUT = 10  # seconds

# Soil Data Simulation Settings
SOIL_UPDATE_INTERVAL = 3600  # 1 hour in seconds
LOCATION_BASED_SOIL = True   # Enable location-based soil characteristics

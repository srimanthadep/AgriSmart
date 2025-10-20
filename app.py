from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import joblib
import os
import requests
from datetime import datetime
import time

app = Flask(__name__)

# Load model and scaler
model = joblib.load('crop_recommendation_model.pkl')
scaler = joblib.load('scaler.pkl')

# Try to load configuration
try:
    from config import *
except ImportError:
    # Fallback configuration
    WEATHER_API_KEY = "YOUR_API_KEY_HERE"
    WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    DEFAULT_LAT = 20.5937
    DEFAULT_LON = 78.9629
    API_TIMEOUT = 10

# Crop info database for detailed results
CROP_INFO = {
    'rice': {
        'season': 'Kharif',
        'growing_period': '120-150 days',
        'soil_type': 'Clay loam',
        'water_need': 'High',
        'conditions': 'Warm, humid climate; clay loam soil; high water requirement.',
        'tips': 'Keep fields flooded, use nitrogen-rich fertilizer, control weeds early.'
    },
    'maize': {
        'season': 'Kharif',
        'growing_period': '90-120 days',
        'soil_type': 'Well-drained loam',
        'water_need': 'Moderate',
        'conditions': 'Well-drained loam; moderate water; warm temperatures.',
        'tips': 'Ensure good drainage, rotate crops, monitor for pests.'
    },
    'chickpea': {
        'season': 'Rabi',
        'growing_period': '90-120 days',
        'soil_type': 'Well-drained loam',
        'water_need': 'Moderate',
        'conditions': 'Cool, dry climate; well-drained loam; moderate water.',
        'tips': 'Avoid waterlogging, use disease-free seeds, inoculate with Rhizobium.'
    },
    'kidneybeans': {
        'season': 'Kharif',
        'growing_period': '80-100 days',
        'soil_type': 'Loamy soil',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; well-drained soil; moderate water.',
        'tips': 'Provide support for climbing varieties, control bean beetles.'
    },
    'pigeonpeas': {
        'season': 'Kharif',
        'growing_period': '150-180 days',
        'soil_type': 'Deep loam',
        'water_need': 'Low',
        'conditions': 'Drought-tolerant; deep soil; warm climate.',
        'tips': 'Drought-resistant, good for intercropping.'
    },
    'mothbeans': {
        'season': 'Kharif',
        'growing_period': '60-80 days',
        'soil_type': 'Sandy loam',
        'water_need': 'Low',
        'conditions': 'Drought-tolerant; sandy soil; hot climate.',
        'tips': 'Excellent for arid regions, good ground cover.'
    },
    'mungbean': {
        'season': 'Kharif',
        'growing_period': '60-90 days',
        'soil_type': 'Loamy soil',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; well-drained soil; moderate water.',
        'tips': 'Fast-growing, good for crop rotation.'
    },
    'blackgram': {
        'season': 'Kharif',
        'growing_period': '80-100 days',
        'soil_type': 'Clay loam',
        'water_need': 'Moderate',
        'conditions': 'Warm, humid climate; clay soil; moderate water.',
        'tips': 'Good for rice fallows, nitrogen-fixing.'
    },
    'lentil': {
        'season': 'Rabi',
        'growing_period': '80-110 days',
        'soil_type': 'Loamy soil',
        'water_need': 'Low',
        'conditions': 'Cool climate; well-drained soil; low water.',
        'tips': 'Nitrogen-fixing, good for crop rotation.'
    },
    'pomegranate': {
        'season': 'Year-round',
        'growing_period': '5-7 years to fruit',
        'soil_type': 'Deep loam',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; deep soil; moderate water.',
        'tips': 'Drought-tolerant, good for arid regions.'
    },
    'banana': {
        'season': 'Year-round',
        'growing_period': '9-12 months',
        'soil_type': 'Rich loam',
        'water_need': 'High',
        'conditions': 'Tropical climate; rich soil; high water.',
        'tips': 'Requires regular watering, protect from wind.'
    },
    'mango': {
        'season': 'Summer',
        'growing_period': '3-6 years to fruit',
        'soil_type': 'Deep loam',
        'water_need': 'Moderate',
        'conditions': 'Tropical climate; deep soil; moderate water.',
        'tips': 'Drought-tolerant, good for tropical regions.'
    },
    'grapes': {
        'season': 'Summer',
        'growing_period': '2-3 years to fruit',
        'soil_type': 'Well-drained loam',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; well-drained soil; moderate water.',
        'tips': 'Good trellis support, control pests.'
    },
    'watermelon': {
        'season': 'Summer',
        'growing_period': '70-90 days',
        'soil_type': 'Sandy loam',
        'water_need': 'High',
        'conditions': 'Hot climate; sandy soil; high water.',
        'tips': 'Requires lots of space, regular watering.'
    },
    'muskmelon': {
        'season': 'Summer',
        'growing_period': '70-90 days',
        'soil_type': 'Sandy loam',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; sandy soil; moderate water.',
        'tips': 'Good drainage, control powdery mildew.'
    },
    'apple': {
        'season': 'Fall',
        'growing_period': '3-5 years to fruit',
        'soil_type': 'Well-drained loam',
        'water_need': 'Moderate',
        'conditions': 'Cool climate; well-drained soil; moderate water.',
        'tips': 'Requires chilling hours, good pruning.'
    },
    'orange': {
        'season': 'Winter',
        'growing_period': '3-5 years to fruit',
        'soil_type': 'Well-drained loam',
        'water_need': 'Moderate',
        'conditions': 'Subtropical climate; well-drained soil; moderate water.',
        'tips': 'Frost-sensitive, good drainage needed.'
    },
    'papaya': {
        'season': 'Year-round',
        'growing_period': '6-9 months to fruit',
        'soil_type': 'Sandy loam',
        'water_need': 'Moderate',
        'conditions': 'Tropical climate; sandy soil; moderate water.',
        'tips': 'Fast-growing, protect from wind.'
    },
    'coconut': {
        'season': 'Year-round',
        'growing_period': '5-7 years to fruit',
        'soil_type': 'Sandy loam',
        'water_need': 'High',
        'conditions': 'Tropical climate; sandy soil; high water.',
        'tips': 'Requires coastal climate, regular watering.'
    },
    'cotton': {
        'season': 'Kharif',
        'growing_period': '150-180 days',
        'soil_type': 'Black soil',
        'water_need': 'Moderate',
        'conditions': 'Warm climate; black soil; moderate water.',
        'tips': 'Good for crop rotation, control bollworms.'
    },
    'jute': {
        'season': 'Kharif',
        'growing_period': '120-150 days',
        'soil_type': 'Alluvial soil',
        'water_need': 'High',
        'conditions': 'Warm, humid climate; alluvial soil; high water.',
        'tips': 'Requires flooding, good for fiber production.'
    },
    'coffee': {
        'season': 'Year-round',
        'growing_period': '3-4 years to fruit',
        'soil_type': 'Volcanic loam',
        'water_need': 'High',
        'conditions': 'Tropical highland climate; volcanic soil; high water.',
        'tips': 'Shade-grown, regular pruning needed.'
    }
}

@app.route('/')
def home():
    return send_file('agrismart_ui.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate and get inputs from form
        def get_float(name, min_val=None, max_val=None):
            val = request.form.get(name, None)
            if val is None:
                raise ValueError(f"Missing value for {name}")
            try:
                val = float(val)
            except Exception:
                raise ValueError(f"Invalid value for {name}")
            if min_val is not None and val < min_val:
                raise ValueError(f"{name} must be at least {min_val}")
            if max_val is not None and val > max_val:
                raise ValueError(f"{name} must be at least {max_val}")
            return val

        N = get_float('N', 0, 500)
        P = get_float('P', 0, 500)
        K = get_float('K', 0, 500)
        temperature = get_float('temperature', -10, 60)
        humidity = get_float('humidity', 0, 100)
        ph = get_float('ph', 0, 14)
        rainfall = get_float('rainfall', 0, 1000)

        # Preprocess input
        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        scaled_data = scaler.transform(data)

        # Predict
        prediction = model.predict(scaled_data)[0]
        
        # Get prediction probabilities for confidence score
        probabilities = model.predict_proba(scaled_data)[0]
        max_probability = max(probabilities)
        confidence_score = int(max_probability * 100)

        # Get crop info if available
        crop_info = CROP_INFO.get(str(prediction).lower(), {})
        
        # Prepare response data
        response_data = {
            'success': True,
            'crop': prediction,
            'confidence': confidence_score,
            'crop_info': {
                'season': crop_info.get('season', 'N/A'),
                'growing_period': crop_info.get('growing_period', 'N/A'),
                'soil_type': crop_info.get('soil_type', 'N/A'),
                'water_need': crop_info.get('water_need', 'N/A'),
                'conditions': crop_info.get('conditions', 'N/A'),
                'tips': crop_info.get('tips', 'N/A')
            }
        }

        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        return jsonify(success=False, error=error_msg)

@app.route('/debug-weather', methods=['GET'])
def debug_weather():
    """Debug endpoint to see raw OpenWeatherMap API response"""
    try:
        lat = request.args.get('lat', DEFAULT_LAT, type=float)
        lon = request.args.get('lon', DEFAULT_LON, type=float)
        
        # Make direct API call
        params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'api_response': data,
                'temperature_raw': data['main'].get('temp'),
                'temperature_unit': 'Celsius (metric)',
                'location': f"({lat}, {lon})",
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f"API returned {response.status_code}",
                'response_text': response.text
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/realtime-data', methods=['GET'])
def get_realtime_data():
    """Fetch real-time weather data and generate realistic soil data"""
    try:
        # Get location from query parameters or use default
        lat = request.args.get('lat', DEFAULT_LAT, type=float)
        lon = request.args.get('lon', DEFAULT_LON, type=float)
        
        # Fetch real-time weather data
        weather_data = fetch_weather_data(lat, lon)
        
        if not weather_data:
            return jsonify(success=False, error="Unable to fetch weather data")
        
        # Generate realistic soil data based on location and weather
        soil_data = generate_realistic_soil_data(lat, lon, weather_data)
        
        # Combine weather and soil data
        realtime_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'location': {
                'lat': lat,
                'lon': lon,
                'city': weather_data.get('city', 'Unknown Location')
            },
            'weather': {
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'rainfall': weather_data['rainfall'],
                'description': weather_data['description'],
                'icon': weather_data['icon']
            },
            'soil': soil_data,
            'data_source': 'OpenWeatherMap API + Soil Simulation'
        }
        
        return jsonify(realtime_data)
        
    except Exception as e:
        return jsonify(success=False, error=str(e))

def fetch_weather_data(lat, lon):
    """Fetch real-time weather data from OpenWeatherMap API"""
    try:
        # If no API key, return simulated data
        if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
            return get_simulated_weather_data(lat, lon)
        
        # Make API call to OpenWeatherMap
        params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Ensure we get Celsius
        }
        
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug: Print raw API response
            print(f"OpenWeatherMap API Response for ({lat}, {lon}):")
            print(f"Raw temperature: {data['main'].get('temp')}")
            print(f"Units: {data.get('units', 'metric')}")
            
            # Extract relevant weather data
            weather_data = {
                'temperature': data['main']['temp'],  # Should be in Celsius with units=metric
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0),  # Rain in last hour
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'city': data.get('name', 'Unknown'),
                'timestamp': data['dt']
            }
            
            # Ensure temperature is in Celsius
            if weather_data['temperature'] < 100:  # Likely Celsius
                print(f"Temperature confirmed as Celsius: {weather_data['temperature']}°C")
            else:
                print(f"Temperature appears to be in Kelvin: {weather_data['temperature']}K")
                # Convert Kelvin to Celsius if needed
                weather_data['temperature'] = weather_data['temperature'] - 273.15
                print(f"Converted to Celsius: {weather_data['temperature']}°C")
            
            return weather_data
        else:
            print(f"OpenWeatherMap API error: {response.status_code}")
            print(f"Response: {response.text}")
            # Fallback to simulated data if API fails
            return get_simulated_weather_data(lat, lon)
            
    except Exception as e:
        print(f"Weather API error: {e}")
        # Fallback to simulated data
        return get_simulated_weather_data(lat, lon)

def get_simulated_weather_data(lat, lon):
    """Generate realistic simulated weather data based on location and time"""
    import random
    
    # Seed random with location and time for consistency
    random.seed(int(lat * 1000) + int(lon * 1000) + int(time.time() / 3600))
    
    # Get current time for more realistic simulation
    current_hour = datetime.now().hour
    current_month = datetime.now().month
    
    # Special handling for Hyderabad area (17.37°N, 78.53°E)
    if 17.0 <= lat <= 18.0 and 78.0 <= lon <= 79.0:
        # Hyderabad-specific weather patterns
        if current_month in [6, 7, 8, 9]:  # Monsoon season
            base_temp = 28
            humidity_range = (70, 90)
            rainfall_chance = 0.8
        elif current_month in [3, 4, 5]:  # Summer
            base_temp = 32
            humidity_range = (40, 60)
            rainfall_chance = 0.1
        else:  # Winter
            base_temp = 24
            humidity_range = (50, 70)
            rainfall_chance = 0.05
        
        # Time of day adjustments for Hyderabad
        if 6 <= current_hour <= 18:  # Daytime
            temp_variation = random.uniform(-2, 3)
        else:  # Nighttime
            temp_variation = random.uniform(-3, 1)
            base_temp -= 2
        
        temperature = round(base_temp + temp_variation, 1)
        humidity = random.randint(*humidity_range)
        
        # Rainfall based on season and humidity
        if humidity > 80 and random.random() < rainfall_chance:
            rainfall = round(random.uniform(5, 30), 1)
        else:
            rainfall = 0
            
    else:
        # General simulation for other locations
        # Simulate weather based on location (latitude affects temperature)
        base_temp = 25 - (abs(lat - 20) * 0.5)  # Cooler away from equator
        
        # Add seasonal variation (month affects temperature)
        if current_month in [12, 1, 2]:  # Winter months
            base_temp -= 5
        elif current_month in [6, 7, 8]:  # Summer months
            base_temp += 5
        
        # Add time-of-day variation (hour affects temperature)
        if 6 <= current_hour <= 18:  # Daytime
            temp_variation = random.uniform(-2, 3)
        else:  # Nighttime
            temp_variation = random.uniform(-5, 2)
            base_temp -= 3  # Cooler at night
        
        temperature = round(base_temp + temp_variation, 1)
        
        # Ensure temperature is realistic for the location
        if lat < 25:  # Southern India
            temperature = max(18, min(35, temperature))  # 18-35°C range
        else:  # Northern India
            temperature = max(10, min(40, temperature))  # 10-40°C range
        
        # Humidity varies with temperature and location
        if temperature > 30:
            humidity = random.randint(40, 70)  # Lower humidity in hot weather
        elif temperature < 20:
            humidity = random.randint(50, 80)  # Moderate humidity in cool weather
        else:
            humidity = random.randint(60, 90)  # Higher humidity in moderate weather
        
        # Rainfall simulation (more likely in certain conditions)
        rainfall_chance = random.random()
        if humidity > 80 and rainfall_chance > 0.6:
            rainfall = round(random.uniform(5, 25), 1)
        elif humidity > 70 and rainfall_chance > 0.8:
            rainfall = round(random.uniform(1, 10), 1)
        else:
            rainfall = 0
    
    # Weather descriptions based on conditions
    if rainfall > 0:
        if rainfall > 15:
            description = "Moderate rain"
        else:
            description = "Light rain"
    elif humidity > 85:
        description = "Humid"
    elif humidity < 50:
        description = "Dry"
    else:
        descriptions = ['Clear sky', 'Partly cloudy', 'Cloudy']
        description = random.choice(descriptions)
    
    print(f"Simulated weather for ({lat}, {lon}): {temperature}°C, {humidity}% humidity, {rainfall}mm rain")
    
    return {
        'temperature': temperature,
        'humidity': humidity,
        'rainfall': rainfall,
        'description': description,
        'icon': '01d',  # Default icon
        'city': f"Location ({lat:.2f}, {lon:.2f})",
        'timestamp': int(time.time())
    }

def generate_realistic_soil_data(lat, lon, weather_data):
    """Generate realistic soil data based on location and weather"""
    import random
    
    # Seed random for consistency
    random.seed(int(lat * 1000) + int(lon * 1000) + int(time.time() / 3600))
    
    # Special handling for Hyderabad area (17.37°N, 78.53°E)
    if 17.0 <= lat <= 18.0 and 78.0 <= lon <= 79.0:
        # Hyderabad-specific soil characteristics
        # Red soil region with moderate fertility
        N_base = random.uniform(65, 85)  # Moderate to good N levels
        P_base = random.uniform(45, 65)  # Moderate P levels
        K_base = random.uniform(80, 110)  # Good K levels
        ph_base = random.uniform(6.2, 7.0)  # Slightly acidic to neutral
        
        # Weather affects soil conditions
        if weather_data['rainfall'] > 0:
            # Rain can leach nutrients slightly
            N_base *= 0.97
            P_base *= 0.98
            K_base *= 0.99
        
        # Seasonal variations for Hyderabad
        current_month = datetime.now().month
        if current_month in [6, 7, 8, 9]:  # Monsoon season
            # Higher moisture can affect nutrient availability
            ph_base *= 0.98  # Slightly more acidic during monsoon
        elif current_month in [3, 4, 5]:  # Summer
            # Dry conditions can concentrate nutrients
            N_base *= 1.02
            P_base *= 1.01
        
    else:
        # General soil characteristics for other locations
        # Soil characteristics vary by location
        # Northern India (higher latitude) - different soil composition
        if lat > 25:
            # Northern regions - typically higher N, moderate P, high K
            N_base = random.uniform(80, 180)
            P_base = random.uniform(30, 80)
            K_base = random.uniform(60, 140)
        else:
            # Southern regions - moderate N, higher P, moderate K
            N_base = random.uniform(40, 120)
            P_base = random.uniform(50, 100)
            K_base = random.uniform(40, 100)
        
        # Weather affects soil conditions
        if weather_data['rainfall'] > 0:
            # Rain can leach nutrients slightly
            N_base *= 0.95
            P_base *= 0.98
            K_base *= 0.97
        
        # pH varies by region but stays in agricultural range
        if lat > 25:
            ph_base = random.uniform(6.0, 7.5)  # Northern soils tend to be neutral
        else:
            ph_base = random.uniform(5.5, 7.0)  # Southern soils can be slightly acidic
    
    return {
        'N': round(N_base, 1),
        'P': round(P_base, 1),
        'K': round(K_base, 1),
        'ph': round(ph_base, 1)
    }

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

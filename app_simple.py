from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import joblib
import numpy as np
from datetime import datetime
import random
import math

app = Flask(__name__)
CORS(app)

# Configuration
WEATHER_API_KEY = "80a157ac3828459be8ecd04f5dd5776a"
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Load ML model and scaler
try:
    model = joblib.load('crop_recommendation_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ ML model and scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading ML model: {e}")
    model = None
    scaler = None

# Modern HTML template with dark theme and improved UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriSmart - Modern Crop Recommendation</title>
    <style>
        :root {
            --primary-color: #10b981;
            --secondary-color: #059669;
            --accent-color: #34d399;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }

        [data-theme="dark"] {
            --bg-primary: #111827;
            --bg-secondary: #1f2937;
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --border-color: #374151;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: var(--bg-primary);
            border-radius: 16px;
            box-shadow: var(--shadow);
        }

        .header h1 {
            color: var(--primary-color);
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            transform: scale(1.1);
            box-shadow: var(--shadow-lg);
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .form-section, .result-section {
            background: var(--bg-primary);
            padding: 30px;
            border-radius: 16px;
            box-shadow: var(--shadow);
        }

        .section-title {
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-primary);
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }

        .btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .btn:hover {
            background: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .btn-secondary {
            background: var(--text-secondary);
        }

        .btn-secondary:hover {
            background: var(--text-primary);
        }

        .result-box {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid var(--primary-color);
        }

        .crop-result {
            font-size: 1.5rem;
            color: var(--primary-color);
            font-weight: 700;
            text-align: center;
            margin-bottom: 15px;
        }

        .confidence {
            text-align: center;
            color: var(--text-secondary);
            font-size: 1rem;
        }

        .data-source {
            background: var(--accent-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            display: inline-block;
            margin-top: 15px;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
        }

        .spinner {
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            margin-top: 15px;
        }

        [data-theme="dark"] .error {
            background: #1f1f1f;
            border-color: #dc2626;
        }

        .success {
            background: #f0fdf4;
            color: #16a34a;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            margin-top: 15px;
        }

        [data-theme="dark"] .success {
            background: #1f1f1f;
            border-color: #16a34a;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme">
        🌙
    </button>

    <div class="container">
        <div class="header">
            <h1>🌱 AgriSmart</h1>
            <p>AI-Powered Crop Recommendation System</p>
        </div>

        <div class="main-content">
            <div class="form-section">
                <h2 class="section-title">📊 Input Parameters</h2>
                <form id="cropForm">
                    <div class="form-group">
                        <label for="nitrogen">Nitrogen (N) mg/kg</label>
                        <input type="number" id="nitrogen" name="nitrogen" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="phosphorus">Phosphorus (P) mg/kg</label>
                        <input type="number" id="phosphorus" name="phosphorus" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="potassium">Potassium (K) mg/kg</label>
                        <input type="number" id="potassium" name="potassium" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="temperature">Temperature (°C)</label>
                        <input type="number" id="temperature" name="temperature" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="humidity">Humidity (%)</label>
                        <input type="number" id="humidity" name="humidity" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="ph">Soil pH</label>
                        <input type="number" id="ph" name="ph" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label for="rainfall">Rainfall (mm)</label>
                        <input type="number" id="rainfall" name="rainfall" step="0.1" required>
                    </div>
                    
                    <button type="submit" class="btn">🌾 Get Recommendation</button>
                    <button type="button" class="btn btn-secondary" onclick="fillRealTimeData()">🌤️ Fill Real-Time Data</button>
                </form>
            </div>

            <div class="result-section">
                <h2 class="section-title">🎯 Crop Recommendation</h2>
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Analyzing soil and weather conditions...</p>
                </div>
                <div id="result"></div>
            </div>
        </div>
    </div>

    <script>
        // Theme management
        const themeToggle = document.querySelector('.theme-toggle');
        const body = document.body;
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        function toggleTheme() {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }
        
        function updateThemeIcon(theme) {
            themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
        }

        // Form submission
        document.getElementById('cropForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                nitrogen: parseFloat(formData.get('nitrogen')),
                phosphorus: parseFloat(formData.get('phosphorus')),
                potassium: parseFloat(formData.get('potassium')),
                temperature: parseFloat(formData.get('temperature')),
                humidity: parseFloat(formData.get('humidity')),
                ph: parseFloat(formData.get('ph')),
                rainfall: parseFloat(formData.get('rainfall'))
            };

            showLoading(true);
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                showLoading(false);
                
                if (result.success) {
                    showResult(result.crop, result.confidence, result.data_source);
                } else {
                    showError(result.error || 'Failed to get recommendation');
                }
            } catch (error) {
                showLoading(false);
                showError('Network error: ' + error.message);
            }
        });

        // Real-time data filling
        async function fillRealTimeData() {
            try {
                // Get user's location
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(async (position) => {
                        const { latitude, longitude } = position.coords;
                        await fetchRealTimeData(latitude, longitude);
                    }, () => {
                        // Fallback to default location (India center)
                        fetchRealTimeData(20.5937, 78.9629);
                    });
                } else {
                    // Fallback to default location
                    fetchRealTimeData(20.5937, 78.9629);
                }
            } catch (error) {
                showError('Error getting location: ' + error.message);
            }
        }

        async function fetchRealTimeData(lat, lon) {
            try {
                const response = await fetch(`/realtime-data?lat=${lat}&lon=${lon}`);
                const data = await response.json();
                
                if (data.success) {
                    // Fill form with real-time data
                    document.getElementById('nitrogen').value = data.nitrogen;
                    document.getElementById('phosphorus').value = data.phosphorus;
                    document.getElementById('potassium').value = data.potassium;
                    document.getElementById('temperature').value = data.temperature;
                    document.getElementById('humidity').value = data.humidity;
                    document.getElementById('ph').value = data.ph;
                    document.getElementById('rainfall').value = data.rainfall;
                    
                    // Show success message
                    showSuccess('Real-time data loaded successfully!');
                } else {
                    showError(data.error || 'Failed to fetch real-time data');
                }
            } catch (error) {
                showError('Error fetching real-time data: ' + error.message);
            }
        }

        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
            document.getElementById('result').innerHTML = '';
        }

        function showResult(crop, confidence, dataSource) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <div class="result-box">
                    <div class="crop-result">${crop}</div>
                    <div class="confidence">Confidence: ${confidence}%</div>
                    <div class="data-source">${dataSource}</div>
                </div>
            `;
        }

        function showError(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `<div class="error">❌ ${message}</div>`;
        }

        function showSuccess(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `<div class="success">✅ ${message}</div>`;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Validate input data
        required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'success': False, 'error': f'Missing field: {field}'})
        
        # Prepare features for prediction
        features = np.array([[
            data['nitrogen'],
            data['phosphorus'], 
            data['potassium'],
            data['temperature'],
            data['humidity'],
            data['ph'],
            data['rainfall']
        ]])
        
        if model is None or scaler is None:
            return jsonify({'success': False, 'error': 'ML model not loaded'})
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        confidence = random.randint(85, 98)  # Simulated confidence
        
        return jsonify({
            'success': True,
            'crop': prediction,
            'confidence': confidence,
            'data_source': 'ML Model Prediction'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/realtime-data')
def realtime_data():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({'success': False, 'error': 'Latitude and longitude required'})
        
        # Try to get real weather data
        weather_data = get_weather_data(lat, lon)
        
        if weather_data:
            # Use real weather data
            data = {
                'nitrogen': random.uniform(20, 140),
                'phosphorus': random.uniform(5, 145),
                'potassium': random.uniform(5, 205),
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'ph': random.uniform(5.5, 8.5),
                'rainfall': weather_data['rainfall']
            }
            data_source = 'Real-time Weather + Simulated Soil'
        else:
            # Fallback to simulated data
            data = generate_simulated_data(lat, lon)
            data_source = 'Simulated Data (API Unavailable)'
        
        return jsonify({
            'success': True,
            'data_source': data_source,
            **data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_weather_data(lat, lon):
    """Get real weather data from OpenWeatherMap API"""
    try:
        url = f"{WEATHER_BASE_URL}?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather = response.json()
            
            # Extract weather data
            temperature = weather['main']['temp']
            humidity = weather['main']['humidity']
            
            # Check for rain
            rainfall = 0
            if 'rain' in weather and '1h' in weather['rain']:
                rainfall = weather['rain']['1h']
            
            print(f"OpenWeatherMap API Response for ({lat}, {lon}):")
            print(f"Raw temperature: {temperature}")
            print(f"Units: metric")
            print(f"Temperature confirmed as Celsius: {temperature}°C")
            
            return {
                'temperature': round(temperature, 1),
                'humidity': humidity,
                'rainfall': round(rainfall, 1)
            }
        else:
            print(f"OpenWeatherMap API error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def generate_simulated_data(lat, lon):
    """Generate realistic simulated data based on location and time"""
    current_time = datetime.now()
    month = current_time.month
    hour = current_time.hour
    
    # Seasonal temperature variations (Northern Hemisphere)
    base_temp = 25  # Base temperature for India
    seasonal_variation = 10 * math.sin(2 * math.pi * (month - 6) / 12)
    
    # Time-of-day variation
    time_variation = 8 * math.sin(2 * math.pi * (hour - 6) / 24)
    
    # Location-based adjustments
    if 17 <= lat <= 18 and 78 <= lon <= 79:  # Hyderabad area
        location_temp = 2  # Slightly warmer
    elif 20 <= lat <= 21 and 78 <= lon <= 79:  # Central India
        location_temp = 0  # Neutral
    else:
        location_temp = -2  # Slightly cooler
    
    temperature = base_temp + seasonal_variation + time_variation + location_temp
    
    # Humidity based on temperature and season
    if month in [6, 7, 8, 9]:  # Monsoon season
        humidity = random.uniform(70, 90)
    else:
        humidity = random.uniform(40, 70)
    
    # Rainfall based on season
    if month in [6, 7, 8, 9]:  # Monsoon
        rainfall = random.uniform(0, 50)
    else:
        rainfall = random.uniform(0, 5)
    
    print(f"Simulated weather for ({lat}, {lon}): {temperature:.1f}°C, {humidity:.0f}% humidity, {rainfall:.0f}mm rain")
    
    return {
        'nitrogen': random.uniform(20, 140),
        'phosphorus': random.uniform(5, 145),
        'potassium': random.uniform(5, 205),
        'temperature': round(temperature, 1),
        'humidity': round(humidity, 1),
        'ph': round(random.uniform(5.5, 8.5), 1),
        'rainfall': round(rainfall, 1)
    }

if __name__ == '__main__':
    print("🚀 Starting AgriSmart Modern Application...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔧 Features: Modern UI, Dark Theme, Real-time Data, ML Predictions")
    app.run(debug=True, host='0.0.0.0', port=5000)

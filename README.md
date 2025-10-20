# AgriSmart - Crop Recommendation System

A machine learning-powered web application that recommends the best crops based on soil and climate conditions, with **real-time weather data integration**.

## Features

- **AI-Powered Predictions**: Uses a Random Forest model trained on 2200+ data points
- **7 Key Parameters**: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, and Rainfall
- **🌡️ Real-Time Weather Data**: Live weather data from OpenWeatherMap API
- **📍 Location-Based Analysis**: GPS location support and location input
- **🌱 Smart Soil Simulation**: Location-based soil characteristics
- **Detailed Crop Information**: Season, growing period, soil type, water needs, and care tips
- **Confidence Scoring**: Shows prediction confidence percentage
- **Mobile-Friendly UI**: Beautiful, responsive design that works on all devices
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **Real-time Analysis**: Instant predictions with live data integration

## How It Works

1. **Set Location**: Enter coordinates or use GPS location
2. **Fetch Real-Time Data**: Get live weather and simulated soil data
3. **AI Analysis**: The machine learning model analyzes the conditions
4. **Crop Recommendation**: Get the best crop recommendation with detailed information
5. **Confidence Score**: See how confident the model is in its prediction

## Installation & Setup

### Prerequisites
- Python 3.7+
- Required packages: Flask, scikit-learn, pandas, numpy, joblib, requests

### Quick Start
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up real-time weather data** (Optional but recommended):
   - Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
   - Copy `config.py` to `config_local.py`
   - Add your API key: `WEATHER_API_KEY = "your_actual_api_key_here"`

3. **Generate the ML model**:
   ```bash
   python create_model.py
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to: `http://localhost:5000`

## Real-Time Data Features

### 🌡️ Weather Data Sources
- **OpenWeatherMap API**: Live temperature, humidity, and rainfall data
- **Fallback Simulation**: Smart simulated data when API is unavailable
- **Location-Based**: Weather varies by geographic coordinates

### 🌱 Soil Data Intelligence
- **Location-Based Simulation**: Soil characteristics vary by region
- **Weather Integration**: Rainfall affects soil nutrient levels
- **Realistic Ranges**: Based on actual agricultural soil data

### 📍 Location Services
- **GPS Integration**: Use your device's location automatically
- **Manual Input**: Enter specific coordinates for any location
- **Global Coverage**: Works anywhere in the world

## API Endpoints

- `GET /`: Serves the main UI
- `POST /predict`: Accepts form data and returns crop prediction
- `GET /realtime-data`: Fetches real-time weather and soil data

### Real-Time Data Response
```json
{
  "success": true,
  "timestamp": "2025-08-30T19:30:00",
  "location": {
    "lat": 20.5937,
    "lon": 78.9629,
    "city": "Mumbai, India"
  },
  "weather": {
    "temperature": 28.5,
    "humidity": 75,
    "rainfall": 0,
    "description": "Partly cloudy"
  },
  "soil": {
    "N": 95.2,
    "P": 67.8,
    "K": 89.1,
    "ph": 6.8
  },
  "data_source": "OpenWeatherMap API + Soil Simulation"
}
```

## Model Details

- **Algorithm**: Random Forest Classifier
- **Training Data**: 2200+ crop recommendations with soil and climate parameters
- **Features**: 7 numerical parameters (N, P, K, temperature, humidity, pH, rainfall)
- **Accuracy**: High accuracy with cross-validation
- **Scalability**: Fast predictions suitable for real-time use

## Supported Crops

The system supports 22+ crop types including:
- **Grains**: Rice, Maize, Wheat
- **Pulses**: Chickpea, Kidney beans, Lentil
- **Fruits**: Mango, Banana, Apple, Orange
- **Commercial**: Cotton, Coffee, Jute
- **Vegetables**: Watermelon, Muskmelon

## File Structure

```
Agrismart/
├── app.py                    # Flask web application with real-time API
├── config.py                 # Configuration template for API keys
├── create_model.py          # Script to train and save ML model
├── model.py                 # Alternative model training script
├── Crop_recommendation.csv  # Training dataset
├── crop_recommendation_model.pkl  # Trained ML model
├── scaler.pkl              # Feature scaler
├── agrismart_ui.html       # Frontend UI with real-time features
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Usage Examples

### Real-Time Data
1. **Set Location**: Use GPS or enter coordinates
2. **Click "🌡️ Real-Time Data"**: Fetches live weather and soil data
3. **Get Recommendations**: Use real-world data for accurate predictions

### Sample Data
Click "📋 Fill Sample Data" for static test values:
- N: 90 mg/kg, P: 42 mg/kg, K: 43 mg/kg
- Temperature: 20.8°C, Humidity: 82%, pH: 6.5, Rainfall: 202.5 mm

## Technical Features

- **Real-Time APIs**: OpenWeatherMap integration for live weather data
- **Location Services**: GPS and manual coordinate input
- **Smart Fallbacks**: Simulated data when APIs are unavailable
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Theme Support**: Light and dark themes with smooth transitions
- **Error Handling**: Graceful fallbacks and user-friendly messages

## API Setup Instructions

### OpenWeatherMap API
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy `config.py` to `config_local.py`
5. Replace `YOUR_OPENWEATHERMAP_API_KEY_HERE` with your actual key

### Benefits of Real-Time Data
- **Accurate Predictions**: Current weather conditions
- **Location Relevance**: Site-specific recommendations
- **Seasonal Accuracy**: Real-time seasonal variations
- **Professional Use**: Suitable for agricultural planning

## Contributing

Feel free to contribute by:
- Improving the ML model
- Adding more weather data sources
- Enhancing soil simulation algorithms
- Adding new features

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please check the code or create an issue in the repository.
"# AgriSmart" 


import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Load the dataset
data = pd.read_csv('indian_agriculture.csv')

# Preprocessing steps: handle missing values, encode, and normalize
data.fillna(data.mean(), inplace=True)
data['Soil_Type'] = data['Soil_Type'].fillna(data['Soil_Type'].mode()[0])
data['Season'] = data['Season'].fillna(data['Season'].mode()[0])

le_soil = LabelEncoder()
le_season = LabelEncoder()

data['Soil_Type'] = le_soil.fit_transform(data['Soil_Type'])
data['Season'] = le_season.fit_transform(data['Season'])

scaler = StandardScaler()
data[['Rainfall', 'Temperature']] = scaler.fit_transform(data[['Rainfall', 'Temperature']])

# Define features and target
X = data.drop(columns=['Crop'])
y = data['Crop']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model and encoders
joblib.dump(model, 'crop_recommendation_model.pkl')
joblib.dump(le_soil, 'soil_encoder.pkl')
joblib.dump(le_season, 'season_encoder.pkl')
joblib.dump(scaler, 'scaler.pkl')

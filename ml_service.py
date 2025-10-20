import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import os
import json
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
import pickle

class MLService:
    """Machine Learning service for crop recommendations"""
    
    def __init__(self, model_path: str = 'crop_recommendation_model.pkl', 
                 scaler_path: str = 'scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.model_version = 'v2.0'
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self.crop_labels = [
            'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
            'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
            'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
            'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
        ]
        
        self.load_model()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for ML service"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.logger.info(f"Model loaded from {self.model_path}")
            else:
                self.logger.warning(f"Model file not found at {self.model_path}")
                self.model = None
            
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                self.logger.info(f"Scaler loaded from {self.scaler_path}")
            else:
                self.logger.warning(f"Scaler file not found at {self.scaler_path}")
                self.scaler = None
                
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.scaler = None
    
    def save_model(self, model, scaler, version: str = None):
        """Save model and scaler with versioning"""
        if version:
            self.model_version = version
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"crop_model_v{self.model_version}_{timestamp}.pkl"
        scaler_filename = f"scaler_v{self.model_version}_{timestamp}.pkl"
        
        try:
            joblib.dump(model, model_filename)
            joblib.dump(scaler, scaler_filename)
            
            # Update paths
            self.model_path = model_filename
            self.scaler_path = scaler_filename
            self.model = model
            self.scaler = scaler
            
            self.logger.info(f"Model saved as {model_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            return False
    
    def preprocess_input(self, features: Dict) -> np.ndarray:
        """Preprocess input features"""
        try:
            # Extract features in correct order
            feature_vector = np.array([
                features['N'],
                features['P'],
                features['K'],
                features['temperature'],
                features['humidity'],
                features['ph'],
                features['rainfall']
            ]).reshape(1, -1)
            
            # Scale features if scaler is available
            if self.scaler:
                feature_vector = self.scaler.transform(feature_vector)
            
            return feature_vector
            
        except KeyError as e:
            self.logger.error(f"Missing feature: {e}")
            raise ValueError(f"Missing required feature: {e}")
        except Exception as e:
            self.logger.error(f"Error preprocessing input: {str(e)}")
            raise
    
    def predict(self, features: Dict) -> Dict:
        """Make crop prediction with confidence and alternatives"""
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Preprocess input
            feature_vector = self.preprocess_input(features)
            
            # Make prediction
            prediction = self.model.predict(feature_vector)[0]
            prediction_proba = self.model.predict_proba(feature_vector)[0]
            
            # Get confidence score
            confidence_score = np.max(prediction_proba)
            
            # Get top 3 alternatives
            top_indices = np.argsort(prediction_proba)[-3:][::-1]
            alternative_crops = []
            
            for idx in top_indices[1:]:  # Skip the top prediction
                alternative_crops.append({
                    'crop': self.crop_labels[idx],
                    'confidence': float(prediction_proba[idx])
                })
            
            # Get predicted crop name
            predicted_crop = self.crop_labels[prediction]
            
            result = {
                'predicted_crop': predicted_crop,
                'confidence_score': float(confidence_score),
                'alternative_crops': alternative_crops,
                'model_version': self.model_version,
                'input_features': features,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Prediction made: {predicted_crop} with confidence {confidence_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def train_model(self, data_path: str = 'Crop_recommendation.csv') -> Dict:
        """Train a new model from data"""
        try:
            # Load data
            data = pd.read_csv(data_path)
            self.logger.info(f"Loaded dataset with {len(data)} samples")
            
            # Prepare features and target
            X = data[self.feature_names].values
            y = data['label'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Create ensemble model
            rf1 = RandomForestClassifier(n_estimators=100, random_state=42)
            rf2 = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
            rf3 = RandomForestClassifier(n_estimators=200, min_samples_split=5, random_state=42)
            
            ensemble = VotingClassifier(
                estimators=[('rf1', rf1), ('rf2', rf2), ('rf3', rf3)],
                voting='soft'
            )
            
            # Train model
            start_time = datetime.now()
            ensemble.fit(X_train_scaled, y_train)
            training_duration = (datetime.now() - start_time).total_seconds()
            
            # Evaluate model
            y_pred = ensemble.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(ensemble, X_train_scaled, y_train, cv=5)
            cv_accuracy = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Detailed metrics
            report = classification_report(y_test, y_pred, output_dict=True)
            conf_matrix = confusion_matrix(y_test, y_pred)
            
            # Save model
            success = self.save_model(ensemble, scaler, f"{self.model_version}_ensemble")
            
            # Performance metrics
            performance = {
                'model_version': self.model_version,
                'model_type': 'RandomForest Ensemble',
                'accuracy': float(accuracy),
                'cv_accuracy': float(cv_accuracy),
                'cv_std': float(cv_std),
                'training_duration': float(training_duration),
                'dataset_size': len(data),
                'features_used': self.feature_names,
                'confusion_matrix': conf_matrix.tolist(),
                'classification_report': report,
                'model_saved': success,
                'training_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
            return performance
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise
    
    def evaluate_model(self, test_data: pd.DataFrame = None) -> Dict:
        """Evaluate model performance"""
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            if test_data is None:
                # Load test data
                data = pd.read_csv('Crop_recommendation.csv')
                test_data = data.sample(frac=0.2, random_state=42)
            
            X_test = test_data[self.feature_names].values
            y_test = test_data['label'].values
            
            if self.scaler:
                X_test_scaled = self.scaler.transform(X_test)
            else:
                X_test_scaled = X_test
            
            # Make predictions
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            conf_matrix = confusion_matrix(y_test, y_pred)
            
            # Calculate confidence distribution
            max_proba = np.max(y_pred_proba, axis=1)
            confidence_stats = {
                'mean': float(np.mean(max_proba)),
                'std': float(np.std(max_proba)),
                'min': float(np.min(max_proba)),
                'max': float(np.max(max_proba)),
                'quartiles': [float(q) for q in np.percentile(max_proba, [25, 50, 75])]
            }
            
            evaluation = {
                'model_version': self.model_version,
                'test_samples': len(test_data),
                'accuracy': float(accuracy),
                'classification_report': report,
                'confusion_matrix': conf_matrix.tolist(),
                'confidence_statistics': confidence_stats,
                'evaluation_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model evaluation completed. Accuracy: {accuracy:.3f}")
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        try:
            if self.model is None:
                return {'status': 'No model loaded'}
            
            model_info = {
                'status': 'Model loaded',
                'model_version': self.model_version,
                'model_type': type(self.model).__name__,
                'feature_names': self.feature_names,
                'crop_labels': self.crop_labels,
                'num_features': len(self.feature_names),
                'num_classes': len(self.crop_labels),
                'model_path': self.model_path,
                'scaler_path': self.scaler_path,
                'last_updated': datetime.fromtimestamp(
                    os.path.getmtime(self.model_path)
                ).isoformat() if os.path.exists(self.model_path) else None
            }
            
            return model_info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {str(e)}")
            return {'status': 'Error', 'error': str(e)}
    
    def batch_predict(self, features_list: List[Dict]) -> List[Dict]:
        """Make predictions for multiple inputs"""
        try:
            results = []
            for i, features in enumerate(features_list):
                try:
                    result = self.predict(features)
                    result['batch_index'] = i
                    results.append(result)
                except Exception as e:
                    results.append({
                        'batch_index': i,
                        'error': str(e),
                        'input_features': features
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch prediction: {str(e)}")
            raise
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from the model"""
        try:
            if self.model is None:
                return {'error': 'No model loaded'}
            
            if hasattr(self.model, 'feature_importances_'):
                importance = self.model.feature_importances_
            elif hasattr(self.model, 'estimators_'):
                # For ensemble models, average importance across estimators
                importance = np.mean([est.feature_importances_ for est in self.model.estimators_], axis=0)
            else:
                return {'error': 'Feature importance not available for this model type'}
            
            feature_importance = dict(zip(self.feature_names, importance.tolist()))
            
            # Sort by importance
            sorted_importance = dict(sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            return {
                'feature_importance': sorted_importance,
                'model_version': self.model_version,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting feature importance: {str(e)}")
            return {'error': str(e)}

# Global ML service instance
ml_service = MLService()

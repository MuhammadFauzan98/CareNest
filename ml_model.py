import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

class HealthRiskPredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
    def generate_sample_data(self):
        """Generate sample training data for demonstration"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.randint(60, 95, n_samples),
            'weight': np.random.randint(50, 120, n_samples),
            'systolic_bp': np.random.randint(100, 200, n_samples),
            'diastolic_bp': np.random.randint(60, 120, n_samples),
            'heart_rate': np.random.randint(50, 120, n_samples),
            'blood_sugar': np.random.uniform(70, 300, n_samples),
            'cholesterol': np.random.uniform(150, 300, n_samples),
            'sleep_hours': np.random.uniform(4, 10, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Simulate risk levels based on health parameters
        def calculate_risk(row):
            risk_score = 0
            if row['systolic_bp'] > 140 or row['diastolic_bp'] > 90:
                risk_score += 2
            if row['blood_sugar'] > 180:
                risk_score += 2
            if row['cholesterol'] > 240:
                risk_score += 1
            if row['heart_rate'] > 100 or row['heart_rate'] < 60:
                risk_score += 1
            if row['age'] > 75:
                risk_score += 1
            if row['sleep_hours'] < 6:
                risk_score += 1
                
            if risk_score >= 4:
                return 'high'
            elif risk_score >= 2:
                return 'medium'
            else:
                return 'low'
        
        df['risk_level'] = df.apply(calculate_risk, axis=1)
        return df
    
    def train_model(self):
        """Train the machine learning model"""
        try:
            # Generate sample data
            df = self.generate_sample_data()
            
            # Prepare features and target
            features = ['age', 'weight', 'systolic_bp', 'diastolic_bp', 
                       'heart_rate', 'blood_sugar', 'cholesterol', 'sleep_hours']
            X = df[features]
            y = self.label_encoder.fit_transform(df['risk_level'])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Calculate accuracy
            accuracy = self.model.score(X_test, y_test)
            print(f"Model trained with accuracy: {accuracy:.2f}")
            
            self.is_trained = True
            
            # Save model
            joblib.dump(self.model, 'health_risk_model.pkl')
            joblib.dump(self.label_encoder, 'label_encoder.pkl')
            
        except Exception as e:
            print(f"Error training model: {e}")
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists('health_risk_model.pkl'):
                self.model = joblib.load('health_risk_model.pkl')
                self.label_encoder = joblib.load('label_encoder.pkl')
                self.is_trained = True
                print("Model loaded successfully")
            else:
                print("No pre-trained model found. Training new model...")
                self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.train_model()
    
    def predict_risk(self, health_data):
        """Predict health risk based on input data"""
        if not self.is_trained:
            self.load_model()
        
        try:
            # Prepare input features
            features = np.array([[
                health_data['age'],
                health_data['weight'],
                health_data['systolic_bp'],
                health_data['diastolic_bp'],
                health_data['heart_rate'],
                health_data['blood_sugar'],
                health_data['cholesterol'],
                health_data['sleep_hours']
            ]])
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            risk_level = self.label_encoder.inverse_transform([prediction])[0]
            confidence = np.max(probability)
            
            return risk_level, confidence
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return "unknown", 0.0

# Global model instance
health_predictor = HealthRiskPredictor()

def predict_health_risk(health_data):
    """Main function to predict health risk"""
    return health_predictor.predict_risk(health_data)

def get_health_recommendations(risk_level, health_data):
    """Generate health recommendations based on risk level and health data"""
    recommendations = []
    
    # Blood pressure recommendations
    if health_data['systolic_bp'] > 140 or health_data['diastolic_bp'] > 90:
        recommendations.extend([
            "Monitor blood pressure regularly",
            "Reduce sodium intake",
            "Consider consulting a doctor for hypertension management"
        ])
    
    # Blood sugar recommendations
    if health_data['blood_sugar'] > 180:
        recommendations.extend([
            "Monitor blood sugar levels",
            "Reduce sugar and carbohydrate intake",
            "Maintain regular meal times"
        ])
    
    # Cholesterol recommendations
    if health_data['cholesterol'] > 240:
        recommendations.extend([
            "Reduce saturated fat intake",
            "Increase fiber consumption",
            "Consider heart-healthy diet"
        ])
    
    # Heart rate recommendations
    if health_data['heart_rate'] > 100:
        recommendations.append("Practice relaxation techniques to lower heart rate")
    elif health_data['heart_rate'] < 60:
        recommendations.append("Consult doctor about low heart rate")
    
    # Sleep recommendations
    if health_data['sleep_hours'] < 6:
        recommendations.extend([
            "Aim for 7-8 hours of sleep per night",
            "Maintain consistent sleep schedule",
            "Create relaxing bedtime routine"
        ])
    
    # General recommendations based on risk level
    if risk_level == 'high':
        recommendations.extend([
            "Consult healthcare provider immediately",
            "Regular monitoring of vital signs",
            "Follow prescribed medications strictly"
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            "Schedule doctor appointment soon",
            "Increase physical activity gradually",
            "Maintain healthy diet"
        ])
    else:
        recommendations.extend([
            "Continue healthy lifestyle habits",
            "Regular health check-ups",
            "Stay physically active"
        ])
    
    return recommendations

def get_predicted_conditions(risk_level, health_data):
    """Predict potential health conditions based on risk factors"""
    conditions = []
    
    if health_data['systolic_bp'] > 140 or health_data['diastolic_bp'] > 90:
        conditions.append("Hypertension")
    
    if health_data['blood_sugar'] > 180:
        conditions.append("Diabetes Risk")
    
    if health_data['cholesterol'] > 240:
        conditions.append("High Cholesterol")
    
    if health_data['heart_rate'] > 100:
        conditions.append("Tachycardia")
    elif health_data['heart_rate'] < 60:
        conditions.append("Bradycardia")
    
    if risk_level == 'high':
        conditions.append("Cardiovascular Risk")
    
    return conditions if conditions else ["No specific conditions detected"]
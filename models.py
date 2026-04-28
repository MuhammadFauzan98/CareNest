from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with health records
    health_records = db.relationship('HealthRecord', backref='user', lazy=True)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Vital signs
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    systolic_bp = db.Column(db.Integer)  # systolic blood pressure
    diastolic_bp = db.Column(db.Integer) # diastolic blood pressure
    heart_rate = db.Column(db.Integer)
    blood_sugar = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    
    # Symptoms (comma-separated string)
    symptoms = db.Column(db.Text)
    
    # Additional health info
    medication = db.Column(db.Text)
    allergies = db.Column(db.Text)
    exercise_frequency = db.Column(db.String(50))
    sleep_hours = db.Column(db.Float)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    health_record_id = db.Column(db.Integer, db.ForeignKey('health_record.id'))
    
    # Prediction results
    risk_level = db.Column(db.String(50))  # low, medium, high
    predicted_conditions = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    recommendations = db.Column(db.Text)
    
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with health record
    health_record = db.relationship('HealthRecord', backref='prediction')
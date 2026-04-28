from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, HealthRecord, Prediction
from ml_model import predict_health_risk, get_health_recommendations, get_predicted_conditions, health_predictor
import os
from datetime import datetime, timedelta
from gettext import translation as gettext_translation, NullTranslations
from functools import lru_cache

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-health-assistant-secret-key-2023'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'bn': 'বাংলা',
    'hi': 'हिन्दी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
}
DEFAULT_LANGUAGE = 'en'
TRANSLATION_DIR = os.path.join(app.root_path, 'translations')

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@lru_cache(maxsize=16)
def load_translation(language_code):
    if language_code == DEFAULT_LANGUAGE:
        return NullTranslations()

    try:
        return gettext_translation('messages', localedir=TRANSLATION_DIR, languages=[language_code])
    except Exception:
        return NullTranslations()


def get_locale():
    language_code = request.args.get('lang') or session.get('lang')
    return language_code if language_code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def translate(text):
    return load_translation(get_locale()).gettext(text)


@app.before_request
def set_request_locale():
    g.current_lang = get_locale()


@app.context_processor
def inject_i18n_helpers():
    return {
        '_': translate,
        'current_lang': getattr(g, 'current_lang', DEFAULT_LANGUAGE),
        'supported_languages': SUPPORTED_LANGUAGES,
        'js_i18n': {
            'very_weak': translate('Very Weak'),
            'weak': translate('Weak'),
            'fair': translate('Fair'),
            'good': translate('Good'),
            'strong': translate('Strong'),
            'age_validation': translate('Age must be between 60 and 120 years for elderly care monitoring.'),
            'required_fields': translate('Please fill in all required fields.'),
            'systolic_bp': translate('Systolic BP should be between 70 and 250 mmHg'),
            'diastolic_bp': translate('Diastolic BP should be between 40 and 150 mmHg'),
            'heart_rate': translate('Heart rate should be between 30 and 200 BPM'),
            'blood_sugar': translate('Blood sugar should be between 50 and 500 mg/dL'),
            'cholesterol': translate('Cholesterol should be between 100 and 400 mg/dL'),
        }
    }


@login_manager.unauthorized_handler
def handle_unauthorized():
    flash(translate('Please log in to access this page.'), 'error')
    return redirect(url_for('login', next=request.url))


@app.route('/set-language/<language_code>')
def set_language(language_code):
    if language_code in SUPPORTED_LANGUAGES:
        session['lang'] = language_code

    next_url = request.args.get('next') or request.referrer or url_for('index')
    return redirect(next_url)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and ML model
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin_user = User.query.filter_by(email='admin@health.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@health.com',
            age=35,
            gender='other',
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
    
    # Load ML model
    health_predictor.load_model()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age'])
        gender = request.form['gender']
        
        if User.query.filter_by(email=email).first():
            flash(translate('Email already registered! Please use a different email.'), 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash(translate('Username already taken! Please choose a different one.'), 'error')
            return render_template('register.html')
        
        new_user = User(
            username=username,
            email=email,
            age=age,
            gender=gender,
            is_admin=False
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(translate('Registration successful! Please login with your credentials.'), 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(translate('Welcome back, {username}!').format(username=user.username), 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(translate('Invalid email or password! Please try again.'), 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(translate('You have been logged out successfully.'), 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent health records
    recent_records = HealthRecord.query.filter_by(user_id=current_user.id)\
        .order_by(HealthRecord.recorded_at.desc())\
        .limit(5).all()
    
    # Get recent predictions
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.predicted_at.desc())\
        .limit(5).all()
    
    return render_template('dashboard.html', 
                         recent_records=recent_records,
                         recent_predictions=recent_predictions)

@app.route('/input-health', methods=['GET', 'POST'])
@login_required
def input_health():
    if request.method == 'POST':
        try:
            # Get form data
            health_data = {
                'weight': float(request.form['weight']),
                'height': float(request.form['height']),
                'systolic_bp': int(request.form['systolic_bp']),
                'diastolic_bp': int(request.form['diastolic_bp']),
                'heart_rate': int(request.form['heart_rate']),
                'blood_sugar': float(request.form['blood_sugar']),
                'cholesterol': float(request.form['cholesterol']),
                'sleep_hours': float(request.form['sleep_hours']),
                'age': current_user.age,
                'symptoms': request.form.get('symptoms', ''),
                'medication': request.form.get('medication', ''),
                'allergies': request.form.get('allergies', ''),
                'exercise_frequency': request.form.get('exercise_frequency', '')
            }
            
            # Create health record
            health_record = HealthRecord(
                user_id=current_user.id,
                weight=health_data['weight'],
                height=health_data['height'],
                systolic_bp=health_data['systolic_bp'],
                diastolic_bp=health_data['diastolic_bp'],
                heart_rate=health_data['heart_rate'],
                blood_sugar=health_data['blood_sugar'],
                cholesterol=health_data['cholesterol'],
                sleep_hours=health_data['sleep_hours'],
                symptoms=health_data['symptoms'],
                medication=health_data['medication'],
                allergies=health_data['allergies'],
                exercise_frequency=health_data['exercise_frequency']
            )
            
            db.session.add(health_record)
            db.session.flush()  # Get the ID before commit
            
            # Predict health risk
            risk_level, confidence = predict_health_risk(health_data)
            recommendations = get_health_recommendations(risk_level, health_data)
            predicted_conditions = get_predicted_conditions(risk_level, health_data)
            
            # Create prediction record
            prediction = Prediction(
                user_id=current_user.id,
                health_record_id=health_record.id,
                risk_level=risk_level,
                predicted_conditions=', '.join(predicted_conditions),
                confidence_score=confidence,
                recommendations='; '.join(recommendations)
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            session['last_prediction'] = {
                'risk_level': risk_level,
                'confidence': confidence,
                'recommendations': recommendations,
                'predicted_conditions': predicted_conditions,
                'health_data': health_data
            }
            
            flash(translate('Health data submitted successfully! Analysis completed.'), 'success')
            return redirect(url_for('analysis'))
            
        except Exception as e:
            db.session.rollback()
            flash(translate('Error processing health data: {error}').format(error=str(e)), 'error')
            return render_template('input_form.html')
    
    return render_template('input_form.html')

from datetime import datetime

@app.route('/analysis')
@login_required
def analysis():
    prediction_data = session.get('last_prediction')
    if not prediction_data:
        flash(translate('No recent analysis found. Please submit health data first.'), 'warning')
        return redirect(url_for('dashboard'))   # or wherever you want to redirect

    # ✅ Pass 'now' to the template
    return render_template(
        'analysis.html',
        now=datetime.now(),
        **prediction_data
    )

@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    health_records = HealthRecord.query.filter_by(user_id=current_user.id)\
        .order_by(HealthRecord.recorded_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    low_risk_count = Prediction.query.filter_by(user_id=current_user.id, risk_level='low').count()
    medium_risk_count = Prediction.query.filter_by(user_id=current_user.id, risk_level='medium').count()
    high_risk_count = Prediction.query.filter_by(user_id=current_user.id, risk_level='high').count()
    
    return render_template(
        'history.html',
        health_records=health_records,
        low_risk_count=low_risk_count,
        medium_risk_count=medium_risk_count,
        high_risk_count=high_risk_count
    )

@app.route('/api/health-trends')
@login_required
def health_trends():
    # Get health records from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.recorded_at >= thirty_days_ago
    ).order_by(HealthRecord.recorded_at).all()
    
    data = {
        'dates': [r.recorded_at.strftime('%Y-%m-%d') for r in records],
        'systolic_bp': [r.systolic_bp for r in records],
        'diastolic_bp': [r.diastolic_bp for r in records],
        'heart_rate': [r.heart_rate for r in records],
        'blood_sugar': [r.blood_sugar for r in records]
    }
    
    return jsonify(data)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash(translate('Access denied. Admin privileges required.'), 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    total_records = HealthRecord.query.count()
    total_predictions = Prediction.query.count()
    
    return render_template('admin.html', 
                         users=users, 
                         total_records=total_records,
                         total_predictions=total_predictions)

@app.route('/admin/user/<int:user_id>')
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        flash(translate('Access denied.'), 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    health_records = HealthRecord.query.filter_by(user_id=user_id)\
        .order_by(HealthRecord.recorded_at.desc())\
        .limit(10).all()
    
    return render_template('admin_user_detail.html', user=user, health_records=health_records)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
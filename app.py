from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objects as go
import json
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Import configuration
try:
    from config import *
except ImportError:
    # Fallback configuration if config.py doesn't exist
    BETA_CODE = "moodtracker2024"
    SECRET_KEY = 'your-secret-key-here'
    DATABASE_URI = 'sqlite:///mood_tracker.db'
    MIN_PASSWORD_LENGTH = 6

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/mood_tracker.log', 
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Setup error file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger('mood_tracker')
    app_logger.setLevel(logging.INFO)
    
    return app_logger

# Setup logging
logger = setup_logging()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)

# Log application startup
logger.info("Mood Tracker application starting up...")
logger.info(f"Database URI: {DATABASE_URI}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Notification settings file
NOTIFICATION_SETTINGS_FILE = 'notification_settings.json'

def load_notification_settings():
    """Load notification settings from JSON file."""
    try:
        with open('notification_settings.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {
            'enabled': True,
            'time': '15:00',
            'timezone': 'US/Eastern',
            'duration': 10,
            'gender': 'female'  # Default to female to show menstruation option
        }
    return settings

def save_notification_settings(settings):
    """Save notification settings to JSON file."""
    with open('notification_settings.json', 'w') as f:
        json.dump(settings, f, indent=2)

class NotificationSettings:
    def __init__(self):
        self.settings = load_notification_settings()
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def save(self):
        save_notification_settings(self.settings)

# Global notification settings instance
notification_settings = NotificationSettings()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to mood entries
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)  # For soft delete
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='medications')
    
class MoodEntryMedication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood_entry_id = db.Column(db.Integer, db.ForeignKey('mood_entry.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken = db.Column(db.Boolean, default=False)
    
    medication = db.relationship('Medication')

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)
    hours_slept = db.Column(db.Float, nullable=False)
    anxiety = db.Column(db.Integer, nullable=False)
    energy_level = db.Column(db.Integer, nullable=False)
    irritability = db.Column(db.Integer, nullable=False)
    alcohol_drugs = db.Column(db.Boolean, default=False)
    exercise = db.Column(db.Boolean, default=False)
    menstruation = db.Column(db.Boolean, default=False)
    stressful_event = db.Column(db.Boolean, default=False)
    weight = db.Column(db.Float)  # Optional weight field
    notes = db.Column(db.Text)
    medications = db.relationship('MoodEntryMedication', backref='mood_entry', cascade='all, delete-orphan')
    
    # Add unique constraint for user_id and entry_date combination
    __table_args__ = (db.UniqueConstraint('user_id', 'entry_date', name='_user_date_uc'),)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        beta_code = request.form['beta_code']
        
        logger.info(f"Registration attempt for username: {username}, email: {email}")
        
        # Validation
        if not username or not email or not password:
            logger.warning(f"Registration failed - missing required fields for username: {username}")
            flash('All fields are required.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        if password != confirm_password:
            logger.warning(f"Registration failed - password mismatch for username: {username}")
            flash('Passwords do not match.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        if len(password) < MIN_PASSWORD_LENGTH:
            logger.warning(f"Registration failed - password too short for username: {username}")
            flash(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration failed - username already exists: {username}")
            flash('Username already exists.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed - email already registered: {email}")
            flash('Email already registered.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        # Check beta code
        if beta_code != BETA_CODE:
            logger.warning(f"Registration failed - invalid beta code for username: {username}, provided code: {beta_code}")
            flash('Invalid beta code.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
        
        # Create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"User registration successful - username: {username}, email: {email}, user_id: {user.id}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Registration failed - database error for username: {username}, error: {str(e)}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)
    
    logger.info("Registration page accessed")
    return render_template('register.html', min_password_length=MIN_PASSWORD_LENGTH)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.info(f"User already logged in, redirecting: {current_user.username}")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logger.info(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"Login successful - username: {username}, user_id: {user.id}")
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            logger.warning(f"Login failed - invalid credentials for username: {username}")
            flash('Invalid username or password.', 'error')
    
    logger.info("Login page accessed")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    user_id = current_user.id
    logout_user()
    logger.info(f"User logged out - username: {username}, user_id: {user_id}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main page with mood entry form."""
    logger.info(f"Index page accessed by user: {current_user.username}")
    today_date = datetime.now().strftime('%Y-%m-%d')
    medications = Medication.query.filter_by(active=True, user_id=current_user.id).all()
    settings = NotificationSettings()
    gender = settings.get('gender', 'female')
    
    # Check if weight input is needed (every 7 days)
    today = datetime.now().date()
    last_weight_entry = MoodEntry.query.filter(
        MoodEntry.weight.isnot(None),
        MoodEntry.user_id == current_user.id
    ).order_by(MoodEntry.entry_date.desc()).first()
    
    weight_needed = False
    if not last_weight_entry:
        weight_needed = True
    else:
        days_since_last_weight = (today - last_weight_entry.entry_date).days
        weight_needed = days_since_last_weight >= 7
    
    return render_template('index.html', 
                         today_date=today_date, 
                         medications=medications,
                         gender=gender,
                         weight_needed=weight_needed)

@app.route('/submit', methods=['POST'])
@login_required
def submit_entry():
    logger.info(f"Mood entry submission attempt by user: {current_user.username}")
    data = request.form
    entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Check if entry is for a future date
    if entry_date > today:
        logger.warning(f"Future date entry attempt by user: {current_user.username}, date: {entry_date}")
        flash('Cannot create entries for future dates. Please select today\'s date or a past date.', 'warning')
        return redirect(url_for('index'))
    
    # Check if entry already exists for this date for this user
    existing_entry = MoodEntry.query.filter_by(entry_date=entry_date, user_id=current_user.id).first()
    if existing_entry:
        logger.warning(f"Duplicate entry attempt by user: {current_user.username}, date: {entry_date}")
        flash('An entry already exists for this date. Please edit the existing entry instead.', 'warning')
        return redirect(url_for('manage_entries'))
    
    try:
        new_entry = MoodEntry(
            user_id=current_user.id,
            entry_date=entry_date,
            mood_level=int(data['mood']),
            hours_slept=float(data['hours_slept']),
            anxiety=int(data['anxiety']),
            energy_level=int(data['energy']),
            irritability=int(data['irritability']),
            alcohol_drugs=data.get('alcohol_drugs') == 'on',
            exercise=data.get('exercise') == 'on',
            menstruation=data.get('menstruation') == 'on',
            stressful_event=data.get('stressful_event') == 'on',
            weight=float(data['weight']) if data.get('weight') else None,
            notes=data.get('notes', '')
        )
        db.session.add(new_entry)
        db.session.flush()  # Get new_entry.id before commit

        # Save medications taken
        taken_ids = data.getlist('medications_taken')
        for med in Medication.query.filter(Medication.id.in_(taken_ids), Medication.user_id == current_user.id).all():
            mem = MoodEntryMedication(mood_entry_id=new_entry.id, medication_id=med.id, taken=True)
            db.session.add(mem)
        
        db.session.commit()
        logger.info(f"Mood entry created successfully - user: {current_user.username}, entry_id: {new_entry.id}, date: {entry_date}")
        flash('Entry added successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Mood entry creation failed - user: {current_user.username}, error: {str(e)}")
        db.session.rollback()
        flash('Failed to create entry. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/manage')
@login_required
def manage_entries():
    """Manage existing entries."""
    logger.info(f"Manage entries page accessed by user: {current_user.username}")
    entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.entry_date.desc()).all()
    medications = Medication.query.filter_by(active=True, user_id=current_user.id).order_by(Medication.name).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    edit_medication_id = request.args.get('edit_medication_id', type=int)
    settings = NotificationSettings()
    gender = settings.get('gender', 'female')
    return render_template('manage.html', 
                         entries=entries, 
                         medications=medications, 
                         today_date=today_date,
                         edit_medication_id=edit_medication_id,
                         gender=gender)

@app.route('/edit/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(entry_id):
    logger.info(f"Entry edit attempt by user: {current_user.username}, entry_id: {entry_id}")
    entry = MoodEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    data = request.form
    
    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Check if entry is for a future date
    if new_date > today:
        logger.warning(f"Future date edit attempt by user: {current_user.username}, entry_id: {entry_id}, date: {new_date}")
        flash('Cannot edit entries to future dates. Please select today\'s date or a past date.', 'warning')
        return redirect(url_for('manage_entries'))
    
    # Check if the new date conflicts with another entry for this user
    if new_date != entry.entry_date:
        existing_entry = MoodEntry.query.filter_by(entry_date=new_date, user_id=current_user.id).first()
        if existing_entry and existing_entry.id != entry_id:
            logger.warning(f"Date conflict edit attempt by user: {current_user.username}, entry_id: {entry_id}, date: {new_date}")
            flash('An entry already exists for this date.', 'warning')
            return redirect(url_for('manage_entries'))
    
    try:
        entry.entry_date = new_date
        entry.mood_level = int(data['mood'])
        entry.hours_slept = float(data['hours_slept'])
        entry.anxiety = int(data['anxiety'])
        entry.energy_level = int(data['energy'])
        entry.irritability = int(data['irritability'])
        entry.alcohol_drugs = data.get('alcohol_drugs') == 'on'
        entry.exercise = data.get('exercise') == 'on'
        entry.menstruation = data.get('menstruation') == 'on'
        entry.stressful_event = data.get('stressful_event') == 'on'
        entry.weight = float(data['weight']) if data.get('weight') else None
        entry.notes = data.get('notes', '')
        
        db.session.commit()
        logger.info(f"Entry edited successfully - user: {current_user.username}, entry_id: {entry_id}")
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('manage_entries'))
    except Exception as e:
        logger.error(f"Entry edit failed - user: {current_user.username}, entry_id: {entry_id}, error: {str(e)}")
        db.session.rollback()
        flash('Failed to update entry. Please try again.', 'error')
        return redirect(url_for('manage_entries'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    logger.info(f"Entry deletion attempt by user: {current_user.username}, entry_id: {entry_id}")
    entry = MoodEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    try:
        db.session.delete(entry)
        db.session.commit()
        logger.info(f"Entry deleted successfully - user: {current_user.username}, entry_id: {entry_id}")
        flash('Entry deleted successfully!', 'success')
        return redirect(url_for('manage_entries'))
    except Exception as e:
        logger.error(f"Entry deletion failed - user: {current_user.username}, entry_id: {entry_id}, error: {str(e)}")
        db.session.rollback()
        flash('Failed to delete entry. Please try again.', 'error')
        return redirect(url_for('manage_entries'))

@app.route('/data')
@login_required
def get_data():
    logger.info(f"Data API accessed by user: {current_user.username}")
    entries = MoodEntry.query.filter_by(user_id=current_user.id).all()
    data = [{
        'date': entry.entry_date.strftime('%Y-%m-%d'),
        'mood': entry.mood_level,
        'hours_slept': entry.hours_slept,
        'anxiety': entry.anxiety,
        'energy': entry.energy_level,
        'irritability': entry.irritability,
        'weight': entry.weight if entry.weight else None,
    } for entry in entries]
    return jsonify(data)

@app.route('/visualize')
@login_required
def visualize():
    logger.info(f"Visualization page accessed by user: {current_user.username}")
    entries = MoodEntry.query.filter_by(user_id=current_user.id).all()
    
    if entries:
        logger.info(f"Generating visualization for user: {current_user.username}, entries count: {len(entries)}")
        dates = [entry.entry_date.strftime('%Y-%m-%d') for entry in entries]  # Remove time
        mood = [entry.mood_level for entry in entries]
        hours_slept = [entry.hours_slept for entry in entries]
        anxiety = [entry.anxiety for entry in entries]
        energy = [entry.energy_level for entry in entries]
        irritability = [entry.irritability for entry in entries]
        weight = [entry.weight for entry in entries if entry.weight is not None]
        weight_dates = [entry.entry_date.strftime('%Y-%m-%d') for entry in entries if entry.weight is not None]
        
        # Get all unique medications for consistent colors
        all_medications = set()
        for entry in entries:
            for mem in entry.medications:
                if mem.taken:
                    all_medications.add(mem.medication.name)
        
        # Create color map for medications
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        medication_colors = {med: colors[i % len(colors)] for i, med in enumerate(all_medications)}
        
        # Create subplot with secondary y-axis for medications
        fig = go.Figure()
        
        # Add main metrics traces
        fig.add_trace(go.Scatter(
            x=dates,
            y=mood,
            name='Mood',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=hours_slept,
            name='Hours Slept',
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=anxiety,
            name='Anxiety',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=energy,
            name='Energy',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=irritability,
            name='Irritability',
            mode='lines+markers'
        ))
        
        # Add weight trace if there's weight data
        if weight:
            fig.add_trace(go.Scatter(
                x=weight_dates,
                y=weight,
                name='Weight',
                mode='lines+markers',
                yaxis='y3'
            ))
        
        # Add medication blocks at the bottom
        for i, entry in enumerate(entries):
            meds_taken = []
            for mem in entry.medications:
                if mem.taken:
                    meds_taken.append(mem.medication.name)
            
            if meds_taken:
                # Create a stacked bar for multiple medications
                for j, med in enumerate(meds_taken):
                    fig.add_trace(go.Bar(
                        x=[dates[i]],
                        y=[1],
                        name=med,
                        marker_color=medication_colors[med],
                        showlegend=False if i > 0 else True,  # Only show legend for first occurrence
                        yaxis='y4',
                        opacity=0.8,
                        width=0.8
                    ))
        
        # Update layout with four y-axes
        layout_updates = {
            'title': 'Mood Tracker Over Time',
            'xaxis_title': 'Date',
            'yaxis_title': 'Level (0-10)',
            'yaxis': dict(range=[0, 10]),
            'yaxis2': dict(
                title='Hours Slept',
                overlaying='y',
                side='right',
                range=[0, 12]
            ),
            'yaxis4': dict(
                title='Medications',
                overlaying='y',
                side='right',
                position=0.02,
                range=[0, 1],
                showticklabels=False,
                showgrid=False
            ),
            'hovermode': 'x unified',
            'height': 800,  # Increase height to accommodate medication section
            'margin': dict(b=80, t=80),  # Add margins
            'barmode': 'stack'  # Stack medication bars
        }
        
        # Add third y-axis for weight if there's weight data
        if weight:
            layout_updates['yaxis3'] = dict(
                title='Weight (lbs)',
                overlaying='y',
                side='right',
                position=0.95,
                range=[min(weight) - 5, max(weight) + 5] if weight else [0, 200]
            )
        
        fig.update_layout(**layout_updates)
        
        graphJSON = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder)
        return render_template('visualize.html', graphJSON=graphJSON)
    return render_template('visualize.html', graphJSON=None)

@app.route('/add_medication', methods=['POST'])
@login_required
def add_medication():
    name = request.form.get('medication_name', '').strip()
    logger.info(f"Medication addition attempt by user: {current_user.username}, medication: {name}")
    
    if name:
        existing = Medication.query.filter_by(name=name, user_id=current_user.id).first()
        if existing:
            if not existing.active:
                existing.active = True
                db.session.commit()
                logger.info(f"Medication reactivated by user: {current_user.username}, medication: {name}")
                flash(f'Medication "{name}" reactivated.', 'success')
            else:
                logger.warning(f"Duplicate medication attempt by user: {current_user.username}, medication: {name}")
                flash(f'Medication "{name}" already exists.', 'warning')
        else:
            try:
                med = Medication(name=name, user_id=current_user.id)
                db.session.add(med)
                db.session.commit()
                logger.info(f"Medication added successfully by user: {current_user.username}, medication: {name}, med_id: {med.id}")
                flash(f'Medication "{name}" added.', 'success')
            except Exception as e:
                logger.error(f"Medication addition failed - user: {current_user.username}, medication: {name}, error: {str(e)}")
                db.session.rollback()
                flash('Failed to add medication. Please try again.', 'error')
    else:
        logger.warning(f"Empty medication name attempt by user: {current_user.username}")
        flash('Medication name cannot be empty.', 'danger')
    return redirect(url_for('manage_entries'))

@app.route('/deactivate_medication/<int:med_id>', methods=['POST'])
@login_required
def deactivate_medication(med_id):
    med = Medication.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    med.active = False
    db.session.commit()
    flash(f'Medication "{med.name}" deactivated.', 'info')
    return redirect(url_for('manage_entries'))

@app.route('/activate_medication/<int:med_id>', methods=['POST'])
@login_required
def activate_medication(med_id):
    med = Medication.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    med.active = True
    db.session.commit()
    flash(f'Medication "{med.name}" activated.', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/edit_medication/<int:med_id>', methods=['POST'])
@login_required
def edit_medication(med_id):
    med = Medication.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    new_name = request.form.get('medication_name', '').strip()
    if not new_name:
        flash('Medication name cannot be empty.', 'danger')
        return redirect(url_for('manage_entries', edit_medication_id=med_id))
    existing = Medication.query.filter(Medication.name == new_name, Medication.id != med_id, Medication.user_id == current_user.id).first()
    if existing:
        flash('A medication with that name already exists.', 'warning')
        return redirect(url_for('manage_entries', edit_medication_id=med_id))
    med.name = new_name
    db.session.commit()
    flash('Medication name updated.', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/admin')
@login_required
def admin():
    """Admin panel for testing and system management."""
    logger.info(f"Admin panel accessed by user: {current_user.username}")
    return render_template('admin.html', 
                         enabled=notification_settings.get('enabled', True),
                         time=notification_settings.get('time', '15:00'),
                         timezone=notification_settings.get('timezone', 'US/Eastern'),
                         duration=notification_settings.get('duration', 10),
                         gender=notification_settings.get('gender', 'female'))

@app.route('/test_notification', methods=['POST'])
def test_notification():
    """Send a test notification."""
    logger.info(f"Test notification requested by user: {current_user.username if current_user.is_authenticated else 'anonymous'}")
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            "Mood Tracker Test",
            "This is a test notification from the admin panel!",
            duration=5,
            threaded=True
        )
        logger.info("Test notification sent successfully")
        flash('Test notification sent successfully!', 'success')
    except Exception as e:
        logger.error(f"Test notification failed: {str(e)}")
        flash(f'Error sending notification: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/update_notification_settings', methods=['POST'])
def update_notification_settings():
    """Update notification settings."""
    logger.info(f"Notification settings update requested by user: {current_user.username if current_user.is_authenticated else 'anonymous'}")
    try:
        notification_settings.settings['enabled'] = 'enabled' in request.form
        notification_settings.settings['time'] = request.form.get('time', '15:00')
        notification_settings.settings['timezone'] = request.form.get('timezone', 'US/Eastern')
        notification_settings.settings['duration'] = int(request.form.get('duration', 10))
        notification_settings.settings['gender'] = request.form.get('gender', 'female')
        notification_settings.save()
        logger.info("Notification settings updated successfully")
        flash('Notification settings updated successfully!', 'success')
    except Exception as e:
        logger.error(f"Notification settings update failed: {str(e)}")
        flash('Failed to update notification settings.', 'error')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    logger.info("Starting Mood Tracker application...")
    logger.info(f"Beta code: {BETA_CODE}")
    logger.info(f"Database: {DATABASE_URI}")
    logger.info("Application ready to serve requests")
    app.run(debug=True) 
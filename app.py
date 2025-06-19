from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objects as go
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
app.secret_key = 'your-secret-key-here'  # Required for flash messages
db = SQLAlchemy(app)

# Notification settings file
NOTIFICATION_SETTINGS_FILE = 'notification_settings.json'

class NotificationSettings:
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self):
        default_settings = {
            'enabled': True,
            'time': '15:00',
            'timezone': 'EST',
            'duration': 10
        }
        
        if os.path.exists(NOTIFICATION_SETTINGS_FILE):
            try:
                with open(NOTIFICATION_SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        with open(NOTIFICATION_SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get_setting(self, key):
        return self.settings.get(key)
    
    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

# Global notification settings instance
notification_settings = NotificationSettings()

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)  # For soft delete
    
class MoodEntryMedication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood_entry_id = db.Column(db.Integer, db.ForeignKey('mood_entry.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken = db.Column(db.Boolean, default=False)
    
    medication = db.relationship('Medication')

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False, unique=True)
    energy_level = db.Column(db.Integer, nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)
    stress_level = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    medications = db.relationship('MoodEntryMedication', backref='mood_entry', cascade='all, delete-orphan')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    entries = MoodEntry.query.order_by(MoodEntry.entry_date.desc()).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    medications = Medication.query.filter_by(active=True).order_by(Medication.name).all()
    return render_template('index.html', entries=entries, today_date=today_date, medications=medications)

@app.route('/submit', methods=['POST'])
def submit_entry():
    data = request.form
    entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Check if entry is for a future date
    if entry_date > today:
        flash('Cannot create entries for future dates. Please select today\'s date or a past date.', 'warning')
        return redirect(url_for('index'))
    
    # Check if entry already exists for this date
    existing_entry = MoodEntry.query.filter_by(entry_date=entry_date).first()
    if existing_entry:
        flash('An entry already exists for this date. Please edit the existing entry instead.', 'warning')
        return redirect(url_for('manage_entries'))
    
    new_entry = MoodEntry(
        entry_date=entry_date,
        energy_level=int(data['energy']),
        mood_level=int(data['mood']),
        stress_level=int(data['stress']),
        notes=data.get('notes', '')
    )
    db.session.add(new_entry)
    db.session.flush()  # Get new_entry.id before commit

    # Save medications taken
    taken_ids = data.getlist('medications_taken')
    for med in Medication.query.filter(Medication.id.in_(taken_ids)).all():
        mem = MoodEntryMedication(mood_entry_id=new_entry.id, medication_id=med.id, taken=True)
        db.session.add(mem)
    db.session.commit()
    flash('Entry added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/manage')
def manage_entries():
    entries = MoodEntry.query.order_by(MoodEntry.entry_date.desc()).all()
    medications = Medication.query.order_by(Medication.name).all()
    edit_medication_id = request.args.get('edit_medication_id', type=int)
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('manage.html', entries=entries, medications=medications, edit_medication_id=edit_medication_id, today_date=today_date)

@app.route('/edit/<int:entry_id>', methods=['POST'])
def edit_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    data = request.form
    
    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Check if entry is for a future date
    if new_date > today:
        flash('Cannot edit entries to future dates. Please select today\'s date or a past date.', 'warning')
        return redirect(url_for('manage_entries'))
    
    # Check if the new date conflicts with another entry
    if new_date != entry.entry_date:
        existing_entry = MoodEntry.query.filter_by(entry_date=new_date).first()
        if existing_entry and existing_entry.id != entry_id:
            flash('An entry already exists for this date.', 'warning')
            return redirect(url_for('manage_entries'))
    
    entry.entry_date = new_date
    entry.energy_level = int(data['energy'])
    entry.mood_level = int(data['mood'])
    entry.stress_level = int(data['stress'])
    entry.notes = data.get('notes', '')
    
    db.session.commit()
    flash('Entry updated successfully!', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/data')
def get_data():
    entries = MoodEntry.query.all()
    data = [{
        'date': entry.entry_date.strftime('%Y-%m-%d'),
        'energy': entry.energy_level,
        'mood': entry.mood_level,
        'stress': entry.stress_level,
    } for entry in entries]
    return jsonify(data)

@app.route('/visualize')
def visualize():
    entries = MoodEntry.query.all()
    
    if entries:
        dates = [entry.entry_date for entry in entries]
        energy = [entry.energy_level for entry in entries]
        mood = [entry.mood_level for entry in entries]
        stress = [entry.stress_level for entry in entries]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=energy,
            name='Energy',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=mood,
            name='Mood',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=stress,
            name='Stress',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Mood Tracker Over Time',
            xaxis_title='Date',
            yaxis_title='Level',
            yaxis=dict(range=[0, 10]),
            hovermode='x unified'
        )
        
        graphJSON = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder)
        return render_template('visualize.html', graphJSON=graphJSON)
    return render_template('visualize.html', graphJSON=None)

@app.route('/add_medication', methods=['POST'])
def add_medication():
    name = request.form.get('medication_name', '').strip()
    if name:
        existing = Medication.query.filter_by(name=name).first()
        if existing:
            if not existing.active:
                existing.active = True
                db.session.commit()
                flash(f'Medication "{name}" reactivated.', 'success')
            else:
                flash(f'Medication "{name}" already exists.', 'warning')
        else:
            med = Medication(name=name)
            db.session.add(med)
            db.session.commit()
            flash(f'Medication "{name}" added.', 'success')
    else:
        flash('Medication name cannot be empty.', 'danger')
    return redirect(url_for('manage_entries'))

@app.route('/deactivate_medication/<int:med_id>', methods=['POST'])
def deactivate_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    med.active = False
    db.session.commit()
    flash(f'Medication "{med.name}" deactivated.', 'info')
    return redirect(url_for('manage_entries'))

@app.route('/activate_medication/<int:med_id>', methods=['POST'])
def activate_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    med.active = True
    db.session.commit()
    flash(f'Medication "{med.name}" activated.', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/edit_medication/<int:med_id>', methods=['POST'])
def edit_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    new_name = request.form.get('medication_name', '').strip()
    if not new_name:
        flash('Medication name cannot be empty.', 'danger')
        return redirect(url_for('manage_entries', edit_medication_id=med_id))
    existing = Medication.query.filter(Medication.name == new_name, Medication.id != med_id).first()
    if existing:
        flash('A medication with that name already exists.', 'warning')
        return redirect(url_for('manage_entries', edit_medication_id=med_id))
    med.name = new_name
    db.session.commit()
    flash('Medication name updated.', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/admin')
def admin():
    """Admin panel for testing and system management."""
    return render_template('admin.html', settings=notification_settings.settings)

@app.route('/test_notification', methods=['POST'])
def test_notification():
    """Send a test notification."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            "Mood Tracker Test",
            "This is a test notification from the admin panel!",
            duration=5,
            threaded=True
        )
        flash('Test notification sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending notification: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/update_notification_settings', methods=['POST'])
def update_notification_settings():
    """Update notification settings."""
    try:
        enabled = request.form.get('enabled') == 'on'
        time = request.form.get('time', '15:00')
        timezone = request.form.get('timezone', 'EST')
        duration = int(request.form.get('duration', 10))
        
        notification_settings.update_setting('enabled', enabled)
        notification_settings.update_setting('time', time)
        notification_settings.update_setting('timezone', timezone)
        notification_settings.update_setting('duration', duration)
        
        flash('Notification settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True) 
import os
import sys
import schedule
import time
from datetime import datetime, timezone, timedelta
from win10toast import ToastNotifier
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the database models from app.py
from app import db, MoodEntry

def load_notification_settings():
    """Load notification settings from JSON file."""
    settings_file = 'notification_settings.json'
    default_settings = {
        'enabled': True,
        'time': '15:00',
        'timezone': 'EST',
        'duration': 10
    }
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except:
            return default_settings
    return default_settings

def get_timezone_offset(timezone_name):
    """Get timezone offset in hours."""
    timezone_offsets = {
        'EST': -5,
        'CST': -6,
        'MST': -7,
        'PST': -8
    }
    return timezone_offsets.get(timezone_name, -5)  # Default to EST

def check_today_entry():
    """Check if an entry exists for today and send notification if not."""
    try:
        # Load current settings
        settings = load_notification_settings()
        
        # Check if notifications are enabled
        if not settings.get('enabled', True):
            print(f"Notifications are disabled - skipping check")
            return
        
        # Get timezone offset
        tz_offset = get_timezone_offset(settings.get('timezone', 'EST'))
        tz = timezone(timedelta(hours=tz_offset))
        today = datetime.now(tz).date()
        
        # Check if entry exists for today
        existing_entry = MoodEntry.query.filter_by(entry_date=today).first()
        
        if not existing_entry:
            # Send notification
            toaster = ToastNotifier()
            duration = settings.get('duration', 10)
            toaster.show_toast(
                "Mood Tracker Reminder",
                "You haven't logged your mood today! Open your browser to add your entry.",
                duration=duration,
                threaded=True
            )
            print(f"Notification sent at {datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')} - No entry found for today")
        else:
            print(f"Entry already exists for today ({today}) - no notification needed")
            
    except Exception as e:
        print(f"Error checking today's entry: {e}")

def open_mood_tracker():
    """Open the mood tracker in the default browser."""
    import webbrowser
    webbrowser.open('http://localhost:5000')

def run_notification_service():
    """Run the notification service."""
    print("Starting Mood Tracker Notification Service...")
    
    # Load initial settings
    settings = load_notification_settings()
    notification_time = settings.get('time', '15:00')
    timezone_name = settings.get('timezone', 'EST')
    
    print(f"Service will check for entries daily at {notification_time} {timezone_name}")
    print(f"Notifications enabled: {settings.get('enabled', True)}")
    print("Press Ctrl+C to stop the service")
    
    # Schedule the check for the configured time
    schedule.every().day.at(notification_time).do(check_today_entry)
    
    # Also run an immediate check when starting (for testing)
    print("Running initial check...")
    check_today_entry()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nNotification service stopped.")

if __name__ == "__main__":
    # Create Flask app context for database operations
    from app import app
    with app.app_context():
        run_notification_service() 
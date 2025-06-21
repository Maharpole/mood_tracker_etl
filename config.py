"""
Configuration file for Mood Tracker application.
You can modify these settings without touching the main application code.
"""

# Beta access configuration
BETA_CODE = "moodtracker2024"  # Change this to your desired beta code

# Application settings
SECRET_KEY = 'your-secret-key-here'  # Change this for production
DATABASE_URI = 'sqlite:///mood_tracker.db'

# Notification settings
DEFAULT_NOTIFICATION_TIME = '15:00'
DEFAULT_TIMEZONE = 'US/Eastern'
DEFAULT_DURATION = 10
DEFAULT_GENDER = 'female'

# Security settings
MIN_PASSWORD_LENGTH = 6 
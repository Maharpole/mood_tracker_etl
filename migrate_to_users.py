#!/usr/bin/env python3
"""
Migration script to add user authentication to existing mood tracker data.
This script will create a default user and associate all existing data with that user.
"""

import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, MoodEntry, Medication

def backup_existing_data():
    """Backup existing data before migration."""
    db_path = 'instance/mood_tracker.db'
    if os.path.exists(db_path):
        backup_path = 'instance/mood_tracker_backup.db'
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Backed up existing database to {backup_path}")
        return backup_path
    return None

def restore_data_from_backup(backup_path):
    """Restore data from backup to new schema."""
    if not backup_path or not os.path.exists(backup_path):
        return
    
    print("Restoring data from backup...")
    
    # Connect to backup database
    backup_conn = sqlite3.connect(backup_path)
    backup_cursor = backup_conn.cursor()
    
    # Get existing mood entries
    backup_cursor.execute("SELECT entry_date, mood_level, hours_slept, anxiety, energy_level, irritability, alcohol_drugs, exercise, menstruation, stressful_event, weight, notes FROM mood_entry")
    mood_entries = backup_cursor.fetchall()
    
    # Get existing medications
    backup_cursor.execute("SELECT name, active FROM medication")
    medications = backup_cursor.fetchall()
    
    backup_conn.close()
    
    # Get the default user
    default_user = User.query.filter_by(username='default_user').first()
    if not default_user:
        print("Default user not found!")
        return
    
    # Restore mood entries
    print(f"Restoring {len(mood_entries)} mood entries...")
    for entry_data in mood_entries:
        entry = MoodEntry(
            user_id=default_user.id,
            entry_date=datetime.strptime(entry_data[0], '%Y-%m-%d').date(),
            mood_level=entry_data[1],
            hours_slept=entry_data[2],
            anxiety=entry_data[3],
            energy_level=entry_data[4],
            irritability=entry_data[5],
            alcohol_drugs=bool(entry_data[6]),
            exercise=bool(entry_data[7]),
            menstruation=bool(entry_data[8]),
            stressful_event=bool(entry_data[9]),
            weight=entry_data[10],
            notes=entry_data[11] or ''
        )
        db.session.add(entry)
    
    # Restore medications
    print(f"Restoring {len(medications)} medications...")
    for med_data in medications:
        medication = Medication(
            name=med_data[0],
            active=bool(med_data[1]),
            user_id=default_user.id
        )
        db.session.add(medication)
    
    db.session.commit()
    print("Data restoration completed!")

def migrate_data():
    """Migrate existing data to user authentication system."""
    with app.app_context():
        print("Starting migration to user authentication system...")
        
        # Check if there are any existing users
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"Found {existing_users} existing user(s). Migration may have already been run.")
            return
        
        # Backup existing data
        backup_path = backup_existing_data()
        
        # Drop and recreate all tables
        print("Recreating database with new schema...")
        db.drop_all()
        db.create_all()
        
        # Create default user
        print("Creating default user...")
        default_user = User(
            username='default_user',
            email='default@example.com',
            password_hash=generate_password_hash('changeme123'),
            created_at=datetime.now()
        )
        db.session.add(default_user)
        db.session.flush()  # Get the user ID
        
        print(f"Created default user with ID: {default_user.id}")
        
        # Restore data from backup if it exists
        if backup_path:
            restore_data_from_backup(backup_path)
        else:
            print("No existing data found to migrate.")
        
        print("\nMigration completed successfully!")
        print(f"Default user created:")
        print(f"  Username: default_user")
        print(f"  Email: default@example.com")
        print(f"  Password: changeme123")
        print("\nIMPORTANT: Please change the default password after logging in!")

if __name__ == '__main__':
    try:
        migrate_data()
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
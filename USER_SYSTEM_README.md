# User Authentication System

This document describes the user authentication system that has been added to the Mood Tracker application.

## Overview

The Mood Tracker now supports multiple users with individual accounts. Each user has their own:
- Mood entries
- Medications
- Data visualizations
- Settings

## Features

### Beta Code Access Control
- **Beta Code Required**: Users must enter a valid beta code to create an account
- **Controlled Access**: Only people with the beta code can register
- **Easy Management**: Beta code can be changed via configuration file or management script

### User Registration
- Users can create new accounts with username, email, password, and beta code
- Password validation (minimum 6 characters)
- Email and username uniqueness validation
- Password confirmation check
- Beta code verification

### User Login
- Secure login with username and password
- Session management with Flask-Login
- Automatic redirect to requested page after login

### User Logout
- Secure logout functionality
- Session cleanup

### Data Isolation
- All mood entries are associated with specific users
- Medications are user-specific
- Visualizations show only user's own data
- Users cannot access other users' data

## Installation and Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Beta Code
Edit `config.py` to set your desired beta code:
```python
BETA_CODE = "your-custom-beta-code-here"
```

Or use the management script:
```bash
python manage_beta_code.py
```

### 3. Run Database Migration (if upgrading from existing installation)
If you have existing mood tracker data, run the migration script:
```bash
python migrate_to_users.py
```

This will:
- Create a default user account
- Associate all existing data with the default user
- Default credentials: `default_user` / `changeme123`

### 4. Start the Application
```bash
python app.py
```

### 5. Access the Application
- Navigate to `http://localhost:5000`
- You'll be redirected to the login page
- Use the default credentials or create a new account with the beta code

## Beta Code Management

### Changing the Beta Code
You can change the beta code in several ways:

1. **Edit config.py directly**:
   ```python
   BETA_CODE = "new-beta-code-here"
   ```

2. **Use the management script**:
   ```bash
   python manage_beta_code.py
   ```

3. **Show current beta code**:
   ```bash
   python manage_beta_code.py
   # Choose option 1
   ```

### Sharing the Beta Code
- Share the beta code with friends you want to give access to
- They'll need this code to create an account
- Without the code, registration will be blocked

## Database Schema Changes

### New Tables
- `user`: Stores user account information
  - `id`: Primary key
  - `username`: Unique username
  - `email`: Unique email address
  - `password_hash`: Hashed password
  - `created_at`: Account creation timestamp
  - `is_active`: Account status

### Modified Tables
- `mood_entry`: Added `user_id` foreign key
- `medication`: Added `user_id` foreign key

### Constraints
- Unique constraint on `user_id` + `entry_date` for mood entries
- Unique usernames and emails across all users

## Security Features

- Password hashing using Werkzeug's security functions
- Session management with Flask-Login
- CSRF protection (built into Flask-WTF)
- Input validation and sanitization
- SQL injection protection through SQLAlchemy ORM

## User Management

### Creating New Users
1. Navigate to `/register`
2. Fill in username, email, and password
3. Confirm password
4. Submit form

### Logging In
1. Navigate to `/login`
2. Enter username and password
3. Submit form

### Logging Out
1. Click "Logout" in the navigation bar
2. Session will be cleared

## Default User Account

After running the migration script, a default user account is created:
- **Username**: `default_user`
- **Email**: `default@example.com`
- **Password**: `changeme123`

**Important**: Change the default password after first login for security.

## Troubleshooting

### Migration Issues
If the migration script fails:
1. Check that the database file exists
2. Ensure you have write permissions
3. Verify all dependencies are installed

### Login Issues
- Ensure username and password are correct
- Check that the user account is active
- Clear browser cookies if session issues occur

### Data Not Showing
- Verify you're logged in with the correct account
- Check that data was properly migrated
- Ensure the user has associated mood entries

## API Changes

All routes now require authentication except:
- `/login` (GET/POST)
- `/register` (GET/POST)

Protected routes include:
- `/` (index)
- `/submit` (POST)
- `/manage`
- `/edit/<id>` (POST)
- `/delete/<id>` (POST)
- `/data`
- `/visualize`
- `/admin`
- All medication management routes

## Future Enhancements

Potential improvements for the user system:
- Password reset functionality
- Email verification
- User profile management
- Admin user roles
- Data export/import
- Account deletion
- Password strength requirements
- Two-factor authentication

## Logging System

The application includes comprehensive logging to help with debugging and monitoring:

### Log Files
- `logs/mood_tracker.log`: Main application log with all events
- `logs/errors.log`: Error-only log for quick debugging

### Log Levels
- **INFO**: Normal application events (logins, data operations, etc.)
- **WARNING**: Potential issues (invalid inputs, duplicate attempts, etc.)
- **ERROR**: Application errors and exceptions

### What Gets Logged
- User registration and login attempts
- Mood entry creation, editing, and deletion
- Medication management operations
- Page access and navigation
- Database operations and errors
- Beta code usage and validation
- Application startup and configuration

### Using the Log Viewer
```bash
python view_logs.py
```

Features:
- View log statistics
- Search for specific terms
- View user activity
- View today's logs
- View recent errors
- Clear log files

### Log Rotation
- Log files are automatically rotated when they reach 10MB
- Up to 5 backup files are kept
- Prevents logs from consuming too much disk space

### Debugging Tips
1. **Check recent logs**: `python view_logs.py` → Option 2
2. **Look for errors**: `python view_logs.py` → Option 3
3. **Search for specific user**: `python view_logs.py` → Option 5
4. **Monitor today's activity**: `python view_logs.py` → Option 6 
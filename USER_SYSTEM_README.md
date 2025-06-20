# User Authentication System

This document describes the user authentication system that has been added to the Mood Tracker application.

## Overview

The Mood Tracker now supports multiple users with individual accounts. Each user has their own:
- Mood entries
- Medications
- Data visualizations
- Settings

## Features

### User Registration
- Users can create new accounts with username, email, and password
- Password validation (minimum 6 characters)
- Email and username uniqueness validation
- Password confirmation check

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

### 2. Run Database Migration (if upgrading from existing installation)
If you have existing mood tracker data, run the migration script:
```bash
python migrate_to_users.py
```

This will:
- Create a default user account
- Associate all existing data with the default user
- Default credentials: `default_user` / `changeme123`

### 3. Start the Application
```bash
python app.py
```

### 4. Access the Application
- Navigate to `http://localhost:5000`
- You'll be redirected to the login page
- Use the default credentials or create a new account

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
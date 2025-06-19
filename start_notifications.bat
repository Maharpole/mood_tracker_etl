@echo off
echo Starting Mood Tracker Notification Service...
echo This will check for mood entries daily at 3:00 PM EST
echo.
echo Make sure your Flask app is running first!
echo.
pause
python notification_service.py
pause 
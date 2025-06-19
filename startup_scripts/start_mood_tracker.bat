@echo off
title Mood Tracker Startup
echo ========================================
echo Starting Mood Tracker System
echo ========================================
echo.

echo Starting Flask application...
start "Flask App" cmd /k "python app.py"

echo Waiting 5 seconds for Flask to start...
timeout /t 5 /nobreak > nul

echo Starting notification service...
start "Notification Service" cmd /k "python notification_service.py"

echo.
echo ========================================
echo Mood Tracker is now running!
echo ========================================
echo.
echo Flask App: http://localhost:5000
echo Notification Service: Running in background
echo.
echo Both services will continue running until you close their windows.
echo.
pause 
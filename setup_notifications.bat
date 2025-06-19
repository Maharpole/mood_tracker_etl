@echo off
echo ========================================
echo Mood Tracker Notification System Setup
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To use the notification system:
echo.
echo 1. Start your Flask app (in one terminal):
echo    python app.py
echo.
echo 2. Start the notification service (in another terminal):
echo    python notification_service.py
echo.
echo OR use the batch file:
echo    start_notifications.bat
echo.
echo The service will:
echo - Check daily at 3:00 PM EST for mood entries
echo - Send a Windows notification if no entry exists
echo - Open the mood tracker when you click the notification
echo.
echo To test the notification system:
echo    python test_notification.py
echo.
pause 
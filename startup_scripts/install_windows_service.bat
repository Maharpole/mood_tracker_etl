@echo off
echo ========================================
echo Installing Mood Tracker as Windows Service
echo ========================================
echo.
echo This will install the notification service to start automatically with Windows.
echo You will need administrator privileges.
echo.

echo Installing pywin32 if not already installed...
pip install pywin32

echo.
echo Installing the notification service...
python notification_service_windows.py install

echo.
echo Starting the service...
python notification_service_windows.py start

echo.
echo ========================================
echo Service Installation Complete!
echo ========================================
echo.
echo The notification service will now:
echo - Start automatically when Windows boots
echo - Run in the background
echo - Send notifications at 3:00 PM EST daily
echo.
echo To manage the service:
echo - Stop: python notification_service_windows.py stop
echo - Start: python notification_service_windows.py start
echo - Remove: python notification_service_windows.py remove
echo.
echo You still need to start your Flask app manually or set it up separately.
echo.
pause 
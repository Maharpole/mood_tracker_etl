@echo off
echo ========================================
echo Restarting Notification Service
echo ========================================
echo.

echo Stopping any existing notification service...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Notification Service*" 2>nul

echo.
echo Starting notification service with new settings...
start "Notification Service" cmd /k "python notification_service.py"

echo.
echo Notification service restarted!
echo New settings will take effect immediately.
echo.
pause 
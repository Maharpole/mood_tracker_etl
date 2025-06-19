@echo off
echo ========================================
echo Adding Mood Tracker to Windows Startup
echo ========================================
echo.

echo Creating startup shortcut...
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Create the startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create the batch file content
echo @echo off > "%STARTUP_FOLDER%\MoodTracker.bat"
echo cd /d "%CURRENT_DIR%" >> "%STARTUP_FOLDER%\MoodTracker.bat"
echo start "Flask App" cmd /k "python app.py" >> "%STARTUP_FOLDER%\MoodTracker.bat"
echo timeout /t 5 /nobreak ^> nul >> "%STARTUP_FOLDER%\MoodTracker.bat"
echo start "Notification Service" cmd /k "python notification_service.py" >> "%STARTUP_FOLDER%\MoodTracker.bat"

echo Startup shortcut created at:
echo %STARTUP_FOLDER%\MoodTracker.bat
echo.
echo The mood tracker will now start automatically when you log into Windows.
echo.
echo To remove from startup, delete the file:
echo %STARTUP_FOLDER%\MoodTracker.bat
echo.
pause 
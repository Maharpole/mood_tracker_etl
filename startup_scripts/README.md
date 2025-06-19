# Keeping Your Mood Tracker Running

This guide shows you different ways to keep your mood tracker and notification service running on your computer.

## 🚀 Quick Start Options

### Option 1: Manual Startup (Simplest)
Run this whenever you want to use the mood tracker:
```bash
startup_scripts/start_mood_tracker.bat
```

### Option 2: Windows Startup Folder (Recommended)
Automatically starts when you log into Windows:
```bash
startup_scripts/create_startup_shortcut.bat
```

### Option 3: Windows Service (Advanced)
Runs as a background service (requires admin):
```bash
startup_scripts/install_windows_service.bat
```

## 📋 Detailed Instructions

### Option 1: Manual Startup
**Pros:** Simple, full control
**Cons:** Must remember to start manually

1. Double-click `startup_scripts/start_mood_tracker.bat`
2. Two command windows will open:
   - Flask App (your web interface)
   - Notification Service (background reminders)
3. Keep both windows open while using the system
4. Close windows when done

### Option 2: Windows Startup Folder
**Pros:** Automatic startup, easy to manage
**Cons:** Only starts when you log in

1. Run `startup_scripts/create_startup_shortcut.bat`
2. The mood tracker will now start automatically when you log into Windows
3. To disable: Delete the file from your startup folder
4. To modify: Edit the batch file in the startup folder

**Startup folder location:**
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

### Option 3: Windows Service
**Pros:** Runs in background, survives reboots
**Cons:** More complex setup, requires admin rights

1. **Run as Administrator:** Right-click Command Prompt → "Run as administrator"
2. Navigate to your project folder
3. Run `startup_scripts/install_windows_service.bat`
4. The notification service will now run as a Windows service

**Service Management:**
- View services: `services.msc`
- Stop service: `python notification_service_windows.py stop`
- Start service: `python notification_service_windows.py start`
- Remove service: `python notification_service_windows.py remove`

## 🔧 Troubleshooting

### Flask App Won't Start
- Check if port 5000 is already in use
- Try: `netstat -ano | findstr :5000`
- Kill the process or change the port in `app.py`

### Notification Service Issues
- Test with: `python test_notification.py`
- Check Windows notifications are enabled
- Verify the database exists and is accessible

### Service Won't Install
- Run Command Prompt as Administrator
- Ensure pywin32 is installed: `pip install pywin32`
- Check Windows Event Viewer for errors

## 🎯 Recommended Setup

For most users, I recommend **Option 2 (Windows Startup Folder)** because:
- ✅ Automatic startup
- ✅ Easy to manage
- ✅ No admin rights required
- ✅ Can be easily disabled

## 📱 Accessing Your Mood Tracker

Once running, access your mood tracker at:
```
http://localhost:5000
```

## 🔔 Notification Schedule

- **Time:** 3:00 PM EST daily
- **Condition:** Only if no mood entry exists for today
- **Action:** Windows notification appears
- **Manual Check:** Run `python test_notification.py` to test

## 🛠️ Customization

### Change Notification Time
Edit the time in `notification_service.py`:
```python
schedule.every().day.at("15:00").do(check_today_entry)  # Change "15:00"
```

### Change Timezone
Edit the timezone offset in `notification_service.py`:
```python
est_tz = timezone(timedelta(hours=-5))  # Change -5 for your timezone
```

### Multiple Reminders
Add more scheduled checks:
```python
schedule.every().day.at("09:00").do(check_today_entry)  # Morning reminder
schedule.every().day.at("15:00").do(check_today_entry)  # Afternoon reminder
schedule.every().day.at("20:00").do(check_today_entry)  # Evening reminder
``` 
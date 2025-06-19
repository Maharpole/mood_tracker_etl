# Mood Tracker Notification System

This system provides Windows notifications to remind you to log your mood entry if you haven't done so by 3:00 PM EST.

## Features

- Daily notification at 3:00 PM EST if no mood entry exists for today
- Clickable notification that opens the mood tracker in your browser
- Can run as a background service or manual script
- EST timezone support

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your Flask app is running:
```bash
python app.py
```

## Usage Options

### Option 1: Simple Script (Recommended for testing)

Run the notification service manually:

```bash
python notification_service.py
```

Or use the batch file:
```bash
start_notifications.bat
```

### Option 2: Windows Service (Advanced)

To install as a Windows service (requires admin privileges):

1. Install pywin32 if not already installed:
```bash
pip install pywin32
```

2. Install the service:
```bash
python notification_service_windows.py install
```

3. Start the service:
```bash
python notification_service_windows.py start
```

4. To stop the service:
```bash
python notification_service_windows.py stop
```

5. To remove the service:
```bash
python notification_service_windows.py remove
```

## How It Works

1. The service checks daily at 3:00 PM EST if you have logged a mood entry for today
2. If no entry exists, it sends a Windows notification
3. Clicking the notification opens your mood tracker in the browser
4. The service continues running and checking daily

## Configuration

### Change Notification Time

To change the notification time, edit the time in the script:

```python
# In notification_service.py or notification_service_windows.py
schedule.every().day.at("15:00").do(check_today_entry)  # Change "15:00" to your preferred time
```

### Change Timezone

To change from EST to another timezone, modify the timezone offset:

```python
# For PST (UTC-8)
est_tz = timezone(timedelta(hours=-8))

# For CST (UTC-6)
est_tz = timezone(timedelta(hours=-6))

# For MST (UTC-7)
est_tz = timezone(timedelta(hours=-7))
```

## Troubleshooting

### Notification Not Appearing
- Make sure Windows notifications are enabled
- Check that the Flask app is running
- Verify the database exists and is accessible

### Service Won't Start
- Run as administrator when installing the service
- Check Windows Event Viewer for error messages
- Ensure all dependencies are installed

### Timezone Issues
- The system uses EST (UTC-5) by default
- Adjust the timezone offset in the script if needed
- Consider daylight saving time changes

## Testing

To test the notification system:

1. Make sure you have no entry for today
2. Run the notification service
3. It will send an immediate notification for testing
4. The service will then schedule the daily 3:00 PM check

## Files

- `notification_service.py` - Main notification script
- `notification_service_windows.py` - Windows service version
- `start_notifications.bat` - Batch file for easy startup
- `requirements.txt` - Updated with notification dependencies

## Dependencies Added

- `win10toast==0.9` - Windows notification library
- `schedule==1.2.0` - Task scheduling library
- `pywin32` - Windows service support (for service version) 
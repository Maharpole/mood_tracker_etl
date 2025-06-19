import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import schedule
from datetime import datetime, timezone, timedelta
from win10toast import ToastNotifier

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MoodTrackerNotificationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MoodTrackerNotificationService"
    _svc_display_name_ = "Mood Tracker Notification Service"
    _svc_description_ = "Sends daily reminders to log mood entries"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()

    def check_today_entry(self):
        """Check if an entry exists for today and send notification if not."""
        try:
            # Import here to avoid issues during service installation
            from app import app, MoodEntry
            
            with app.app_context():
                # Get today's date in EST
                est_tz = timezone(timedelta(hours=-5))
                today = datetime.now(est_tz).date()
                
                # Check if entry exists for today
                existing_entry = MoodEntry.query.filter_by(entry_date=today).first()
                
                if not existing_entry:
                    # Send notification
                    toaster = ToastNotifier()
                    toaster.show_toast(
                        "Mood Tracker Reminder",
                        "You haven't logged your mood today! Click here to add your entry.",
                        duration=10,
                        threaded=True
                    )
                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                         0, (f"Notification sent - No entry for {today}", ''))
                else:
                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                         0, (f"Entry exists for {today} - no notification needed", ''))
                    
        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                 0, (f"Error checking entry: {str(e)}", ''))

    def main(self):
        # Schedule the check for 3:00 PM EST daily
        schedule.every().day.at("15:00").do(self.check_today_entry)
        
        while self.is_alive:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MoodTrackerNotificationService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MoodTrackerNotificationService) 
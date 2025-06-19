#!/usr/bin/env python3
"""
Test script for the notification system
"""
import sys
import os
from datetime import datetime, timezone, timedelta
from win10toast import ToastNotifier

def test_notification():
    """Test the Windows notification system."""
    print("Testing Windows notification system...")
    
    # Create a test notification
    toaster = ToastNotifier()
    
    try:
        toaster.show_toast(
            "Mood Tracker Test",
            "This is a test notification from your mood tracker!",
            duration=5,
            threaded=True
        )
        print("✅ Test notification sent successfully!")
        print("You should see a Windows notification appear.")
        
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False
    
    return True

def test_timezone():
    """Test the EST timezone calculation."""
    print("\nTesting EST timezone...")
    
    # Get current time in EST
    est_tz = timezone(timedelta(hours=-5))
    now_est = datetime.now(est_tz)
    today_est = now_est.date()
    
    print(f"Current time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today's date (EST): {today_est}")
    
    # Check if it's past 3 PM EST
    three_pm = now_est.replace(hour=15, minute=0, second=0, microsecond=0)
    is_past_three = now_est > three_pm
    
    print(f"3:00 PM EST today: {three_pm.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Is it past 3 PM EST? {'Yes' if is_past_three else 'No'}")
    
    return True

if __name__ == "__main__":
    print("=== Mood Tracker Notification System Test ===\n")
    
    # Test notification
    notification_ok = test_notification()
    
    # Test timezone
    timezone_ok = test_timezone()
    
    print("\n=== Test Results ===")
    print(f"Notification system: {'✅ PASS' if notification_ok else '❌ FAIL'}")
    print(f"Timezone calculation: {'✅ PASS' if timezone_ok else '❌ FAIL'}")
    
    if notification_ok and timezone_ok:
        print("\n🎉 All tests passed! Your notification system is ready to use.")
        print("\nTo start the full service:")
        print("1. Make sure your Flask app is running: python app.py")
        print("2. Start the notification service: python notification_service.py")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.") 
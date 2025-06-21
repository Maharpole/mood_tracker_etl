#!/usr/bin/env python3
"""
Log Viewer Utility for Mood Tracker
This script helps you view and analyze the application logs.
"""

import os
import sys
from datetime import datetime, timedelta
import re

def show_log_stats():
    """Show statistics about the log files"""
    print("=== Log File Statistics ===\n")
    
    log_files = [
        ('logs/mood_tracker.log', 'Main Application Log'),
        ('logs/errors.log', 'Error Log')
    ]
    
    for log_file, description in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            size_mb = size / (1024 * 1024)
            print(f"{description}:")
            print(f"  File: {log_file}")
            print(f"  Size: {size_mb:.2f} MB")
            
            # Count lines
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  Lines: {len(lines)}")
                
                # Count by log level
                levels = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'DEBUG': 0}
                for line in lines:
                    for level in levels:
                        if f' - {level} - ' in line:
                            levels[level] += 1
                            break
                
                print(f"  INFO: {levels['INFO']}")
                print(f"  WARNING: {levels['WARNING']}")
                print(f"  ERROR: {levels['ERROR']}")
                print(f"  DEBUG: {levels['DEBUG']}")
        else:
            print(f"{description}: File not found")
        print()

def view_recent_logs(log_file='logs/mood_tracker.log', lines=50):
    """View recent log entries"""
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    print(f"=== Recent Log Entries ({lines} lines) ===\n")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in recent_lines:
            print(line.rstrip())

def view_errors(lines=20):
    """View recent error log entries"""
    error_file = 'logs/errors.log'
    if not os.path.exists(error_file):
        print("Error log file not found")
        return
    
    print(f"=== Recent Errors ({lines} lines) ===\n")
    
    with open(error_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in recent_lines:
            print(line.rstrip())

def search_logs(search_term, log_file='logs/mood_tracker.log'):
    """Search logs for specific terms"""
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    print(f"=== Searching for '{search_term}' ===\n")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if search_term.lower() in line.lower():
                print(f"Line {line_num}: {line.rstrip()}")

def view_user_activity(username, log_file='logs/mood_tracker.log'):
    """View activity for a specific user"""
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    print(f"=== User Activity for '{username}' ===\n")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if username.lower() in line.lower():
                print(line.rstrip())

def view_today_logs(log_file='logs/mood_tracker.log'):
    """View logs from today"""
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"=== Today's Logs ({today}) ===\n")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if today in line:
                print(line.rstrip())

def clear_logs():
    """Clear log files (with confirmation)"""
    print("=== Clear Log Files ===\n")
    print("WARNING: This will delete all log files!")
    confirm = input("Are you sure you want to clear all logs? (yes/no): ").lower()
    
    if confirm == 'yes':
        log_files = ['logs/mood_tracker.log', 'logs/errors.log']
        for log_file in log_files:
            if os.path.exists(log_file):
                os.remove(log_file)
                print(f"Deleted: {log_file}")
        print("All logs cleared!")
    else:
        print("Operation cancelled.")

def main():
    print("=== Mood Tracker Log Viewer ===\n")
    
    while True:
        print("1. Show log statistics")
        print("2. View recent logs (50 lines)")
        print("3. View recent errors (20 lines)")
        print("4. Search logs")
        print("5. View user activity")
        print("6. View today's logs")
        print("7. Clear all logs")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            show_log_stats()
        elif choice == '2':
            lines = input("Number of lines to show (default 50): ").strip()
            lines = int(lines) if lines.isdigit() else 50
            view_recent_logs(lines=lines)
        elif choice == '3':
            lines = input("Number of lines to show (default 20): ").strip()
            lines = int(lines) if lines.isdigit() else 20
            view_errors(lines=lines)
        elif choice == '4':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_logs(search_term)
            else:
                print("Search term cannot be empty!")
        elif choice == '5':
            username = input("Enter username: ").strip()
            if username:
                view_user_activity(username)
            else:
                print("Username cannot be empty!")
        elif choice == '6':
            view_today_logs()
        elif choice == '7':
            clear_logs()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    main() 
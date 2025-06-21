#!/usr/bin/env python3
"""
Beta Code Management Script
This script helps you manage the beta code for your mood tracker application.
"""

import os
import sys

def show_current_beta_code():
    """Show the current beta code from config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('BETA_CODE'):
                    code = line.split('=')[1].strip().strip('"\'')
                    print(f"Current beta code: {code}")
                    return code
    except FileNotFoundError:
        print("config.py not found. Using default beta code: moodtracker2024")
        return "moodtracker2024"

def change_beta_code(new_code):
    """Change the beta code in config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the beta code line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('BETA_CODE'):
                lines[i] = f'BETA_CODE = "{new_code}"  # Change this to your desired beta code'
                break
        
        # Write back to file
        with open('config.py', 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Beta code changed to: {new_code}")
        return True
    except Exception as e:
        print(f"Error changing beta code: {e}")
        return False

def main():
    print("=== Mood Tracker Beta Code Manager ===\n")
    
    while True:
        print("1. Show current beta code")
        print("2. Change beta code")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            show_current_beta_code()
        elif choice == '2':
            new_code = input("Enter new beta code: ").strip()
            if new_code:
                change_beta_code(new_code)
            else:
                print("Beta code cannot be empty!")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*40 + "\n")

if __name__ == '__main__':
    main() 
#!/usr/bin/env python3
"""
A simple script that beeps every 5 seconds.
Press Ctrl+C to stop the beeping.
"""

import time
import sys
import subprocess
import os

def beep():
    """Make a beep sound using sox play command."""
    try:
        # Generate a 0.2 second beep at 1000 Hz using sox
        subprocess.run(['play', '-n', 'synth', '0.2', 'sine', '1000'], 
                      capture_output=True, check=True, timeout=3)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: visual beep
        print("🔔 BEEP!", end=' ', flush=True)

def main():
    print("Starting beep timer - beeping every 5 seconds...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            beep()
            print(f"Beep! {time.strftime('%H:%M:%S')}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nBeep timer stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()

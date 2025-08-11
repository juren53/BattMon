#!/usr/bin/env python3
"""
A simple script that beeps every 5 seconds - Windows compatible version.
Press Ctrl+C to stop the beeping.
"""

import time
import sys
import platform

def beep():
    """Make a beep sound using platform-appropriate methods."""
    system = platform.system().lower()
    
    if system == 'windows':
        try:
            # Method 1: Use winsound module (built into Python on Windows)
            import winsound
            # Play a beep at 1000 Hz for 200ms
            winsound.Beep(1000, 200)
            return
        except ImportError:
            pass
        
        try:
            # Method 2: Use os.system with Windows beep command
            import os
            os.system('echo \a')
            return
        except:
            pass
    
    elif system == 'linux' or system == 'darwin':  # Linux or macOS
        try:
            # Use sox if available
            import subprocess
            subprocess.run(['play', '-n', 'synth', '0.2', 'sine', '1000'], 
                          capture_output=True, check=True, timeout=3)
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # Fallback for all systems: visual beep
    print("🔔 BEEP!", end=' ', flush=True)

def main():
    print(f"Starting beep timer on {platform.system()} - beeping every 5 seconds...")
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

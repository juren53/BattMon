#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Windows 11 Proof-of-Concept
Cross-platform battery monitor using psutil and pystray
"""

import os
import sys
import time
import threading
import configparser
from datetime import datetime

# Cross-platform dependencies
try:
    import psutil
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw, ImageFont
    HAS_WINDOWS_DEPS = True
except ImportError as e:
    HAS_WINDOWS_DEPS = False
    print(f"Missing Windows dependencies: {e}")
    print("Install with: pip install psutil pystray pillow")

VERSION = '0.2.0-windows-poc'

class CrossPlatformBatteryMonitor:
    def __init__(self):
        self.running = True
        self.last_percentage = 0
        self.last_state = ""
        self.update_interval = 5  # seconds
        
        if not HAS_WINDOWS_DEPS:
            print("Cannot start: Missing required dependencies")
            sys.exit(1)
            
        print(f"BattMon Windows PoC v{VERSION} starting...")
        print("Cross-platform battery monitor using psutil + pystray")
        
    def get_battery_info(self):
        """Get battery information using psutil (cross-platform)"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {
                    'percentage': 0,
                    'state': 'Unknown',
                    'time_left': None,
                    'is_charging': False
                }
                
            # Convert time from seconds to hours:minutes
            time_left = None
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                time_left = f"{hours:02d}:{minutes:02d}"
                
            state = "Charging" if battery.power_plugged else "Discharging"
            if battery.percent >= 100 and battery.power_plugged:
                state = "Full"
                
            return {
                'percentage': int(battery.percent),
                'state': state,
                'time_left': time_left,
                'is_charging': battery.power_plugged
            }
        except Exception as e:
            print(f"Error getting battery info: {e}")
            return {
                'percentage': 0,
                'state': 'Error',
                'time_left': None,
                'is_charging': False
            }
    
    def create_battery_icon(self, percentage, is_charging=False):
        """Create battery icon using Pillow (cross-platform)"""
        try:
            # Create 32x32 image for better Windows compatibility
            size = 32
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Choose color based on battery level
            if percentage > 75:
                color = (40, 167, 69)  # Bootstrap success green
            elif percentage > 25:
                color = (255, 193, 7)  # Bootstrap warning orange
            else:
                color = (220, 53, 69)  # Bootstrap danger red
                
            # Scale coordinates for 32x32
            scale = size / 24
            
            # Draw battery body (rectangular)
            battery_x = int(4 * scale)
            battery_y = int(10 * scale)
            battery_w = int(20 * scale)
            battery_h = int(12 * scale)
            
            draw.rectangle(
                [(battery_x, battery_y), (battery_x + battery_w, battery_y + battery_h)],
                fill=color,
                outline=(0, 0, 0),
                width=2
            )
            
            # Draw battery terminal
            terminal_x = battery_x + battery_w
            terminal_y = battery_y + int(3 * scale)
            terminal_w = int(3 * scale)
            terminal_h = int(6 * scale)
            
            draw.rectangle(
                [(terminal_x, terminal_y), (terminal_x + terminal_w, terminal_y + terminal_h)],
                fill=(0, 0, 0)
            )
            
            # Add charging indicator
            if is_charging:
                # Draw lightning bolt
                lightning_points = [
                    (int(12 * scale), int(5 * scale)),   # Top
                    (int(18 * scale), int(9 * scale)),   # Right middle
                    (int(15 * scale), int(9 * scale)),   # Center
                    (int(20 * scale), int(13 * scale)),  # Bottom right
                    (int(14 * scale), int(9 * scale)),   # Back to center
                    (int(17 * scale), int(9 * scale))    # Right point
                ]
                draw.polygon(lightning_points, fill=(255, 255, 0), outline=(255, 255, 255))
            
            # Add percentage text
            text = str(percentage)
            try:
                # Try to use a system font
                if os.name == 'nt':  # Windows
                    font = ImageFont.truetype("arial.ttf", int(10 * scale))
                else:  # Linux/Mac
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", int(10 * scale))
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = int(24 * scale)
            
            # Draw text with black outline for visibility
            outline_width = 1
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), text, font=font, fill=(0, 0, 0))
            
            # Draw white text on top
            draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
            
            return img
            
        except Exception as e:
            print(f"Error creating battery icon: {e}")
            # Return a simple fallback icon
            img = Image.new('RGBA', (32, 32), (100, 100, 100, 255))
            return img
    
    def show_notification(self, title, message):
        """Show system notification (cross-platform)"""
        try:
            if os.name == 'nt':  # Windows
                # Try Windows toast notification
                try:
                    from plyer import notification
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=5,
                        app_name="BattMon"
                    )
                except ImportError:
                    print(f"Notification: {title} - {message}")
            else:  # Linux
                os.system(f'notify-send "{title}" "{message}"')
        except Exception as e:
            print(f"Notification error: {e}")
            print(f"{title}: {message}")
    
    def show_battery_status(self, icon, item):
        """Show detailed battery status"""
        info = self.get_battery_info()
        time_info = f" ({info['time_left']} remaining)" if info['time_left'] else ""
        message = f"State: {info['state']}\\nCharge: {info['percentage']}%{time_info}"
        self.show_notification("Battery Status", message)
    
    def show_about(self, icon, item):
        """Show about information"""
        script_path = os.path.abspath(__file__)
        mtime = os.path.getmtime(script_path)
        update_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        about_text = f"BattMon Windows PoC\\n\\nVersion: {VERSION}\\nLast Updated: {update_date}\\n\\nCross-platform battery monitor\\nBuilt with psutil + pystray + Pillow"
        self.show_notification("About BattMon", about_text)
    
    def quit_application(self, icon, item):
        """Quit the application"""
        print("BattMon shutting down...")
        self.running = False
        icon.stop()
    
    def update_battery_icon(self, icon):
        """Update battery icon periodically"""
        while self.running:
            try:
                info = self.get_battery_info()
                percentage = info['percentage']
                
                # Only update if significant change
                if abs(percentage - self.last_percentage) >= 5 or info['state'] != self.last_state:
                    print(f"Battery: {percentage}% {info['state']}")
                    self.last_percentage = percentage
                    self.last_state = info['state']
                
                # Create new icon
                new_image = self.create_battery_icon(percentage, info['is_charging'])
                icon.icon = new_image
                
                # Update tooltip
                tooltip = f"Battery: {percentage}% ({info['state']})"
                if info['time_left']:
                    tooltip += f"\\n{info['time_left']} remaining"
                icon.title = tooltip
                
            except Exception as e:
                print(f"Error updating icon: {e}")
            
            # Wait before next update
            time.sleep(self.update_interval)
    
    def create_menu(self):
        """Create system tray context menu"""
        return pystray.Menu(
            item('Battery Status', self.show_battery_status),
            item('About BattMon', self.show_about),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_application)
        )
    
    def run(self):
        """Run the battery monitor"""
        try:
            # Get initial battery info
            info = self.get_battery_info()
            initial_image = self.create_battery_icon(info['percentage'], info['is_charging'])
            
            # Create system tray icon
            icon = pystray.Icon(
                "BattMon",
                initial_image,
                f"Battery: {info['percentage']}% ({info['state']})",
                self.create_menu()
            )
            
            # Start battery monitoring thread
            monitor_thread = threading.Thread(target=self.update_battery_icon, args=(icon,), daemon=True)
            monitor_thread.start()
            
            print("BattMon is running in system tray. Right-click the icon for options.")
            
            # Run the icon (blocking call)
            icon.run()
            
        except KeyboardInterrupt:
            print("\\nShutdown requested...")
            self.running = False
        except Exception as e:
            print(f"Error running BattMon: {e}")
            self.running = False

def main():
    """Main entry point"""
    print("BattMon Windows 11 Proof-of-Concept")
    print("=" * 40)
    
    # Check if running on Windows
    if os.name == 'nt':
        print("✓ Running on Windows")
    else:
        print("ℹ Running on non-Windows OS (should still work)")
    
    # Check dependencies
    if not HAS_WINDOWS_DEPS:
        print("✗ Missing dependencies")
        print("Install with: pip install psutil pystray pillow plyer")
        return 1
    else:
        print("✓ Dependencies available")
    
    # Check if battery is available
    battery = psutil.sensors_battery()
    if battery is None:
        print("✗ No battery detected (running on desktop?)")
        print("This is normal for desktop computers")
        return 1
    else:
        print(f"✓ Battery detected: {int(battery.percent)}%")
    
    print()
    
    # Create and run monitor
    monitor = CrossPlatformBatteryMonitor()
    return_code = 0
    
    try:
        monitor.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        return_code = 1
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())

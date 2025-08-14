#!/usr/bin/env python3
"""
Test script to generate sample battery icons showing enhanced color coding
"""

import sys
import os

# Add current directory to path to import from battmon_qt6
sys.path.insert(0, '.')

try:
    from battmon_qt6 import BattMonQt6
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtCore import Qt
    QT6_AVAILABLE = True
except ImportError:
    print("PyQt6 or battmon_qt6 not available")
    sys.exit(1)

def generate_sample_icons():
    """Generate sample icons at different battery levels"""
    
    app = QApplication(sys.argv)
    battmon = BattMonQt6()
    
    # Test different battery levels and charging states (4-tier system)
    test_cases = [
        # Red tier (29-0%)
        (15, False, "15_percent_red_discharging"),
        (15, True, "15_percent_red_charging"),
        # Orange tier (49-30%)
        (40, False, "40_percent_orange_discharging"),
        (40, True, "40_percent_orange_charging"),
        # Yellow tier (74-50%)
        (60, False, "60_percent_yellow_discharging"),
        (60, True, "60_percent_yellow_charging"),
        # Green tier (100-75%)
        (85, False, "85_percent_green_discharging"),
        (85, True, "85_percent_green_charging"),
        (100, False, "100_percent_green_full"),
        (100, True, "100_percent_green_charging"),
    ]
    
    print("Generating sample battery icons with enhanced color coding...")
    
    for percentage, is_charging, filename in test_cases:
        # Generate icon at larger size for better visibility
        icon = battmon.create_battery_icon(percentage, is_charging, 64)
        pixmap = icon.pixmap(64, 64)
        
        # Save as PNG file
        output_file = f"sample_icons_{filename}.png"
        if pixmap.save(output_file):
            print(f"✓ Generated: {output_file} ({percentage}%, charging: {is_charging})")
        else:
            print(f"✗ Failed to generate: {output_file}")
    
    print(f"\nSample icons generated! Check the PNG files to see:")
    print("• Enhanced color coding in the upper area (subtle background)")
    print("• Larger, more prominent battery shape")
    print("• Better space utilization")
    print("• Improved percentage text positioning")
    print("• NEW 4-tier color system:")
    print("  - Red: 29-0% (Critical)")
    print("  - Orange: 49-30% (Low)")
    print("  - Yellow: 74-50% (Medium)")
    print("  - Green: 100-75% (Good)")
    print("• Charging indicators with lightning bolts")
    
    app.quit()

if __name__ == "__main__":
    generate_sample_icons()

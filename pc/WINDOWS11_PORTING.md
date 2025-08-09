# BattMon Windows 11 Porting Guide

This document outlines the requirements and changes needed to port BattMon from Linux to Windows 11.

## Current Linux Dependencies That Need Replacement

### 1. System Tray Integration
**Current**: GTK3 StatusIcon (deprecated but functional on Linux)
**Windows Alternative**: 
- **Windows System Tray API** via `win32gui` and `win32api`
- **pystray library** (cross-platform, recommended)
- **plyer** for notifications

### 2. Battery Status Detection
**Current**: ACPI command (`acpi` utility)
**Windows Alternative**:
- **psutil library** (cross-platform, recommended)
- **WMI (Windows Management Instrumentation)** via `wmi` library
- **Windows PowerShell** battery cmdlets

### 3. Graphics and Icon Generation
**Current**: Cairo graphics with GTK3
**Windows Alternative**:
- **Pillow (PIL)** for image manipulation
- **tkinter** for simple graphics (built-in)
- **pygame** for more complex graphics
- **pycairo** (can work on Windows with proper setup)

### 4. GUI Framework
**Current**: GTK3 via gi.repository
**Windows Alternative**:
- **tkinter** (built-in, lightweight)
- **PyQt5/PyQt6** (professional, cross-platform)
- **wxPython** (native look and feel)
- **Kivy** (modern, touch-friendly)

## Recommended Cross-Platform Architecture

### Option 1: Pure Cross-Platform (Recommended)
```python
# Dependencies:
- psutil (battery status)
- pystray (system tray)
- Pillow (icon generation)
- plyer (notifications - optional)
```

### Option 2: Windows-Specific Implementation
```python
# Dependencies:
- pywin32 (Windows API access)
- wmi (Windows Management Instrumentation)
- Pillow (icon generation)
- win10toast (Windows notifications)
```

## Required Changes for Windows 11 Support

### 1. Replace ACPI Battery Detection
```python
# Current Linux approach:
subprocess.check_output('acpi').decode('utf-8')

# Windows replacement using psutil:
import psutil
battery = psutil.sensors_battery()
percentage = battery.percent
is_charging = battery.power_plugged
time_left = battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
```

### 2. Replace GTK System Tray
```python
# Current GTK approach:
from gi.repository import Gtk
self.icon = Gtk.StatusIcon()

# Windows replacement using pystray:
import pystray
from pystray import MenuItem as item
from PIL import Image

def create_menu():
    return pystray.Menu(
        item('Battery Status', show_battery_info),
        item('About', show_about),
        item('Quit', quit_application)
    )

icon = pystray.Icon("BattMon", image, "BattMon", create_menu())
```

### 3. Replace Cairo Graphics
```python
# Current Cairo approach:
import cairo
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)

# Windows replacement using Pillow:
from PIL import Image, ImageDraw, ImageFont

def create_battery_icon(percentage, is_charging=False):
    # Create 24x24 image
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Choose color based on battery level
    if percentage > 75:
        color = (51, 179, 51)  # Green
    elif percentage > 25:
        color = (204, 153, 0)  # Orange
    else:
        color = (204, 51, 51)  # Red
    
    # Draw battery rectangle
    draw.rectangle([(2, 8), (20, 16)], fill=color, outline=(0, 0, 0), width=2)
    # Draw terminal
    draw.rectangle([(20, 10), (22, 14)], fill=(0, 0, 0))
    
    # Add charging indicator
    if is_charging:
        # Draw lightning bolt
        draw.polygon([(10, 4), (14, 7), (12, 7), (16, 10), (12, 7), (14, 7)], 
                    fill=(255, 255, 0), outline=(255, 255, 255))
    
    # Add percentage text
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
    
    text = str(percentage)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position text
    x = (24 - text_width) // 2
    y = 18
    
    # Draw text with outline
    for adj in range(-1, 2):
        for adj2 in range(-1, 2):
            draw.text((x + adj, y + adj2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    return img
```

### 4. Replace Configuration File Handling
```python
# Current approach works on Windows, but path needs adjustment:
# Linux: ~/.battmon
# Windows: %APPDATA%/BattMon/battmon.ini

import os
import configparser

def get_config_path():
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'BattMon')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'battmon.ini')
    else:  # Linux/Unix
        return os.path.expanduser('~/.battmon')
```

## Installation Requirements for Windows 11

### Python Requirements
```bash
# Install Python 3.8+ from python.org or Microsoft Store
pip install psutil pystray pillow plyer configparser
```

### Optional Dependencies
```bash
# For enhanced Windows integration:
pip install pywin32 wmi win10toast

# For professional GUI (if using Qt):
pip install PyQt6
```

## Cross-Platform Implementation Strategy

### Phase 1: Create Windows-Compatible Version
1. **Replace ACPI with psutil** for battery detection
2. **Replace GTK with pystray** for system tray
3. **Replace Cairo with Pillow** for icon generation
4. **Update configuration paths** for Windows
5. **Test on Windows 11**

### Phase 2: Create True Cross-Platform Version
1. **Detect operating system** at runtime
2. **Use appropriate backend** for each OS
3. **Maintain single codebase** with OS-specific modules
4. **Update build/packaging** for both platforms

### Phase 3: Enhanced Windows Integration
1. **Windows-specific features** (e.g., better notifications)
2. **Windows installer** creation
3. **Auto-start integration** with Windows Task Scheduler
4. **Windows Store packaging** (optional)

## Estimated Effort

### Quick Windows Port (Phase 1): 2-3 days
- Replace Linux-specific dependencies
- Basic Windows functionality
- Minimal testing

### Cross-Platform Version (Phase 2): 5-7 days
- OS detection and abstraction
- Comprehensive testing
- Documentation updates

### Professional Windows Release (Phase 3): 10-14 days
- Installer creation
- Advanced Windows features
- Store preparation

## Potential Challenges

### 1. Icon Quality on Windows
- **Issue**: Different DPI settings, scaling
- **Solution**: Generate multiple icon sizes, use vector-like approach

### 2. Windows Permissions
- **Issue**: UAC, admin rights for system tray
- **Solution**: Proper manifest, user-level installation

### 3. Background Execution
- **Issue**: Windows may suspend background apps
- **Solution**: Proper Windows service or keep-alive mechanisms

### 4. Notification System
- **Issue**: Different notification APIs on Windows
- **Solution**: Use plyer or win10toast for Windows notifications

## Next Steps

1. **Create proof-of-concept** Windows version using psutil + pystray
2. **Test basic functionality** on Windows 11
3. **Refactor for cross-platform** architecture
4. **Create Windows installer** and deployment strategy
5. **Update documentation** for Windows users

## File Structure for Cross-Platform Version
```
BattMon/
├── battmon/
│   ├── __init__.py
│   ├── core.py           # Core battery monitoring logic
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── linux_gtk.py  # Linux GTK implementation
│   │   └── windows_tray.py # Windows system tray
│   ├── battery/
│   │   ├── __init__.py
│   │   ├── linux_acpi.py # Linux ACPI implementation
│   │   └── windows_wmi.py # Windows WMI/psutil implementation
│   └── utils/
│       ├── __init__.py
│       ├── config.py     # Cross-platform config handling
│       └── graphics.py   # Cross-platform icon generation
├── battmon.py           # Main entry point
├── requirements.txt     # Python dependencies
├── setup.py            # Installation script
└── windows/
    ├── installer.nsi    # NSIS installer script
    └── battmon.exe      # Compiled executable (optional)
```

Would you like me to start implementing any of these changes or create a proof-of-concept Windows version?

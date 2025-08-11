#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Cross-Platform (bm_x) - Battery Monitor for Linux and Windows
Version 0.5.1 - A Qt6-based cross-platform version with OS detection

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import sys
import subprocess
import os
import platform
import configparser
import datetime
import io

try:
    from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QMessageBox, 
                                 QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
                                 QPushButton)
    from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSize
    from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen, QFont, QAction, QPolygon
    QT6_AVAILABLE = True
except ImportError:
    print("PyQt6 not found. Please install it with:")
    print("  pip install PyQt6")
    if platform.system() == "Linux":
        print("  or")
        print("  sudo apt install python3-pyqt6")
    sys.exit(1)

# Cross-platform constants
VERSION = '0.5.1'
TIMEOUT = 2000  # milliseconds
config = False
config_path = os.path.expanduser('~/.battmon')

# Platform detection
CURRENT_OS = platform.system()
IS_WINDOWS = CURRENT_OS == "Windows"
IS_LINUX = CURRENT_OS == "Linux"
IS_MACOS = CURRENT_OS == "Darwin"

class BatteryWidget(QWidget):
    """A widget to display battery information in a window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"BattMon Cross-Platform - Battery Status ({CURRENT_OS})")
        self.setFixedSize(380, 220)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Set window icon
        icon_pixmap = self.create_window_icon()
        self.setWindowIcon(QIcon(icon_pixmap))
        
        layout = QVBoxLayout()
        
        # Title
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(icon_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        title_label = QLabel("BattMon Cross-Platform")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # OS indicator
        os_label = QLabel(f"Running on {CURRENT_OS}")
        os_font = os_label.font()
        os_font.setPointSize(10)
        os_label.setFont(os_font)
        os_label.setStyleSheet("color: #666666;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(os_label)
        
        # Battery percentage (large display)
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        percentage_font = self.percentage_label.font()
        percentage_font.setPointSize(32)
        percentage_font.setBold(True)
        self.percentage_label.setFont(percentage_font)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(30)
        
        # Status info
        self.state_label = QLabel("Unknown")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        state_font = self.state_label.font()
        state_font.setPointSize(12)
        self.state_label.setFont(state_font)
        
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        
        layout.addLayout(title_layout)
        layout.addWidget(self.percentage_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.state_label)
        layout.addWidget(self.time_label)
        layout.addStretch()
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
        # Apply modern styling with OS-appropriate colors
        if IS_WINDOWS:
            # Windows 11 style
            bg_color = "#f9f9f9"
            accent_color = "#0078d4"
            hover_color = "#106ebe"
            pressed_color = "#005a9e"
        else:
            # Linux/Unix style
            bg_color = "#f0f0f0"
            accent_color = "#007acc"
            hover_color = "#005a9e"
            pressed_color = "#004578"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: #333333;
            }}
            QProgressBar {{
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: {accent_color};
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)
        
    def create_window_icon(self):
        """Create a window icon"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw battery outline
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(100, 200, 100)))
        painter.drawRect(4, 12, 22, 10)
        
        # Draw battery terminal
        painter.fillRect(26, 15, 3, 4, QBrush(QColor(0, 0, 0)))
        
        painter.end()
        return pixmap
        
    def update_battery_info(self, info):
        """Update the widget with battery information"""
        percentage = info['percentage']
        state = info['state']
        time_remaining = info.get('time', '')
        
        self.percentage_label.setText(f"{percentage}%")
        self.state_label.setText(state)
        
        if time_remaining:
            self.time_label.setText(f"Time: {time_remaining}")
        else:
            self.time_label.setText("")
        
        self.progress_bar.setValue(percentage)
        
        # Color-code the progress bar and percentage (4-tier system)
        if percentage >= 75:
            color = "#4CAF50"  # Green (100-75%)
            text_color = "#2E7D32"
        elif percentage >= 50:
            color = "#FFEB3B"  # Yellow (74-50%)
            text_color = "#F57F17"
        elif percentage >= 30:
            color = "#FF9800"  # Orange (49-30%)
            text_color = "#F57C00"
        else:
            color = "#F44336"  # Red (29-0%)
            text_color = "#C62828"
            
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        self.percentage_label.setStyleSheet(f"color: {text_color};")

class BattMonCrossPlatform(QWidget):
    """Main cross-platform BattMon application"""
    
    def __init__(self):
        super().__init__()
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            sys.exit(1)
        
        self.battery_widget = None
        self.last_percentage = None
        self.last_state = None
        
        # Pulsing animation state
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.3  # Fade direction and speed
        self.pulse_timer = None
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip(f"BattMon Cross-Platform - Battery Monitor ({CURRENT_OS})")
        
        # Create context menu
        self.create_tray_menu()
        
        # Set up timer for battery updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_battery)
        self.timer.start(TIMEOUT)
        
        # Initial battery update
        self.update_battery()
        
        # Show tray icon
        self.tray_icon.show()
        
        print(f"BattMon Cross-Platform started on {CURRENT_OS} - system tray icon should be visible")
        print("Left-click to show battery window, Right-click for menu")
        
    def create_tray_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()
        
        # Battery status action (disabled, shows current status)
        self.status_action = QAction(f"Battery: --% (--) [{CURRENT_OS}]", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Show battery window action
        show_action = QAction("Show Battery Window", self)
        show_action.triggered.connect(self.show_battery_window)
        menu.addAction(show_action)
        
        # About action
        about_action = QAction("About BattMon Cross-Platform", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        
        # Connect left-click to show battery window
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left-click
            self.show_battery_window()
    
    def show_battery_window(self):
        """Show the battery information window"""
        if self.battery_widget is None:
            self.battery_widget = BatteryWidget()
        
        # Update with current battery info
        info = self.get_battery_info()
        self.battery_widget.update_battery_info(info)
        
        self.battery_widget.show()
        self.battery_widget.raise_()
        self.battery_widget.activateWindow()
    
    def show_about(self):
        """Show about dialog"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CDT")
        about_text = f"""<h2>BattMon Cross-Platform - Battery Monitor</h2>

<p><b>Version:</b> {VERSION}<br>
<b>Build Date:</b> {current_time}<br>
<b>Qt Version:</b> {QApplication.instance().applicationVersion()}<br>
<b>Framework:</b> PyQt6<br>
<b>Platform:</b> {CURRENT_OS} ({platform.platform()})</p>

<p>A modern Qt6-based cross-platform battery monitoring application featuring:</p>
<ul>
<li>Cross-platform support (Linux, Windows, macOS)</li>
<li>Native OS integration and styling</li>
<li>Clean, native system tray integration</li>
<li>Superior image handling (no external dependencies)</li>
<li>Modern Qt6 widgets and styling</li>
<li>Interactive battery status window with progress bar</li>
<li>Color-coded battery levels (Red/Orange/Yellow/Green)</li>
<li>Dynamic system tray icons with percentage display</li>
<li>Pulsing animation for low battery warnings</li>
<li>Charging indicators and notifications</li>
<li>High DPI display support</li>
</ul>

<p><b>Platform-Specific Features:</b></p>
<ul>
<li><b>Linux:</b> Uses ACPI for battery information</li>
<li><b>Windows:</b> Uses WMI/PowerShell for battery data</li>
<li><b>macOS:</b> Uses system_profiler for battery status</li>
</ul>

<p><b>Key Advantages:</b></p>
<ul>
<li>Single codebase for all platforms</li>
<li>Native look and feel on each OS</li>
<li>No platform-specific dependencies</li>
<li>Superior graphics rendering</li>
<li>Modern UI framework</li>
</ul>

<p>Developed with Python 3 + PyQt6<br>
License: GPL v2+</p>"""
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About BattMon Cross-Platform")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(self.create_battery_icon(75, False).pixmap(64, 64))
        msg_box.exec()
    
    def quit_application(self):
        """Quit the application"""
        print(f"BattMon Cross-Platform shutting down on {CURRENT_OS}...")
        if self.battery_widget:
            self.battery_widget.close()
        QApplication.quit()
    
    def get_battery_info(self):
        """Get battery information using OS-appropriate method"""
        if IS_WINDOWS:
            return self.get_battery_info_windows()
        elif IS_LINUX:
            return self.get_battery_info_linux()
        elif IS_MACOS:
            return self.get_battery_info_macos()
        else:
            return self.get_battery_info_fallback()
    
    def get_battery_info_windows(self):
        """Get battery information on Windows using WMI/PowerShell"""
        try:
            # Try WMI first (requires pywin32 or wmi module)
            try:
                import wmi
                c = wmi.WMI()
                
                for battery in c.Win32_Battery():
                    percentage = battery.EstimatedChargeRemaining or 0
                    
                    # Convert Windows battery status to our format
                    status_map = {
                        1: "Unknown",     # Other
                        2: "Discharging", # Low
                        3: "Discharging", # Warning  
                        4: "Discharging", # Critical
                        5: "Charging",    # Charging
                        6: "Full",        # Charged/Full
                    }
                    state = status_map.get(battery.BatteryStatus, "Unknown")
                    
                    # Get time estimate
                    time_remaining = None
                    if battery.EstimatedRunTime and battery.EstimatedRunTime != 71582788:
                        hours = battery.EstimatedRunTime // 60
                        minutes = battery.EstimatedRunTime % 60
                        time_remaining = f"{hours:02d}:{minutes:02d}"
                    
                    return {
                        'state': state,
                        'percentage': percentage,
                        'time': time_remaining
                    }
                        
            except ImportError:
                # Fallback to PowerShell
                return self.get_battery_info_powershell()
                
        except Exception as e:
            print(f"Error getting Windows battery info: {e}")
            return self.get_battery_info_fallback()
    
    def get_battery_info_powershell(self):
        """Get battery information using PowerShell (Windows fallback)"""
        try:
            # PowerShell command to get battery info
            ps_cmd = """
            Get-WmiObject -Class Win32_Battery | ForEach-Object {
                $percentage = $_.EstimatedChargeRemaining
                $status = switch ($_.BatteryStatus) {
                    1 { "Unknown" }
                    2 { "Discharging" }  
                    3 { "Discharging" }
                    4 { "Discharging" }
                    5 { "Charging" }
                    6 { "Full" }
                    default { "Unknown" }
                }
                $time = if ($_.EstimatedRunTime -and $_.EstimatedRunTime -ne 71582788) {
                    $hours = [math]::Floor($_.EstimatedRunTime / 60)
                    $minutes = $_.EstimatedRunTime % 60
                    "{0:D2}:{1:D2}" -f $hours, $minutes
                } else { "" }
                Write-Output "$percentage,$status,$time"
            }
            """
            
            result = subprocess.check_output(
                ["powershell", "-Command", ps_cmd], 
                shell=True, text=True
            ).strip()
            
            if result:
                parts = result.split(',')
                percentage = int(parts[0]) if parts[0].isdigit() else 0
                state = parts[1] if len(parts) > 1 else "Unknown"
                time_remaining = parts[2] if len(parts) > 2 and parts[2] else None
                
                return {
                    'state': state,
                    'percentage': percentage,
                    'time': time_remaining
                }
                
        except Exception as e:
            print(f"Error getting PowerShell battery info: {e}")
            
        return self.get_battery_info_fallback()
    
    def get_battery_info_linux(self):
        """Get battery information on Linux using ACPI"""
        try:
            text = subprocess.check_output('acpi', shell=True).decode('utf-8').strip()
            if 'Battery' not in text:
                return self.get_battery_info_fallback()
            
            data = text.split(',')
            state = data[0].split(':')[1].strip()
            percentage_str = data[1].strip(' %')
            percentage = int(percentage_str)
            time = None
            
            if len(data) > 2 and state not in ('Full', 'Unknown'):
                time_part = data[2].strip()
                if ' ' in time_part:
                    time = time_part.split(' ')[1]
            
            return {
                'state': state,
                'percentage': percentage,
                'time': time
            }
            
        except Exception as e:
            print(f"Error getting Linux battery info: {e}")
            return self.get_battery_info_fallback()
    
    def get_battery_info_macos(self):
        """Get battery information on macOS using system_profiler"""
        try:
            # Use pmset for battery info on macOS
            result = subprocess.check_output(['pmset', '-g', 'batt'], text=True)
            lines = result.split('\n')
            
            for line in lines:
                if 'InternalBattery' in line or 'Battery' in line:
                    # Parse line like: "InternalBattery-0	100%; charged; 0:00 remaining present: true"
                    parts = line.split('\t')[1] if '\t' in line else line
                    
                    # Extract percentage
                    percentage_match = parts.split(';')[0].strip()
                    percentage = int(percentage_match.replace('%', ''))
                    
                    # Extract state
                    if 'charging' in parts:
                        state = "Charging"
                    elif 'charged' in parts or 'charged;' in parts:
                        state = "Full"
                    elif 'discharging' in parts:
                        state = "Discharging"
                    else:
                        state = "Unknown"
                    
                    # Extract time remaining
                    time_remaining = None
                    if 'remaining' in parts:
                        time_part = parts.split('remaining')[0].split(';')[-1].strip()
                        if ':' in time_part and time_part != '0:00':
                            time_remaining = time_part
                    
                    return {
                        'state': state,
                        'percentage': percentage,
                        'time': time_remaining
                    }
                    
        except Exception as e:
            print(f"Error getting macOS battery info: {e}")
            
        return self.get_battery_info_fallback()
    
    def get_battery_info_fallback(self):
        """Fallback battery info when platform detection fails"""
        return {
            'state': f"Error ({CURRENT_OS})",
            'percentage': 0,
            'time': None
        }
    
    def start_pulse_animation(self, pulse_speed):
        """Start pulsing animation for low battery warnings"""
        if self.pulse_timer:
            self.pulse_timer.stop()
        
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_update)
        self.pulse_timer.start(pulse_speed)  # milliseconds
        
    def stop_pulse_animation(self):
        """Stop pulsing animation"""
        if self.pulse_timer:
            self.pulse_timer.stop()
            self.pulse_timer = None
        self.pulse_opacity = 1.0
        
    def pulse_update(self):
        """Update pulse animation state"""
        # Update opacity for pulsing effect
        self.pulse_opacity += self.pulse_direction
        
        # Reverse direction at boundaries
        if self.pulse_opacity <= 0.3:
            self.pulse_opacity = 0.3
            self.pulse_direction = 0.3  # Fade in
        elif self.pulse_opacity >= 1.0:
            self.pulse_opacity = 1.0
            self.pulse_direction = -0.3  # Fade out
        
        # Update the icon with new opacity
        info = self.get_battery_info()
        is_charging = info['state'] not in ('Discharging', 'Full', 'Unknown')
        icon = self.create_battery_icon(info['percentage'], is_charging, 24, self.pulse_opacity)
        self.tray_icon.setIcon(icon)
    
    def create_battery_icon(self, percentage, is_charging=False, size=24, opacity=1.0):
        """Create a battery icon using Qt's cross-platform image handling"""
        # Create a pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Scale dimensions based on icon size
        scale = size / 24.0
        
        # Choose color based on battery level (4-tier system)
        if percentage >= 75:
            color = QColor(76, 175, 80)   # Green (100-75%)
            bg_color = QColor(200, 255, 200, 180)  # Light green background
        elif percentage >= 50:
            color = QColor(255, 235, 59)  # Yellow (74-50%)
            bg_color = QColor(255, 255, 200, 180)  # Light yellow background
        elif percentage >= 30:
            color = QColor(255, 152, 0)   # Orange (49-30%)
            bg_color = QColor(255, 230, 180, 180)  # Light orange background
        else:
            color = QColor(244, 67, 54)   # Red (29-0%)
            bg_color = QColor(255, 200, 200, 180)  # Light red background
        
        # Use more of the available space - make battery larger and move it higher up
        battery_x = int(1 * scale)
        battery_y = int(2 * scale)  # Move higher up to use more top space
        battery_width = int(20 * scale)  # Make wider
        battery_height = int(12 * scale)  # Make even taller
        terminal_width = int(2 * scale)
        terminal_height = int(8 * scale)  # Make terminal taller to match
        
        # Add a subtle background color fill in upper area to reinforce color coding
        if size >= 20:  # Only for larger icons
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(Qt.GlobalColor.transparent))
            painter.drawRoundedRect(0, 0, size, int(16 * scale), 2, 2)
        
        # Draw battery fill based on percentage
        fill_width = int((battery_width * percentage) / 100)
        if fill_width > 0:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.transparent))
            painter.drawRect(battery_x, battery_y, fill_width, battery_height)
        
        # Draw empty battery area (if not full)
        if fill_width < battery_width:
            empty_color = QColor(240, 240, 240, 200)  # Light gray for empty area
            painter.setBrush(QBrush(empty_color))
            painter.setPen(QPen(Qt.GlobalColor.transparent))
            painter.drawRect(battery_x + fill_width, battery_y, 
                           battery_width - fill_width, battery_height)
        
        # Draw battery outline with thicker line for better visibility
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.setPen(QPen(Qt.GlobalColor.black, max(1, int(2.5 * scale))))
        painter.drawRect(battery_x, battery_y, battery_width, battery_height)
        
        # Draw battery terminal (positive end)
        terminal_x = battery_x + battery_width
        terminal_y = battery_y + int(2 * scale)  # Adjust for taller battery
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawRect(terminal_x, terminal_y, terminal_width, terminal_height)
        
        # Add charging indicator if charging
        if is_charging:
            painter.setBrush(QBrush(QColor(255, 235, 59)))  # Yellow
            painter.setPen(QPen(QColor(255, 235, 59), max(1, int(scale))))
            
            # Draw simplified lightning bolt
            painter.drawLine(int(10 * scale), int(4 * scale), int(14 * scale), int(10 * scale))
            painter.drawLine(int(14 * scale), int(6 * scale), int(10 * scale), int(12 * scale))
            
            # Add white outline for visibility
            painter.setPen(QPen(Qt.GlobalColor.white, max(1, int(2 * scale))))
            painter.drawLine(int(10 * scale), int(4 * scale), int(14 * scale), int(10 * scale))
            painter.drawLine(int(14 * scale), int(6 * scale), int(10 * scale), int(12 * scale))
        
        # Add percentage text in the lower area below the battery
        if size >= 16:  # Only add text for larger icons
            font = QFont("Arial", max(8, int(10 * scale)), QFont.Weight.Bold)
            painter.setFont(font)
            
            text = str(percentage)
            font_metrics = painter.fontMetrics()
            text_rect = font_metrics.boundingRect(text)
            
            # Center text in lower part, below the new battery position
            text_x = (size - text_rect.width()) // 2
            text_y = int(23 * scale)  # Slightly lower to accommodate taller battery
            
            # Draw text with outline for better visibility
            outline_width = max(1, int(3 * scale))
            
            # Black outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        painter.setPen(QPen(Qt.GlobalColor.black))
                        painter.drawText(text_x + dx, text_y + dy, text)
            
            # White text
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(text_x, text_y, text)
        
        painter.end()
        
        # Apply global opacity if specified (for pulsing effect)
        if opacity < 1.0:
            temp_pixmap = QPixmap(pixmap.size())
            temp_pixmap.fill(Qt.GlobalColor.transparent)
            temp_painter = QPainter(temp_pixmap)
            temp_painter.setOpacity(opacity)
            temp_painter.drawPixmap(0, 0, pixmap)
            temp_painter.end()
            return QIcon(temp_pixmap)
        
        return QIcon(pixmap)
    
    def update_battery(self):
        """Update battery status and icon"""
        info = self.get_battery_info()
        percentage = info['percentage']
        state = info['state']
        is_charging = info['state'] not in ('Discharging', 'Full', 'Unknown')
        
        # Check if we should show a notification
        show_message = False
        if self.last_percentage is None:
            self.last_percentage = percentage
            self.last_state = state
            show_message = True
        else:
            percentage_diff = abs(percentage - self.last_percentage)
            state_changed = state != self.last_state
            show_message = percentage_diff >= 5 or state_changed
            
            if show_message:
                self.last_percentage = percentage
                self.last_state = state
        
        # Handle pulse animation based on battery level and charging state
        if not is_charging:  # Only pulse when not charging
            if percentage < 30:  # Red level - fast pulse
                if not self.pulse_timer or not self.pulse_timer.isActive():
                    self.start_pulse_animation(300)  # Fast pulse (300ms)
            elif percentage < 50:  # Orange level - slower pulse
                if not self.pulse_timer or not self.pulse_timer.isActive():
                    self.start_pulse_animation(600)  # Slower pulse (600ms)
            else:  # Green/Yellow levels - no pulse
                if self.pulse_timer and self.pulse_timer.isActive():
                    self.stop_pulse_animation()
        else:  # Stop pulsing when charging
            if self.pulse_timer and self.pulse_timer.isActive():
                self.stop_pulse_animation()
        
        # Update system tray icon (only if not pulsing to avoid conflicts)
        if not self.pulse_timer or not self.pulse_timer.isActive():
            icon = self.create_battery_icon(percentage, is_charging, 24)
            self.tray_icon.setIcon(icon)
        
        # Update tooltip
        tooltip = f"BattMon Cross-Platform ({CURRENT_OS})\\nBattery: {percentage}% ({state})"
        if info.get('time'):
            tooltip += f"\\nTime: {info['time']}"
        self.tray_icon.setToolTip(tooltip)
        
        # Update context menu status
        self.status_action.setText(f"Battery: {percentage}% ({state}) [{CURRENT_OS}]")
        
        # Update battery window if it's open
        if self.battery_widget and self.battery_widget.isVisible():
            self.battery_widget.update_battery_info(info)
        
        # Print status message
        if show_message:
            print(f"[{CURRENT_OS}] Battery: {percentage}% {state}")

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    if IS_LINUX:
        try:
            subprocess.check_output('acpi', shell=True, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: ACPI utility not found. Battery info may not work correctly.")
            print("  To fix: sudo apt install acpi")
    
    elif IS_WINDOWS:
        try:
            # Test PowerShell availability
            subprocess.check_output(
                ["powershell", "-Command", "Write-Output 'test'"], 
                shell=True, stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: PowerShell not found. Battery info may not work correctly.")
            
        # Check for optional WMI module
        try:
            import wmi
            print("WMI module found - will use WMI for battery info")
        except ImportError:
            print("WMI module not found - will use PowerShell fallback")
            print("  For better performance: pip install WMI")
    
    elif IS_MACOS:
        try:
            subprocess.check_output(['pmset', '-g', 'batt'], stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: pmset not found. Battery info may not work correctly.")
    
    return True  # Continue even with warnings

def main():
    """Main function"""
    print(f"BattMon Cross-Platform v{VERSION}")
    print(f"Detected OS: {CURRENT_OS} ({platform.platform()})")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setApplicationName("BattMon Cross-Platform")
    app.setApplicationVersion(VERSION)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    
    # Set application icon
    app_icon = QIcon()
    # Create multiple sizes for better scaling
    for size in [16, 24, 32, 48, 64]:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = size / 24.0
        painter.setBrush(QBrush(QColor(76, 175, 80)))
        painter.setPen(QPen(Qt.GlobalColor.black, max(1, int(2 * scale))))
        painter.drawRect(int(2 * scale), int(8 * scale), int(18 * scale), int(8 * scale))
        painter.fillRect(int(20 * scale), int(10 * scale), int(2 * scale), int(4 * scale), QBrush(Qt.GlobalColor.black))
        painter.end()
        app_icon.addPixmap(pixmap)
    
    app.setWindowIcon(app_icon)
    
    # Create main application
    try:
        battmon = BattMonCrossPlatform()
        
        print(f"BattMon Cross-Platform v{VERSION} initialized successfully on {CURRENT_OS}")
        print("Features:")
        print("• Cross-platform compatibility (Linux, Windows, macOS)")
        print("• Native OS integration and styling")
        print("• Superior Qt6 image handling (no external dependencies)")
        print("• Modern UI with styled progress bars")
        print("• Dynamic system tray icons with percentage display")
        print("• Color-coded battery levels and charging indicators")
        print("• Pulsing animation for low battery warnings")
        print("• Interactive battery status window")
        print("• High DPI display support")
        
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        print(f"\\nBattMon Cross-Platform shutting down on {CURRENT_OS}...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting BattMon Cross-Platform on {CURRENT_OS}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Cross-Platform (bm_x) - Battery Monitor for Linux and Windows
Version 0.5.7 - A Qt6-based cross-platform version with desktop notifications and help system

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
import time
import json

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
VERSION = '0.5.7'
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
        # Track last seen percentage across ticks (for drop detection across state changes)
        self.last_seen_percent = None
        
        # Desktop notifications system
        self.user_profile = self.load_user_profile()
        self.milestone_thresholds = self.user_profile.get('milestone_thresholds', [90, 80, 70, 60, 50, 40, 30, 20, 10])
        self.charging_milestones = self.user_profile.get('charging_milestones', [25, 50, 75, 90, 100])
        self.notifications_enabled = self.user_profile.get('notifications_enabled', True)
        self.last_milestone_triggered = None  # Track last milestone to prevent spam
        self.last_charging_milestone = None  # Track charging milestones separately
        
        # Pulsing animation state
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.3  # Fade direction and speed
        self.pulse_timer = None
        # Enable pulse beeps and 1% step beeps for debugging
        self.beep_with_pulse = True  # Enable/disable beeps with pulsing
        
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
        
        # Show startup notification with milestone thresholds
        self.show_startup_notification()
        
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
        
        # Show notification settings action
        settings_action = QAction("🔔 Show Notification Settings", self)
        settings_action.triggered.connect(self.show_startup_notification)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Help action
        help_action = QAction("📖 Help", self)
        help_action.triggered.connect(self.show_help)
        menu.addAction(help_action)
        
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
    
    def show_help(self):
        """Show help documentation"""
        try:
            # Try to read the HELP.md file
            help_file_path = os.path.join(os.path.dirname(__file__), 'HELP.md')
            
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    help_content = f.read()
                
                # Create a help window/dialog to display the markdown content
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
                from PyQt6.QtCore import QSize
                
                help_dialog = QDialog()
                help_dialog.setWindowTitle("BattMon Cross-Platform - Help")
                help_dialog.setMinimumSize(QSize(800, 600))
                help_dialog.resize(QSize(900, 700))
                
                # Set dialog icon
                help_dialog.setWindowIcon(QIcon(self.create_battery_icon(75, False).pixmap(32, 32)))
                
                layout = QVBoxLayout()
                
                # Text area for help content
                text_edit = QTextEdit()
                text_edit.setPlainText(help_content)
                text_edit.setReadOnly(True)
                
                # Style the text edit for better readability
                text_edit.setStyleSheet("""
                    QTextEdit {
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 10px;
                    }
                """)
                
                # Button layout
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                
                # Close button
                close_button = QPushButton("Close")
                close_button.clicked.connect(help_dialog.accept)
                close_button.setMinimumSize(QSize(100, 30))
                
                button_layout.addWidget(close_button)
                
                layout.addWidget(text_edit)
                layout.addLayout(button_layout)
                
                help_dialog.setLayout(layout)
                help_dialog.exec()
                
            else:
                # Fallback if HELP.md file is not found
                fallback_help = """
BattMon Cross-Platform - Quick Help

=== Basic Usage ===
• Left-click the tray icon to show the battery window
• Right-click the tray icon for the context menu
• The tray icon shows your current battery percentage and status

=== System Tray Icon ===
• Green (75-100%): Good charge level
• Yellow (50-74%): Medium charge level  
• Orange (30-49%): Low charge level
• Red (0-29%): Critical charge level
• Lightning bolt: Charging indicator
• Pulsing animation: Low battery warning

=== Notifications ===
• Desktop notifications at milestone battery levels
• Default discharge alerts: 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10%
• Default charging alerts: 25%, 50%, 75%, 90%, 100%
• Audio alerts with platform-specific sounds

=== Battery Window ===
• Large percentage display
• Color-coded progress bar
• Battery state information
• Time remaining estimates (when available)
• Always stays on top

=== Keyboard Shortcuts ===
• Escape: Close battery window
• Alt+F4 (Windows/Linux): Close battery window
• Cmd+W (macOS): Close battery window

=== Configuration ===
Settings are automatically saved in:
• Linux: ~/.config/battmon/profile.json
• Windows: %APPDATA%\\battmon\\profile.json  
• macOS: ~/Library/Application Support/battmon/profile.json

=== Platform Support ===
• Linux: Uses ACPI for battery information
• Windows: Uses WMI/PowerShell for battery data
• macOS: Uses pmset for battery status

=== Getting Help ===
For more information, visit:
https://github.com/juren53/BattMon

Version: """ + VERSION + """
Platform: """ + CURRENT_OS
                
                msg_box = QMessageBox()
                msg_box.setWindowTitle("BattMon Cross-Platform - Help")
                msg_box.setTextFormat(Qt.TextFormat.PlainText)
                msg_box.setText(fallback_help)
                msg_box.setIconPixmap(self.create_battery_icon(75, False).pixmap(64, 64))
                msg_box.exec()
                
        except Exception as e:
            print(f"Error showing help: {e}")
            # Simple error fallback
            QMessageBox.information(None, "Help", 
                                   f"Help system error. Please visit:\nhttps://github.com/juren53/BattMon\n\nVersion: {VERSION}")
    
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


<p>Developed with Python 3 + PyQt6<br>
License: GPL v2+</p>

<p style="margin-top: 10px; text-align: center;">
📖 <a href="https://github.com/juren53/BattMon" target="_blank">View project on GitHub</a><br>
📋 <a href="https://github.com/juren53/BattMon/blob/main/pc/CHANGELOG.md" target="_blank">View changelog</a>
</p>"""
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About BattMon Cross-Platform")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(self.create_battery_icon(75, False).pixmap(64, 64))
        msg_box.exec()
    
    def quit_application(self):
        """Quit the application"""
        print(f"BattMon Cross-Platform shutting down on {CURRENT_OS}...")
        # Save user profile before quitting
        self.save_user_profile()
        if self.battery_widget:
            self.battery_widget.close()
        QApplication.quit()
    
    def get_config_dir(self):
        """Get the user configuration directory path"""
        if IS_WINDOWS:
            # Windows: Use APPDATA
            config_base = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(config_base, 'BattMon')
        else:
            # Linux/macOS: Use XDG_CONFIG_HOME or ~/.config
            config_base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            return os.path.join(config_base, 'battmon')
    
    def load_user_profile(self):
        """Load user profile from configuration file"""
        config_dir = self.get_config_dir()
        profile_path = os.path.join(config_dir, 'profile.json')
        
        # Default profile settings
        default_profile = {
            'milestone_thresholds': [90, 80, 70, 60, 50, 40, 30, 20, 10],
            'charging_milestones': [25, 50, 75, 90, 100],
            'notifications_enabled': True,
            'notification_timeout': 5000,  # milliseconds
            'play_sound': True,
            'version': VERSION
        }
        
        try:
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                # Merge with defaults to handle missing keys in older profiles
                for key, value in default_profile.items():
                    if key not in profile:
                        profile[key] = value
                print(f"Loaded user profile from: {profile_path}")
                return profile
            else:
                # Create default profile file
                os.makedirs(config_dir, exist_ok=True)
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(default_profile, f, indent=2)
                print(f"Created default user profile at: {profile_path}")
                return default_profile
                
        except Exception as e:
            print(f"Error loading user profile: {e}")
            print("Using default settings")
            return default_profile
    
    def save_user_profile(self):
        """Save current user profile to configuration file"""
        config_dir = self.get_config_dir()
        profile_path = os.path.join(config_dir, 'profile.json')
        
        try:
            # Update profile with current settings
            self.user_profile.update({
                'milestone_thresholds': self.milestone_thresholds,
                'charging_milestones': self.charging_milestones,
                'notifications_enabled': self.notifications_enabled,
                'version': VERSION
            })
            
            os.makedirs(config_dir, exist_ok=True)
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, indent=2)
            print(f"Saved user profile to: {profile_path}")
            
        except Exception as e:
            print(f"Error saving user profile: {e}")
    
    def show_desktop_notification(self, title, message, notification_type='info'):
        """Show cross-platform desktop notification"""
        if not self.notifications_enabled:
            return
        
        try:
            # Use Qt's built-in system tray notification as primary method
            icon_type = QSystemTrayIcon.MessageIcon.Information
            
            if notification_type == 'warning':
                icon_type = QSystemTrayIcon.MessageIcon.Warning
            elif notification_type == 'critical':
                icon_type = QSystemTrayIcon.MessageIcon.Critical
            
            # Show notification with timeout from user profile
            timeout = self.user_profile.get('notification_timeout', 5000)
            self.tray_icon.showMessage(title, message, icon_type, timeout)
            
            # Platform-specific enhancements
            if IS_LINUX:
                self._show_linux_notification(title, message, notification_type)
            elif IS_WINDOWS:
                self._show_windows_notification(title, message, notification_type)
            elif IS_MACOS:
                self._show_macos_notification(title, message, notification_type)
                
        except Exception as e:
            print(f"Error showing desktop notification: {e}")
    
    def _show_linux_notification(self, title, message, notification_type):
        """Show Linux desktop notification using notify-send"""
        try:
            urgency = 'normal'
            if notification_type == 'warning':
                urgency = 'normal'
            elif notification_type == 'critical':
                urgency = 'critical'
            
            # Use notify-send if available
            subprocess.run([
                'notify-send', 
                '--urgency', urgency,
                '--icon', 'battery',
                '--app-name', 'BattMon',
                '--expire-time', str(self.user_profile.get('notification_timeout', 5000)),
                title, 
                message
            ], capture_output=True, timeout=2)
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # notify-send not available, Qt notification is sufficient
            pass
        except Exception as e:
            print(f"Linux notification error: {e}")
    
    def _show_windows_notification(self, title, message, notification_type):
        """Show Windows desktop notification using Windows toast"""
        try:
            # For now, rely on Qt's built-in notification
            # Future enhancement: Use Windows 10+ toast notifications via win10toast
            pass
        except Exception as e:
            print(f"Windows notification error: {e}")
    
    def _show_macos_notification(self, title, message, notification_type):
        """Show macOS desktop notification using osascript"""
        try:
            # Use AppleScript to show native macOS notification
            script = f'''
            display notification "{message}" with title "BattMon" subtitle "{title}"
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=2)
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # osascript not available, Qt notification is sufficient
            pass
        except Exception as e:
            print(f"macOS notification error: {e}")
    
    def check_milestone_notifications(self, percentage, is_charging):
        """Check and trigger milestone notifications"""
        if not self.notifications_enabled:
            return
        
        if is_charging:
            # Check charging milestones (ascending order)
            for milestone in self.charging_milestones:
                if (percentage >= milestone and 
                    (self.last_charging_milestone is None or self.last_charging_milestone < milestone)):
                    
                    # Determine notification type and message
                    if milestone == 100:
                        title = "🔋 Battery Fully Charged"
                        message = "Battery is now 100% charged. You can unplug the charger."
                        notification_type = 'info'
                    elif milestone >= 75:
                        title = "🔋 Battery Almost Full"
                        message = f"Battery charged to {percentage}% ({milestone}% milestone reached)"
                        notification_type = 'info'
                    else:
                        title = "🔋 Battery Charging"
                        message = f"Battery charged to {percentage}% ({milestone}% milestone reached)"
                        notification_type = 'info'
                    
                    self.show_desktop_notification(title, message, notification_type)
                    self.last_charging_milestone = milestone
                    
                    # Play notification sound if enabled
                    if self.user_profile.get('play_sound', True):
                        self.alert_beep(1)
                    
                    break
        else:
            # Check discharge milestones (descending order)
            for milestone in self.milestone_thresholds:
                if (percentage <= milestone and 
                    (self.last_milestone_triggered is None or self.last_milestone_triggered > milestone)):
                    
                    # Determine notification type and message based on battery level
                    if milestone <= 10:
                        title = "🔴 Critical Battery Level"
                        message = f"Battery critically low at {percentage}%! Please charge immediately to avoid data loss."
                        notification_type = 'critical'
                    elif milestone <= 20:
                        title = "🟠 Low Battery Warning"
                        message = f"Battery low at {percentage}%. Please connect charger soon."
                        notification_type = 'warning'
                    elif milestone <= 30:
                        title = "🟡 Battery Getting Low"
                        message = f"Battery at {percentage}%. Consider charging soon."
                        notification_type = 'warning'
                    else:
                        title = "🔋 Battery Milestone"
                        message = f"Battery level: {percentage}% ({milestone}% milestone)"
                        notification_type = 'info'
                    
                    self.show_desktop_notification(title, message, notification_type)
                    self.last_milestone_triggered = milestone
                    
                    # Play notification sound if enabled (more urgent = more beeps)
                    if self.user_profile.get('play_sound', True):
                        if milestone <= 10:
                            self.alert_beep(3)  # Critical - 3 beeps
                        elif milestone <= 20:
                            self.alert_beep(2)  # Low - 2 beeps
                        else:
                            self.alert_beep(1)  # Normal - 1 beep
                    
                    break
            
            # Reset charging milestone when not charging
            if self.last_charging_milestone is not None:
                self.last_charging_milestone = None
    
    def show_startup_notification(self):
        """Show startup notification with configured milestone thresholds"""
        try:
            # Get current battery info for context
            info = self.get_battery_info()
            current_percentage = info.get('percentage', 0)
            current_state = info.get('state', 'Unknown')
            
            # Format milestone thresholds for display
            discharge_thresholds = ', '.join([f"{t}%" for t in sorted(self.milestone_thresholds, reverse=True)])
            charging_thresholds = ', '.join([f"{t}%" for t in sorted(self.charging_milestones)])
            
            # Create informative startup message
            title = "🔋 BattMon Started - Desktop Notifications Active"
            
            message = (
                f"Battery monitoring active! Current: {current_percentage}% ({current_state})\n\n"
                f"📉 Discharge alerts at: {discharge_thresholds}\n"
                f"📈 Charging alerts at: {charging_thresholds}\n\n"
                f"🔔 Notifications: {'Enabled' if self.notifications_enabled else 'Disabled'}\n"
                f"🔊 Sound alerts: {'Enabled' if self.user_profile.get('play_sound', True) else 'Disabled'}"
            )
            
            # Show the startup notification
            self.show_desktop_notification(title, message, 'info')
            
            # Also print to console
            print(f"Desktop notifications configured:")
            print(f"  Discharge milestones: {discharge_thresholds}")
            print(f"  Charging milestones: {charging_thresholds}")
            print(f"  Notifications: {'ON' if self.notifications_enabled else 'OFF'}")
            print(f"  Sound alerts: {'ON' if self.user_profile.get('play_sound', True) else 'OFF'}")
            
        except Exception as e:
            print(f"Error showing startup notification: {e}")
    
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
        
    def beep(self):
        """Make a beep sound using platform-appropriate methods."""
        if not self.beep_with_pulse:
            return
            
        system = platform.system().lower()
        
        if system == 'windows':
            try:
                # Method 1: Use winsound module (built into Python on Windows)
                import winsound
                # Play a beep at 800 Hz for 150ms (shorter for pulse beeps)
                winsound.Beep(800, 150)
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
                # Use sox if available - shorter beep for pulsing
                import subprocess
                subprocess.run(['play', '-n', 'synth', '0.1', 'sine', '800'], 
                              capture_output=True, check=True, timeout=2)
                return
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # Fallback: silent (no beep)
        
    def alert_beep(self, times: int = 1):
        """Cross-platform short beep N times (separate from pulsing)."""
        system = platform.system().lower()
        
        for i in range(max(1, times)):
            if system == 'windows':
                try:
                    import winsound
                    # Use Windows system WAV sounds - these work when beeps are disabled
                    if i == 0:  # First beep - use warning sound
                        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                    else:  # Subsequent beeps - use default
                        winsound.PlaySound("SystemDefault", winsound.SND_ALIAS)
                except Exception:
                    try:
                        # Fallback to MessageBeep
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    except Exception:
                        try:
                            # Fallback to raw beep
                            winsound.Beep(880, 120)
                        except Exception:
                            try:
                                # Final fallback
                                os.system('echo \a')
                            except Exception:
                                pass
            else:
                try:
                    subprocess.run(['play', '-nq', 'synth', '0.12', 'sine', '880'],
                                   capture_output=True, check=True, timeout=2)
                except Exception:
                    try:
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                    except Exception:
                        pass
            time.sleep(0.08)

    def pulse_update(self):
        """Update pulse animation state"""
        # Update opacity for pulsing effect
        self.pulse_opacity += self.pulse_direction
        
        # Reverse direction at boundaries and play beep
        if self.pulse_opacity <= 0.3:
            self.pulse_opacity = 0.3
            self.pulse_direction = 0.3  # Fade in
        elif self.pulse_opacity >= 1.0:
            self.pulse_opacity = 1.0
            self.pulse_direction = -0.3  # Fade out
            # Beep when pulse reaches maximum opacity (most visible)
            self.beep()
        
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
        
        # Check for milestone notifications
        self.check_milestone_notifications(percentage, is_charging)
        
        # Beep when percentage decreases by 1 (or more) since last tick while NOT charging
        # This uses last_seen_percent so it works across state transitions.
        if self.last_seen_percent is not None:
            drop_any = self.last_seen_percent - percentage
            # print(f"[DEBUG] drop-check last_seen={self.last_seen_percent}% current={percentage}% drop_any={drop_any} is_charging={is_charging}")
            if not is_charging and drop_any >= 1:
                if percentage < 30:
                    print("[DEBUG] RED zone 1%+ drop detected -> double beep")
                    self.alert_beep(2)
                elif 30 <= percentage < 50:
                    print("[DEBUG] ORANGE zone 1%+ drop detected -> single beep")
                    self.alert_beep(1)
        else:
            # print(f"[DEBUG] initializing last_seen_percent at {percentage}%")
            pass
        # Update last seen for next tick
        self.last_seen_percent = percentage
        
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
        # Beep once on program load to confirm startup
        try:
            battmon.alert_beep(1)
        except Exception:
            pass
        
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

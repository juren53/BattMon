#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Cross-Platform (bm_x) - Battery Monitor for Linux and Windows
Version 0.5.11 - Enhanced Milestone Tracking with Professional Help System

Change Log at:  https://github.com/juren53/BattMon/blob/main/pc/CHANGELOG.md

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
import re

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
VERSION = '0.5.11'
TIMEOUT = 2000  # milliseconds
config = False
config_path = os.path.expanduser('~/.battmon')

# Platform detection
CURRENT_OS = platform.system()
IS_WINDOWS = CURRENT_OS == "Windows"
IS_LINUX = CURRENT_OS == "Linux"
IS_MACOS = CURRENT_OS == "Darwin"

def show_battery_window_dialog(parent_app):
    """Show battery status in a QMessageBox dialog that matches About window style"""
    try:
        # Get battery information
        info = parent_app.get_battery_info()
        detailed_info = parent_app.get_detailed_battery_info()
        
        percentage = info['percentage']
        state = info['state']
        time_remaining = info.get('time', '')
        is_charging = info.get('state', '').lower() in ('charging', 'full')
        
        # Create prominent battery status display
        charging_indicator = " ⚡" if is_charging else ""
        time_info = f"<br><b>Time Remaining:</b> {time_remaining}" if time_remaining else ""
        
        # Color-code the percentage based on battery level
        if percentage >= 75:
            color = "#27ae60"  # Green
            status_icon = "🔋"
        elif percentage >= 50:
            color = "#f39c12"  # Orange-yellow
            status_icon = "🔋"
        elif percentage >= 30:
            color = "#e67e22"  # Orange
            status_icon = "⚠️"
        else:
            color = "#e74c3c"  # Red
            status_icon = "🚨"
        
        # Build the battery status text in the same format as About window
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        battery_text = f"""<h2>{status_icon} BattMon Cross-Platform - Battery Status</h2>

<p><b>Current Charge:</b> <span style="color: {color}; font-size: 18pt; font-weight: bold;">{percentage}%{charging_indicator}</span><br>
<b>Battery State:</b> {state}{time_info}<br>
<b>Platform:</b> {CURRENT_OS}<br>
<b>Last Updated:</b> {current_time}</p>

<h3>⚡ Battery Details</h3>
<p><b>Technology:</b> {detailed_info.get('technology', 'Unknown')}<br>
<b>Manufacturer:</b> {detailed_info.get('manufacturer', 'Unknown')}<br>
<b>Voltage:</b> {detailed_info.get('voltage', 'Unknown')}<br>
<b>Power Draw:</b> {detailed_info.get('power_draw', 'Unknown')}</p>

<h3>💚 Battery Health</h3>
<p><b>Health Status:</b> {detailed_info.get('health_status', 'Unknown')}<br>
<b>Health Percentage:</b> {detailed_info.get('health_percentage', 0)}%<br>
<b>Design Capacity:</b> {detailed_info.get('design_capacity', 'Unknown')}<br>
<b>Current Capacity:</b> {detailed_info.get('current_capacity', 'Unknown')}<br>
<b>Cycle Count:</b> {detailed_info.get('cycle_count', 'Unknown')}</p>

<p style="margin-top: 10px; text-align: center;">
<b>BattMon Cross-Platform</b> v{VERSION}<br>
<em>Real-time battery monitoring and health tracking</em>
</p>"""
        
        # Create and show the message box in the same style as About
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Battery Status - BattMon Cross-Platform")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(battery_text)
        msg_box.setIconPixmap(parent_app.create_battery_icon(percentage, is_charging, 24).pixmap(64, 64))
        
        # Add a Refresh button alongside OK
        refresh_button = msg_box.addButton("🔄 Refresh", QMessageBox.ButtonRole.ActionRole)
        ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(ok_button)
        
        # Show dialog and handle refresh
        while True:
            result = msg_box.exec()
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == refresh_button:
                # Refresh data and update dialog
                info = parent_app.get_battery_info()
                detailed_info = parent_app.get_detailed_battery_info()
                
                percentage = info['percentage']
                state = info['state']
                time_remaining = info.get('time', '')
                is_charging = info.get('state', '').lower() in ('charging', 'full')
                
                # Update colors and indicators
                charging_indicator = " ⚡" if is_charging else ""
                time_info = f"<br><b>Time Remaining:</b> {time_remaining}" if time_remaining else ""
                
                if percentage >= 75:
                    color = "#27ae60"
                    status_icon = "🔋"
                elif percentage >= 50:
                    color = "#f39c12"
                    status_icon = "🔋"
                elif percentage >= 30:
                    color = "#e67e22"
                    status_icon = "⚠️"
                else:
                    color = "#e74c3c"
                    status_icon = "🚨"
                
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                
                # Update the text
                battery_text = f"""<h2>{status_icon} BattMon Cross-Platform - Battery Status</h2>

<p><b>Current Charge:</b> <span style="color: {color}; font-size: 18pt; font-weight: bold;">{percentage}%{charging_indicator}</span><br>
<b>Battery State:</b> {state}{time_info}<br>
<b>Platform:</b> {CURRENT_OS}<br>
<b>Last Updated:</b> {current_time}</p>

<h3>⚡ Battery Details</h3>
<p><b>Technology:</b> {detailed_info.get('technology', 'Unknown')}<br>
<b>Manufacturer:</b> {detailed_info.get('manufacturer', 'Unknown')}<br>
<b>Voltage:</b> {detailed_info.get('voltage', 'Unknown')}<br>
<b>Power Draw:</b> {detailed_info.get('power_draw', 'Unknown')}</p>

<h3>💚 Battery Health</h3>
<p><b>Health Status:</b> {detailed_info.get('health_status', 'Unknown')}<br>
<b>Health Percentage:</b> {detailed_info.get('health_percentage', 0)}%<br>
<b>Design Capacity:</b> {detailed_info.get('design_capacity', 'Unknown')}<br>
<b>Current Capacity:</b> {detailed_info.get('current_capacity', 'Unknown')}<br>
<b>Cycle Count:</b> {detailed_info.get('cycle_count', 'Unknown')}</p>

<p style="margin-top: 10px; text-align: center;">
<b>BattMon Cross-Platform</b> v{VERSION}<br>
<em>Real-time battery monitoring and health tracking</em>
</p>"""
                
                msg_box.setText(battery_text)
                msg_box.setIconPixmap(parent_app.create_battery_icon(percentage, is_charging, 24).pixmap(64, 64))
                
                print("[DEBUG] Battery status refreshed")
            else:
                break
                
    except Exception as e:
        print(f"[ERROR] Failed to show battery status: {e}")
        # Fallback to simple message
        QMessageBox.information(None, "Battery Status", 
                               f"Battery Status Error\n\nUnable to retrieve battery information.\n\nError: {str(e)}")

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
        
        # Battery Status Window state tracking
        self.battery_status_window = None  # Reference to the currently open battery status window
        
        # Desktop notifications system
        self.user_profile = self.load_user_profile()
        
        # Sleep mode detection - detect when system wakes up from sleep
        self.last_update_time = time.time()
        self.sleep_threshold = self.user_profile.get('sleep_threshold', 300)  # seconds - consider system was asleep if gap > 5 minutes
        self.sleep_notifications_enabled = self.user_profile.get('sleep_notifications_enabled', True)
        self.was_asleep = False
        self.milestone_thresholds = self.user_profile.get('milestone_thresholds', [90, 80, 70, 60, 50, 40, 30, 20, 10])
        self.charging_milestones = self.user_profile.get('charging_milestones', [25, 50, 75, 90, 100])
        self.notifications_enabled = self.user_profile.get('notifications_enabled', True)
        self.last_milestone_triggered = None  # Track last milestone to prevent spam
        self.last_charging_milestone = None  # Track charging milestones separately
        
        # Initialize milestone tracking based on current battery level to prevent startup cascade
        self._initialize_milestone_tracking = True  # Flag to initialize on first update
        
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
        """Toggle the battery information window"""
        # If battery status window is currently open, close it
        if self.battery_status_window is not None:
            try:
                self.battery_status_window.close()
                self.battery_status_window = None
                print("[DEBUG] Battery status window closed")
                return
            except Exception as e:
                print(f"[DEBUG] Error closing battery status window: {e}")
                self.battery_status_window = None
        
        # Otherwise, create and show a new battery status window
        try:
            self.battery_status_window = self.create_battery_status_dialog()
            if self.battery_status_window:
                # Connect the finished signal to clear our reference when dialog is closed
                self.battery_status_window.finished.connect(self.on_battery_window_closed)
                # Show the dialog non-modally (so it doesn't block the main application)
                self.battery_status_window.show()
                print("[DEBUG] Battery status window opened")
        except Exception as e:
            print(f"[DEBUG] Error creating battery status window: {e}")
            self.battery_status_window = None
    
    def create_battery_status_dialog(self):
        """Create a non-modal battery status dialog"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
            from PyQt6.QtCore import QTimer
            
            # Get battery information
            info = self.get_battery_info()
            detailed_info = self.get_detailed_battery_info()
            
            percentage = info['percentage']
            state = info['state']
            time_remaining = info.get('time', '')
            is_charging = info.get('state', '').lower() in ('charging', 'full')
            
            # Create dialog
            dialog = QDialog()
            dialog.setWindowTitle("Battery Status - BattMon Cross-Platform")
            dialog.setModal(False)  # Non-modal so it doesn't block the main application
            dialog.resize(500, 400)
            
            # Set dialog icon
            dialog.setWindowIcon(self.create_battery_icon(percentage, is_charging, 24))
            
            # Create layout
            layout = QVBoxLayout()
            
            # Create main content label
            content_label = QLabel()
            content_label.setTextFormat(Qt.TextFormat.RichText)
            content_label.setWordWrap(True)
            
            # Create the battery status text in HTML format
            charging_indicator = " ⚡" if is_charging else ""
            time_info = f"<br><b>Time Remaining:</b> {time_remaining}" if time_remaining else ""
            
            # Color-code the percentage based on battery level
            if percentage >= 75:
                color = "#27ae60"  # Green
                status_icon = "🔋"
            elif percentage >= 50:
                color = "#f39c12"  # Orange-yellow
                status_icon = "🔋"
            elif percentage >= 30:
                color = "#e67e22"  # Orange
                status_icon = "⚠️"
            else:
                color = "#e74c3c"  # Red
                status_icon = "🚨"
            
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            battery_text = f"""
<h2>{status_icon} BattMon Cross-Platform - Battery Status</h2>

<p><b>Current Charge:</b> <span style="color: {color}; font-size: 18pt; font-weight: bold;">{percentage}%{charging_indicator}</span><br>
<b>Battery State:</b> {state}{time_info}<br>
<b>Platform:</b> {CURRENT_OS}<br>
<b>Last Updated:</b> {current_time}</p>

<h3>⚡ Battery Details</h3>
<p><b>Technology:</b> {detailed_info.get('technology', 'Unknown')}<br>
<b>Manufacturer:</b> {detailed_info.get('manufacturer', 'Unknown')}<br>
<b>Voltage:</b> {detailed_info.get('voltage', 'Unknown')}<br>
<b>Power Draw:</b> {detailed_info.get('power_draw', 'Unknown')}</p>

<h3>💚 Battery Health</h3>
<p><b>Health Status:</b> {detailed_info.get('health_status', 'Unknown')}<br>
<b>Health Percentage:</b> {detailed_info.get('health_percentage', 0)}%<br>
<b>Design Capacity:</b> {detailed_info.get('design_capacity', 'Unknown')}<br>
<b>Current Capacity:</b> {detailed_info.get('current_capacity', 'Unknown')}<br>
<b>Cycle Count:</b> {detailed_info.get('cycle_count', 'Unknown')}</p>

<p style="margin-top: 10px; text-align: center;">
<b>BattMon Cross-Platform</b> v{VERSION}<br>
<em>Real-time battery monitoring and health tracking</em>
</p>
"""
            
            content_label.setText(battery_text)
            layout.addWidget(content_label)
            
            # Create button layout
            button_layout = QHBoxLayout()
            
            # Refresh button
            refresh_button = QPushButton("🔄 Refresh")
            refresh_button.clicked.connect(lambda: self.refresh_battery_dialog(dialog, content_label))
            button_layout.addWidget(refresh_button)
            
            button_layout.addStretch()
            
            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            button_layout.addWidget(close_button)
            
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # Set up auto-refresh timer
            refresh_timer = QTimer()
            refresh_timer.timeout.connect(lambda: self.refresh_battery_dialog(dialog, content_label))
            refresh_timer.start(5000)  # Refresh every 5 seconds
            
            # Store timer reference in dialog so it doesn't get garbage collected
            dialog._refresh_timer = refresh_timer
            
            return dialog
            
        except Exception as e:
            print(f"[ERROR] Failed to create battery status dialog: {e}")
            return None
    
    def refresh_battery_dialog(self, dialog, content_label):
        """Refresh the battery status dialog content"""
        try:
            if dialog is None or not dialog.isVisible():
                return
            
            # Get updated battery information
            info = self.get_battery_info()
            detailed_info = self.get_detailed_battery_info()
            
            percentage = info['percentage']
            state = info['state']
            time_remaining = info.get('time', '')
            is_charging = info.get('state', '').lower() in ('charging', 'full')
            
            # Update dialog icon
            dialog.setWindowIcon(self.create_battery_icon(percentage, is_charging, 24))
            
            # Create updated content
            charging_indicator = " ⚡" if is_charging else ""
            time_info = f"<br><b>Time Remaining:</b> {time_remaining}" if time_remaining else ""
            
            # Color-code the percentage based on battery level
            if percentage >= 75:
                color = "#27ae60"  # Green
                status_icon = "🔋"
            elif percentage >= 50:
                color = "#f39c12"  # Orange-yellow
                status_icon = "🔋"
            elif percentage >= 30:
                color = "#e67e22"  # Orange
                status_icon = "⚠️"
            else:
                color = "#e74c3c"  # Red
                status_icon = "🚨"
            
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            battery_text = f"""
<h2>{status_icon} BattMon Cross-Platform - Battery Status</h2>

<p><b>Current Charge:</b> <span style="color: {color}; font-size: 18pt; font-weight: bold;">{percentage}%{charging_indicator}</span><br>
<b>Battery State:</b> {state}{time_info}<br>
<b>Platform:</b> {CURRENT_OS}<br>
<b>Last Updated:</b> {current_time}</p>

<h3>⚡ Battery Details</h3>
<p><b>Technology:</b> {detailed_info.get('technology', 'Unknown')}<br>
<b>Manufacturer:</b> {detailed_info.get('manufacturer', 'Unknown')}<br>
<b>Voltage:</b> {detailed_info.get('voltage', 'Unknown')}<br>
<b>Power Draw:</b> {detailed_info.get('power_draw', 'Unknown')}</p>

<h3>💚 Battery Health</h3>
<p><b>Health Status:</b> {detailed_info.get('health_status', 'Unknown')}<br>
<b>Health Percentage:</b> {detailed_info.get('health_percentage', 0)}%<br>
<b>Design Capacity:</b> {detailed_info.get('design_capacity', 'Unknown')}<br>
<b>Current Capacity:</b> {detailed_info.get('current_capacity', 'Unknown')}<br>
<b>Cycle Count:</b> {detailed_info.get('cycle_count', 'Unknown')}</p>

<p style="margin-top: 10px; text-align: center;">
<b>BattMon Cross-Platform</b> v{VERSION}<br>
<em>Real-time battery monitoring and health tracking</em>
</p>
"""
            
            # Update the content
            content_label.setText(battery_text)
            print("[DEBUG] Battery status dialog refreshed")
            
        except Exception as e:
            print(f"[ERROR] Failed to refresh battery status dialog: {e}")
    
    def on_battery_window_closed(self):
        """Handle battery status window being closed"""
        print("[DEBUG] Battery status window closed via signal")
        # Stop the refresh timer if it exists
        if self.battery_status_window and hasattr(self.battery_status_window, '_refresh_timer'):
            self.battery_status_window._refresh_timer.stop()
        # Clear the reference
        self.battery_status_window = None
    
    def markdown_to_html(self, markdown_text):
        """Convert Markdown text to HTML using proper markdown library for GitHub-like rendering"""
        try:
            # Try to use the markdown library for proper conversion
            import markdown
            
            # Configure markdown with extensions for better GitHub-like rendering
            md = markdown.Markdown(
                extensions=[
                    'markdown.extensions.tables',     # For table support
                    'markdown.extensions.fenced_code', # For ```code blocks```
                    'markdown.extensions.codehilite',  # For syntax highlighting
                    'markdown.extensions.toc',         # For table of contents
                    'markdown.extensions.nl2br',       # For line break handling
                ],
                extension_configs={
                    'codehilite': {
                        'css_class': 'highlight',
                        'use_pygments': False,  # Use CSS for highlighting instead
                    }
                }
            )
            
            # Convert markdown to HTML
            html_content = md.convert(markdown_text)
            return html_content
            
        except ImportError:
            print("[DEBUG] markdown library not found, using basic converter")
            # Fallback to basic conversion if markdown library is not available
            return self._basic_markdown_to_html(markdown_text)
        except Exception as e:
            print(f"[DEBUG] Error using markdown library: {e}, falling back to basic converter")
            return self._basic_markdown_to_html(markdown_text)
    
    def _basic_markdown_to_html(self, markdown_text):
        """Basic Markdown to HTML converter as fallback"""
        html = markdown_text
        
        # Convert headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Convert bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert italic text
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Convert inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Convert code blocks
        html = re.sub(r'^```.*?\n(.*?)^```', r'<pre><code>\1</code></pre>', html, flags=re.MULTILINE | re.DOTALL)
        
        # Convert bullet points
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                item_text = line.strip()[2:].strip()
                result_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        html = '\n'.join(result_lines)
        
        # Convert table headers and rows
        lines = html.split('\n')
        result_lines = []
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for table header pattern
            if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                if not in_table:
                    result_lines.append('<table>')
                    in_table = True
                
                # Process header
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    result_lines.append('<thead><tr>')
                    for cell in cells:
                        result_lines.append(f'<th>{cell}</th>')
                    result_lines.append('</tr></thead><tbody>')
                
                # Skip the separator line
                i += 2
                continue
            elif in_table and '|' in line and line.strip():
                # Process table row
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    result_lines.append('<tr>')
                    for cell in cells:
                        result_lines.append(f'<td>{cell}</td>')
                    result_lines.append('</tr>')
            else:
                if in_table and not ('|' in line):
                    result_lines.append('</tbody></table>')
                    in_table = False
                result_lines.append(line)
            
            i += 1
        
        if in_table:
            result_lines.append('</tbody></table>')
        
        html = '\n'.join(result_lines)
        
        # Convert links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # Convert paragraphs
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<'):
                html_paragraphs.append(f'<p>{p.replace(chr(10), "<br>")}</p>')
            else:
                html_paragraphs.append(p)
        
        return '\n\n'.join(html_paragraphs)
    
    def show_help(self):
        """Show help documentation"""
        try:
            # Try to read the HELP.md file
            help_file_path = os.path.join(os.path.dirname(__file__), 'HELP.md')
            print(f"[DEBUG] Help file path: {help_file_path}")
            print(f"[DEBUG] File exists: {os.path.exists(help_file_path)}")
            
            if os.path.exists(help_file_path):
                with open(help_file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                print(f"[DEBUG] Content length: {len(markdown_content)} characters")
                
                # Convert Markdown to HTML
                html_content = self.markdown_to_html(markdown_content)
                print(f"[DEBUG] HTML content length: {len(html_content)} characters")
                
                # Create a help window/dialog to display the HTML content
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
                from PyQt6.QtCore import QSize
                
                help_dialog = QDialog()
                help_dialog.setWindowTitle("BattMon Cross-Platform - Help")
                help_dialog.setMinimumSize(QSize(900, 700))
                help_dialog.resize(QSize(1000, 800))
                
                # Set dialog icon
                help_dialog.setWindowIcon(QIcon(self.create_battery_icon(75, False).pixmap(32, 32)))
                
                # Dark theme for the entire dialog to match About window
                help_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #2b2b2b;
                        color: #e0e0e0;
                    }
                    QPushButton {
                        background-color: #404040;
                        color: #e0e0e0;
                        border: 1px solid #606060;
                        border-radius: 4px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                        border-color: #707070;
                    }
                    QPushButton:pressed {
                        background-color: #353535;
                    }
                """)
                
                layout = QVBoxLayout()
                
                # Text area for help content - use QTextBrowser with HTML support
                text_edit = QTextBrowser()
                print(f"[DEBUG] Setting HTML content in QTextBrowser...")
                
                # Enable hyperlinks to be clickable and open in default browser
                text_edit.setOpenExternalLinks(True)
                text_edit.setTextInteractionFlags(
                    Qt.TextInteractionFlag.TextSelectableByMouse | 
                    Qt.TextInteractionFlag.LinksAccessibleByMouse |
                    Qt.TextInteractionFlag.LinksAccessibleByKeyboard
                )
                
                # Apply GitHub-style dark theme CSS with proper margins and spacing
                dark_themed_html = f"""
<style>
    body {{
        background-color: #2b2b2b;
        color: #e8e8e8;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Ubuntu', sans-serif;
        font-size: 16px;
        line-height: 1.7;
        margin: 0;
        padding: 0;
        max-width: none;
    }}
    .content {{
        max-width: 980px;
        margin: 0 auto;
        padding: 45px 60px;
        box-sizing: border-box;
    }}
    @media (max-width: 768px) {{
        .content {{
            padding: 30px 20px;
        }}
    }}
    h1 {{
        color: #ffffff;
        font-size: 32px;
        font-weight: 600;
        margin: 0 0 25px 0;
        border-bottom: 2px solid #444444;
        padding-bottom: 15px;
        line-height: 1.25;
    }}
    h1:first-child {{
        margin-top: 0;
    }}
    h2 {{
        color: #f0f0f0;
        font-size: 24px;
        font-weight: 600;
        margin: 35px 0 20px 0;
        border-bottom: 1px solid #444444;
        padding-bottom: 10px;
        line-height: 1.25;
    }}
    h3 {{
        color: #e0e0e0;
        font-size: 20px;
        font-weight: 600;
        margin: 30px 0 15px 0;
        line-height: 1.25;
    }}
    h4 {{
        color: #d0d0d0;
        font-size: 18px;
        font-weight: 600;
        margin: 25px 0 12px 0;
        line-height: 1.25;
    }}
    p {{
        margin: 0 0 16px 0;
        color: #e8e8e8;
        font-size: 16px;
        line-height: 1.6;
    }}
    a {{
        color: #58a6ff;
        text-decoration: none;
        font-weight: 500;
    }}
    a:hover {{
        color: #79c0ff;
        text-decoration: underline;
    }}
    strong, b {{
        color: #ffffff;
        font-weight: 600;
    }}
    em, i {{
        color: #f0f0f0;
        font-style: italic;
    }}
    code {{
        background-color: rgba(110, 118, 129, 0.4);
        color: #f0f6fc;
        padding: 3px 6px;
        border-radius: 6px;
        font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', monospace;
        font-size: 85%;
        font-weight: 400;
    }}
    pre {{
        background-color: #161b22;
        color: #f0f6fc;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 16px 0;
        font-size: 85%;
        line-height: 1.45;
        border: 1px solid #30363d;
    }}
    pre code {{
        background-color: transparent;
        color: inherit;
        padding: 0;
        border-radius: 0;
        font-size: inherit;
    }}
    ul, ol {{
        margin: 0 0 16px 0;
        padding-left: 32px;
        font-size: 16px;
    }}
    ul ul, ol ol, ul ol, ol ul {{
        margin: 8px 0;
    }}
    li {{
        margin: 4px 0;
        color: #e8e8e8;
        line-height: 1.6;
    }}
    li p {{
        margin: 8px 0;
    }}
    table {{
        border-collapse: collapse;
        border-spacing: 0;
        margin: 16px 0;
        width: 100%;
        background-color: transparent;
        font-size: 14px;
        display: block;
        overflow: auto;
    }}
    table th {{
        background-color: #21262d;
        color: #f0f6fc;
        padding: 12px 13px;
        border: 1px solid #30363d;
        font-weight: 600;
        text-align: left;
    }}
    table td {{
        padding: 12px 13px;
        border: 1px solid #30363d;
        color: #e6edf3;
        background-color: #0d1117;
    }}
    table tr:nth-child(2n) {{
        background-color: #161b22;
    }}
    table tr:nth-child(2n) td {{
        background-color: #161b22;
    }}
    blockquote {{
        background-color: transparent;
        border-left: 4px solid #30363d;
        margin: 16px 0;
        padding: 0 16px;
        color: #8b949e;
        font-style: normal;
        font-size: 16px;
    }}
    blockquote p {{
        color: #8b949e;
    }}
    hr {{
        border: none;
        height: 1px;
        background-color: #30363d;
        margin: 24px 0;
    }}
    .highlight {{
        background-color: #161b22;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #30363d;
        overflow-x: auto;
    }}
</style>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
"""
                
                text_edit.setHtml(dark_themed_html)
                text_edit.setReadOnly(True)
                
                # Dark theme styling for the QTextBrowser widget itself
                text_edit.setStyleSheet("""
                    QTextBrowser {
                        background-color: #2b2b2b;
                        color: #e0e0e0;
                        border: 1px solid #555555;
                        border-radius: 8px;
                        padding: 0px;
                        selection-background-color: #0078d4;
                        selection-color: #ffffff;
                    }
                    QScrollBar:vertical {
                        background-color: #404040;
                        width: 12px;
                        border-radius: 6px;
                        border: none;
                    }
                    QScrollBar::handle:vertical {
                        background-color: #666666;
                        border-radius: 6px;
                        min-height: 20px;
                        border: none;
                    }
                    QScrollBar::handle:vertical:hover {
                        background-color: #777777;
                    }
                    QScrollBar::handle:vertical:pressed {
                        background-color: #555555;
                    }
                    QScrollBar::add-line:vertical,
                    QScrollBar::sub-line:vertical {
                        border: none;
                        background: none;
                    }
                """)
                
                # Button layout
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                
                # Close button
                close_button = QPushButton("Close")
                close_button.clicked.connect(help_dialog.accept)
                close_button.setMinimumSize(QSize(100, 35))
                
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
            'sleep_notifications_enabled': True,  # Enable sleep/wake notifications
            'sleep_threshold': 300,  # seconds - consider system was asleep if gap > 5 minutes
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
        """Show Windows desktop notification using multiple methods"""
        try:
            # Method 1: Use PowerShell to show Windows 10/11 toast notifications (most reliable)
            try:
                # Create PowerShell script for native Windows toast
                # Escape any quotes in the title and message for PowerShell
                title_escaped = title.replace('"', '`"').replace("'", "`'")
                message_escaped = message.replace('"', '`"').replace("'", "`'")
                
                ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null

# Try to use Windows 10+ toast notifications
try {{
    Add-Type -AssemblyName Windows.UI
    Add-Type -AssemblyName Windows.Data
    
    $template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>{title_escaped}</text>
            <text>{message_escaped}</text>
        </binding>
    </visual>
</toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("BattMon")
    $notifier.Show($toast)
    Write-Output "Toast notification sent successfully"
}} catch {{
    # Fallback to balloon tip
    try {{
        Add-Type -AssemblyName System.Windows.Forms
        $balloon = New-Object System.Windows.Forms.NotifyIcon
        $balloon.Icon = [System.Drawing.SystemIcons]::Information
        $balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
        $balloon.BalloonTipTitle = "{title_escaped}"
        $balloon.BalloonTipText = "{message_escaped}"
        $balloon.Visible = $true
        $balloon.ShowBalloonTip(5000)
        Start-Sleep -Seconds 1
        $balloon.Visible = $false
        $balloon.Dispose()
        Write-Output "Balloon notification sent successfully"
    }} catch {{
        # Final fallback - simple message box
        [System.Windows.Forms.MessageBox]::Show("{message_escaped}", "{title_escaped}", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        Write-Output "MessageBox shown successfully"
    }}
}}
'''
                
                # Execute PowerShell script
                result = subprocess.run(
                    ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"[DEBUG] PowerShell notification success: {result.stdout.strip()}")
                    return  # Success
                else:
                    print(f"[DEBUG] PowerShell notification failed: {result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"[DEBUG] PowerShell method failed: {e}")
                pass
            
            # Method 2: Try win10toast library if available
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                
                # Determine icon based on notification type
                icon_path = None  # Will use default app icon
                duration = 10 if notification_type == 'critical' else 5
                
                toaster.show_toast(
                    title=title,
                    msg=message,
                    icon_path=icon_path,
                    duration=duration,
                    threaded=True  # Non-blocking
                )
                print(f"[DEBUG] win10toast notification sent successfully")
                return  # Success - exit function
            except Exception as toast_error:
                print(f"[DEBUG] win10toast failed: {toast_error}")
                pass
            
            # Method 3: Use Windows API via ctypes (fallback)
            try:
                import ctypes
                from ctypes import wintypes
                
                # Show a simple Windows message box as fallback
                MB_OK = 0x0
                MB_ICONINFORMATION = 0x40
                MB_ICONWARNING = 0x30
                MB_ICONERROR = 0x10
                
                icon_type = MB_ICONINFORMATION
                if notification_type == 'warning':
                    icon_type = MB_ICONWARNING
                elif notification_type == 'critical':
                    icon_type = MB_ICONERROR
                
                # Non-blocking message box
                def show_msgbox():
                    ctypes.windll.user32.MessageBoxW(0, message, title, icon_type | MB_OK)
                
                import threading
                threading.Thread(target=show_msgbox, daemon=True).start()
                
            except Exception as fallback_error:
                print(f"[DEBUG] Windows API fallback failed: {fallback_error}")
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
    
    def show_wake_up_notification(self):
        """Show notification when system wakes up from sleep mode"""
        try:
            # Get current battery info after waking up
            info = self.get_battery_info()
            current_percentage = info.get('percentage', 0)
            current_state = info.get('state', 'Unknown')
            is_charging = info.get('state', '').lower() in ('charging', 'full')
            time_remaining = info.get('time', '')
            
            # Get current time for context
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Create wake-up notification with battery status
            title = "💻 System Wake-Up - BattMon Active"
            
            charging_info = " (Charging ⚡)" if is_charging else " (On Battery)"
            time_info = f"\nTime Remaining: {time_remaining}" if time_remaining else ""
            
            message = (
                f"Welcome back! System resumed at {current_time}\n\n"
                f"🔋 Current Battery: {current_percentage}% ({current_state}){charging_info}{time_info}\n\n"
                f"Battery monitoring has resumed automatically."
            )
            
            # Determine notification type based on battery level
            if current_percentage <= 20 and not is_charging:
                notification_type = 'warning'
                title = "⚠️ System Wake-Up - Low Battery Warning"
            elif current_percentage <= 10 and not is_charging:
                notification_type = 'critical'
                title = "🔴 System Wake-Up - Critical Battery Level"
            else:
                notification_type = 'info'
            
            # Show the wake-up notification
            self.show_desktop_notification(title, message, notification_type)
            
            # Play notification sound if enabled
            if self.user_profile.get('play_sound', True):
                if current_percentage <= 10 and not is_charging:
                    self.alert_beep(3)  # Critical - 3 beeps
                elif current_percentage <= 20 and not is_charging:
                    self.alert_beep(2)  # Warning - 2 beeps
                else:
                    self.alert_beep(1)  # Normal wake-up - 1 beep
            
            # Also print to console
            print(f"[WAKE-UP] System resumed at {current_time}")
            print(f"[WAKE-UP] Battery: {current_percentage}% ({current_state}){charging_info}")
            
        except Exception as e:
            print(f"Error showing wake-up notification: {e}")
    
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
    
    def get_detailed_battery_info(self):
        """Get detailed battery information including health data"""
        if IS_WINDOWS:
            return self.get_detailed_battery_info_windows()
        elif IS_LINUX:
            return self.get_detailed_battery_info_linux()
        elif IS_MACOS:
            return self.get_detailed_battery_info_macos()
        else:
            return self.get_detailed_battery_info_fallback()
    
    def get_detailed_battery_info_windows(self):
        """Get detailed battery information on Windows"""
        detailed_info = {
            'voltage': '--',
            'temperature': '--',
            'technology': '--',
            'manufacturer': '--',
            'health_status': 'Unknown',
            'health_percentage': 0,
            'design_capacity': '--',
            'current_capacity': '--',
            'cycle_count': '--',
            'power_draw': '--'
        }
        
        try:
            # Try WMI for detailed info
            try:
                import wmi
                c = wmi.WMI()
                
                # Get battery information
                for battery in c.Win32_Battery():
                    if battery.Chemistry:
                        chemistry_map = {
                            1: "Other",
                            2: "Unknown",
                            3: "Lead Acid",
                            4: "Nickel Cadmium",
                            5: "Nickel Metal Hydride",
                            6: "Lithium Ion",
                            7: "Zinc Air",
                            8: "Lithium Polymer"
                        }
                        detailed_info['technology'] = chemistry_map.get(battery.Chemistry, "Unknown")
                    
                    if battery.DeviceID:
                        detailed_info['manufacturer'] = battery.DeviceID or "Unknown"
                    
                    if battery.DesignCapacity and battery.FullChargeCapacity:
                        design = battery.DesignCapacity
                        current = battery.FullChargeCapacity
                        detailed_info['design_capacity'] = f"{design} mWh"
                        detailed_info['current_capacity'] = f"{current} mWh"
                        
                        # Calculate health percentage
                        health_percentage = int((current / design) * 100) if design > 0 else 0
                        detailed_info['health_percentage'] = max(0, min(100, health_percentage))
                    
                    break
                
                # Try to get additional info from Win32_SystemBattery
                for battery in c.Win32_SystemBattery():
                    if hasattr(battery, 'BatteryStatus'):
                        if battery.BatteryStatus == 1:
                            detailed_info['health_status'] = "Good"
                        elif battery.BatteryStatus == 2:
                            detailed_info['health_status'] = "Weak"
                        else:
                            detailed_info['health_status'] = "Unknown"
                    break
                    
            except ImportError:
                # Fallback to PowerShell
                pass
                
        except Exception as e:
            print(f"Error getting detailed Windows battery info: {e}")
            
        return detailed_info
    
    def get_detailed_battery_info_linux(self):
        """Get detailed battery information on Linux using /sys/class/power_supply"""
        detailed_info = {
            'voltage': '--',
            'temperature': '--',
            'technology': '--',
            'manufacturer': '--',
            'health_status': 'Unknown',
            'health_percentage': 0,
            'design_capacity': '--',
            'current_capacity': '--',
            'cycle_count': '--',
            'power_draw': '--'
        }
        
        try:
            # Find battery path
            battery_path = None
            for bat_name in os.listdir('/sys/class/power_supply/'):
                if bat_name.startswith('BAT'):
                    battery_path = f'/sys/class/power_supply/{bat_name}'
                    break
            
            if battery_path:
                # Read various battery properties
                try:
                    # Voltage (in microvolts)
                    voltage_file = os.path.join(battery_path, 'voltage_now')
                    if os.path.exists(voltage_file):
                        with open(voltage_file, 'r') as f:
                            voltage_uv = int(f.read().strip())
                            voltage_v = voltage_uv / 1000000.0
                            detailed_info['voltage'] = f"{voltage_v:.2f} V"
                except:
                    pass
                
                try:
                    # Technology
                    tech_file = os.path.join(battery_path, 'technology')
                    if os.path.exists(tech_file):
                        with open(tech_file, 'r') as f:
                            detailed_info['technology'] = f.read().strip()
                except:
                    pass
                
                try:
                    # Manufacturer
                    mfg_file = os.path.join(battery_path, 'manufacturer')
                    if os.path.exists(mfg_file):
                        with open(mfg_file, 'r') as f:
                            detailed_info['manufacturer'] = f.read().strip()
                except:
                    pass
                
                try:
                    # Capacity information
                    design_file = os.path.join(battery_path, 'energy_full_design')
                    current_file = os.path.join(battery_path, 'energy_full')
                    
                    if os.path.exists(design_file) and os.path.exists(current_file):
                        with open(design_file, 'r') as f:
                            design_uwh = int(f.read().strip())
                            design_wh = design_uwh / 1000000.0
                            detailed_info['design_capacity'] = f"{design_wh:.2f} Wh"
                        
                        with open(current_file, 'r') as f:
                            current_uwh = int(f.read().strip())
                            current_wh = current_uwh / 1000000.0
                            detailed_info['current_capacity'] = f"{current_wh:.2f} Wh"
                            
                            # Calculate health percentage
                            health_percentage = int((current_wh / design_wh) * 100) if design_wh > 0 else 0
                            detailed_info['health_percentage'] = max(0, min(100, health_percentage))
                except:
                    pass
                
                try:
                    # Cycle count
                    cycle_file = os.path.join(battery_path, 'cycle_count')
                    if os.path.exists(cycle_file):
                        with open(cycle_file, 'r') as f:
                            detailed_info['cycle_count'] = f.read().strip()
                except:
                    pass
                
                try:
                    # Power draw (in microwatts)
                    power_file = os.path.join(battery_path, 'power_now')
                    if os.path.exists(power_file):
                        with open(power_file, 'r') as f:
                            power_uw = int(f.read().strip())
                            power_w = power_uw / 1000000.0
                            detailed_info['power_draw'] = f"{power_w:.2f} W"
                except:
                    pass
                
                try:
                    # Health status
                    health_file = os.path.join(battery_path, 'health')
                    if os.path.exists(health_file):
                        with open(health_file, 'r') as f:
                            detailed_info['health_status'] = f.read().strip().title()
                except:
                    pass
                    
        except Exception as e:
            print(f"Error getting detailed Linux battery info: {e}")
            
        return detailed_info
    
    def get_detailed_battery_info_macos(self):
        """Get detailed battery information on macOS using system_profiler"""
        detailed_info = {
            'voltage': '--',
            'temperature': '--',
            'technology': '--',
            'manufacturer': '--',
            'health_status': 'Unknown',
            'health_percentage': 0,
            'design_capacity': '--',
            'current_capacity': '--',
            'cycle_count': '--',
            'power_draw': '--'
        }
        
        try:
            # Use system_profiler to get detailed battery info
            result = subprocess.check_output(
                ['system_profiler', 'SPPowerDataType', '-xml'],
                text=True, timeout=10
            )
            
            # Parse the XML output (simplified parsing)
            if 'Health Information' in result:
                # Extract cycle count
                if 'Cycle Count' in result:
                    import re
                    cycle_match = re.search(r'Cycle Count</key>\s*<integer>(\d+)</integer>', result)
                    if cycle_match:
                        detailed_info['cycle_count'] = cycle_match.group(1)
                
                # Extract condition
                if 'Condition' in result:
                    condition_match = re.search(r'Condition</key>\s*<string>([^<]+)</string>', result)
                    if condition_match:
                        detailed_info['health_status'] = condition_match.group(1)
                        
                        # Map condition to health percentage
                        condition = condition_match.group(1).lower()
                        if 'normal' in condition:
                            detailed_info['health_percentage'] = 90
                        elif 'good' in condition:
                            detailed_info['health_percentage'] = 75
                        elif 'fair' in condition:
                            detailed_info['health_percentage'] = 50
                        else:
                            detailed_info['health_percentage'] = 25
            
            # Get additional info from ioreg
            try:
                ioreg_result = subprocess.check_output(
                    ['ioreg', '-rc', 'AppleSmartBattery'],
                    text=True, timeout=5
                )
                
                if 'DesignCapacity' in ioreg_result:
                    design_match = re.search(r'"DesignCapacity"\s*=\s*(\d+)', ioreg_result)
                    if design_match:
                        design_mah = int(design_match.group(1))
                        detailed_info['design_capacity'] = f"{design_mah} mAh"
                
                if 'MaxCapacity' in ioreg_result:
                    max_match = re.search(r'"MaxCapacity"\s*=\s*(\d+)', ioreg_result)
                    if max_match:
                        max_mah = int(max_match.group(1))
                        detailed_info['current_capacity'] = f"{max_mah} mAh"
                        
                        # Recalculate health percentage from actual values
                        if 'design_capacity' in detailed_info and design_mah > 0:
                            health_percentage = int((max_mah / design_mah) * 100)
                            detailed_info['health_percentage'] = max(0, min(100, health_percentage))
                
                if 'Voltage' in ioreg_result:
                    voltage_match = re.search(r'"Voltage"\s*=\s*(\d+)', ioreg_result)
                    if voltage_match:
                        voltage_mv = int(voltage_match.group(1))
                        voltage_v = voltage_mv / 1000.0
                        detailed_info['voltage'] = f"{voltage_v:.2f} V"
                        
            except:
                pass
                
        except Exception as e:
            print(f"Error getting detailed macOS battery info: {e}")
            
        return detailed_info
    
    def get_detailed_battery_info_fallback(self):
        """Fallback detailed battery info"""
        return {
            'voltage': '--',
            'temperature': '--',
            'technology': '--',
            'manufacturer': '--',
            'health_status': 'Unknown',
            'health_percentage': 0,
            'design_capacity': '--',
            'current_capacity': '--',
            'cycle_count': '--',
            'power_draw': '--'
        }
    
    def get_battery_info_linux(self):
        """Get battery information on Linux using ACPI"""
        try:
            text = subprocess.check_output('acpi', shell=True).decode('utf-8').strip()
            if 'Battery' not in text:
                return self.get_battery_info_fallback()
            
            # Handle different acpi output formats
            # Format 1: "Battery 0: Full, 100%"
            # Format 2: "100%\nBattery 1: Discharging"
            # Format 3: Multiple lines with different formats
            
            # Split by lines first to handle multi-line output
            lines = text.split('\n')
            
            # Process each line to find battery information
            for line in lines:
                line = line.strip()
                if not line or 'Battery' not in line:
                    continue
                
                # Try comma-separated format first (Format 1)
                if ',' in line:
                    try:
                        data = line.split(',')
                        if len(data) >= 2:
                            # Extract state from first part
                            if ':' in data[0]:
                                state = data[0].split(':')[1].strip()
                            else:
                                state = "Unknown"
                            
                            # Extract percentage from second part
                            percentage_part = data[1].strip()
                            # Extract percentage number (handle various formats like " 100%", "100%", etc.)
                            import re
                            percentage_match = re.search(r'(\d+)%', percentage_part)
                            if percentage_match:
                                percentage = int(percentage_match.group(1))
                            else:
                                continue  # Skip this line if no percentage found
                            
                            # Extract time remaining if available
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
                        pass  # Continue to next parsing method
                        continue
                
                # Try colon-separated format (Format 2 and variations)
                if ':' in line:
                    try:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            # First part should contain "Battery X"
                            # Second part should contain state and possibly percentage
                            battery_part = parts[0].strip()
                            info_part = ':'.join(parts[1:]).strip()  # Join back in case of multiple colons
                            
                            # Extract percentage using regex
                            import re
                            percentage_match = re.search(r'(\d+)%', info_part)
                            if percentage_match:
                                percentage = int(percentage_match.group(1))
                            else:
                                # Maybe percentage is in the battery part or elsewhere
                                percentage_match = re.search(r'(\d+)%', line)
                                if percentage_match:
                                    percentage = int(percentage_match.group(1))
                                else:
                                    continue  # Skip if no percentage found
                            
                            # Extract state (check 'discharging' before 'charging' since 'discharging' contains 'charging')
                            state = "Unknown"
                            if 'discharging' in info_part.lower():
                                state = "Discharging"
                            elif 'charging' in info_part.lower():
                                state = "Charging"
                            elif 'full' in info_part.lower() or 'charged' in info_part.lower():
                                state = "Full"
                            elif 'unknown' in info_part.lower():
                                state = "Unknown"
                            
                            # Extract time remaining
                            time = None
                            time_match = re.search(r'(\d{2}:\d{2})', info_part)
                            if time_match:
                                time = time_match.group(1)
                            
                            return {
                                'state': state,
                                'percentage': percentage,
                                'time': time
                            }
                    except Exception as e:
                        pass  # Continue to next parsing method
                        continue
            
            # If we get here, no valid battery info was found
            return self.get_battery_info_fallback()
            
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
        current_time = time.time()
        
        # Sleep mode detection - check if there's been a significant time gap
        time_gap = current_time - self.last_update_time
        
        # If gap is greater than our threshold, system likely woke from sleep
        if (self.sleep_notifications_enabled and 
            time_gap > self.sleep_threshold and 
            not self.was_asleep):
            print(f"[SLEEP] Detected sleep mode wake-up. Time gap: {time_gap:.1f} seconds")
            self.was_asleep = True
            # Show wake-up notification
            self.show_wake_up_notification()
        elif time_gap <= self.sleep_threshold:
            # Normal update interval - reset sleep flag if it was set
            self.was_asleep = False
        
        # Update the last update time for next detection
        self.last_update_time = current_time
        
        info = self.get_battery_info()
        percentage = info['percentage']
        state = info['state']
        is_charging = info['state'] not in ('Discharging', 'Full', 'Unknown')
        
        # Initialize milestone tracking on first update to prevent startup cascade
        if hasattr(self, '_initialize_milestone_tracking') and self._initialize_milestone_tracking:
            print(f"[INIT] Initializing milestone tracking at {percentage}% to prevent startup cascade")
            
            # For discharge milestones, set the last triggered to the nearest milestone at or below current level
            # This prevents notifications for milestones that are at or below the current level
            if not is_charging:
                # Find the highest milestone that is <= current percentage
                for milestone in sorted(self.milestone_thresholds, reverse=True):
                    if milestone <= percentage:
                        self.last_milestone_triggered = milestone
                        print(f"[INIT] Set last_milestone_triggered to {milestone}% (current: {percentage}%)")
                        break
                # If no milestone is <= current percentage, set to None (all milestones are above current level)
                if self.last_milestone_triggered is None:
                    print(f"[INIT] All discharge milestones are above {percentage}%, leaving last_milestone_triggered as None")
            
            # For charging milestones, set to the highest milestone at or below current level
            if is_charging:
                # Find the highest milestone that is <= current percentage
                for milestone in sorted(self.charging_milestones, reverse=True):
                    if milestone <= percentage:
                        self.last_charging_milestone = milestone
                        print(f"[INIT] Set last_charging_milestone to {milestone}% (current: {percentage}%)")
                        break
                # If no milestone is <= current percentage, set to None (all milestones are above current level)
                if self.last_charging_milestone is None:
                    print(f"[INIT] All charging milestones are above {percentage}%, leaving last_charging_milestone as None")
            
            # Remove the initialization flag
            delattr(self, '_initialize_milestone_tracking')
        
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
        
        # Battery window now uses dialog style - no persistent window to update
        
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

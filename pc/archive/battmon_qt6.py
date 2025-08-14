#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Qt6 - Battery Monitor for Linux
Version 0.4.0 - A Qt6-based version with superior image handling and modern UI

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import sys
import subprocess
import os
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
    print("  or")
    print("  sudo apt install python3-pyqt6")
    sys.exit(1)

ACPI_CMD = 'acpi'
TIMEOUT = 2000  # milliseconds
VERSION = '0.4.2'
config = False
config_path = os.path.expanduser('~/.battmon')

class BatteryWidget(QWidget):
    """A widget to display battery information in a window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BattMon Qt6 - Battery Status")
        self.setFixedSize(350, 200)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Set window icon
        icon_pixmap = self.create_window_icon()
        self.setWindowIcon(QIcon(icon_pixmap))
        
        layout = QVBoxLayout()
        
        # Title
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(icon_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        title_label = QLabel("BattMon Qt6")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
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
        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
            QPushButton {
                background-color: #007acc;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
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

class BattMonQt6(QWidget):
    """Main BattMon Qt6 application"""
    
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
        self.tray_icon.setToolTip("BattMon Qt6 - Battery Monitor")
        
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
        
        print("BattMon Qt6 started - system tray icon should be visible")
        print("Left-click to show battery window, Right-click for menu")
        
    def create_tray_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()
        
        # Battery status action (disabled, shows current status)
        self.status_action = QAction("Battery: --% (--)", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Show battery window action
        show_action = QAction("Show Battery Window", self)
        show_action.triggered.connect(self.show_battery_window)
        menu.addAction(show_action)
        
        # About action
        about_action = QAction("About BattMon Qt6", self)
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
        about_text = f"""<h2>BattMon Qt6 - Battery Monitor for Linux</h2>

<p><b>Version:</b> {VERSION}<br>
<b>Qt Version:</b> {QApplication.instance().applicationVersion()}<br>
<b>Framework:</b> PyQt6</p>

<p>A modern Qt6-based battery monitoring application featuring:</p>
<ul>
<li>Clean, native system tray integration</li>
<li>Superior image handling (no GdkPixbuf dependencies)</li>
<li>Modern Qt6 widgets and styling</li>
<li>Interactive battery status window with progress bar</li>
<li>Color-coded battery levels (Red/Orange/Green)</li>
<li>Dynamic system tray icons with percentage display</li>
<li>Charging indicators and system notifications</li>
<li>Cross-platform compatibility</li>
</ul>

<p><b>Key Advantages over GTK version:</b></p>
<ul>
<li>No GdkPixbuf PNG loading issues</li>
<li>Better cross-platform support</li>
<li>More modern UI framework</li>
<li>Superior graphics rendering</li>
<li>Better HiDPI display support</li>
</ul>

<p>Developed with Python 3 + PyQt6<br>
License: GPL v2+</p>"""
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About BattMon Qt6")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(self.create_battery_icon(75, False).pixmap(64, 64))
        msg_box.exec()
    
    def quit_application(self):
        """Quit the application"""
        print("BattMon Qt6 shutting down...")
        if self.battery_widget:
            self.battery_widget.close()
        QApplication.quit()
    
    def get_battery_info(self):
        """Get battery information from acpi"""
        try:
            text = subprocess.check_output(ACPI_CMD, shell=True).decode('utf-8').strip()
            if 'Battery' not in text:
                return {
                    'state': "Unknown",
                    'percentage': 0,
                    'time': None
                }
            
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
            print(f"Error getting battery info: {e}")
            return {
                'state': "Error",
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
        """Create a battery icon using Qt's superior image handling with better space utilization"""
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
        
        # Use more of the available space - make battery larger and move it up
        battery_x = int(1 * scale)
        battery_y = int(6 * scale)  # Move up to use upper space
        battery_width = int(20 * scale)  # Make wider
        battery_height = int(10 * scale)  # Make taller
        terminal_width = int(2 * scale)
        terminal_height = int(6 * scale)  # Make terminal taller too
        
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
        terminal_y = battery_y + int(2 * scale)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawRect(terminal_x, terminal_y, terminal_width, terminal_height)
        
        # Add charging indicator if charging
        if is_charging:
            painter.setBrush(QBrush(QColor(255, 235, 59)))  # Yellow
            painter.setPen(QPen(QColor(255, 235, 59), max(1, int(scale))))
            
            # Create lightning bolt polygon
            lightning_points = [
                (int(10 * scale), int(4 * scale)),   # Top
                (int(14 * scale), int(8 * scale)),   # Middle right
                (int(12 * scale), int(8 * scale)),   # Middle left  
                (int(16 * scale), int(12 * scale)),  # Bottom right
                (int(12 * scale), int(8 * scale)),   # Back to middle
                (int(14 * scale), int(8 * scale)),   # Complete shape
            ]
            
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
        is_charging = state not in ('Discharging', 'Full', 'Unknown')
        
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
        tooltip = f"BattMon Qt6\nBattery: {percentage}% ({state})"
        if info.get('time'):
            tooltip += f"\nTime: {info['time']}"
        self.tray_icon.setToolTip(tooltip)
        
        # Update context menu status
        self.status_action.setText(f"Battery: {percentage}% ({state})")
        
        # Update battery window if it's open
        if self.battery_widget and self.battery_widget.isVisible():
            self.battery_widget.update_battery_info(info)
        
        # Print status message
        if show_message:
            print(f"Battery: {percentage}% {state}")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        # Check if acpi is available
        subprocess.check_output(ACPI_CMD, shell=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ACPI utility not found. Please install acpi:")
        print("  sudo apt install acpi")
        return False
    
    try:
        # Check if PyQt6 is available (already done at import)
        pass
    except ImportError:
        print("Error: PyQt6 not found. Please install PyQt6:")
        print("  pip install PyQt6")
        print("  or")  
        print("  sudo apt install python3-pyqt6")
        return False
        
    return True

def main():
    """Main function"""
    if not check_dependencies():
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setApplicationName("BattMon Qt6")
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
        battmon = BattMonQt6()
        
        print(f"BattMon Qt6 v{VERSION} initialized successfully")
        print("Features:")
        print("• Superior Qt6 image handling (no GdkPixbuf issues)")
        print("• Modern UI with styled progress bars")
        print("• Dynamic system tray icons with percentage display")
        print("• Color-coded battery levels and charging indicators")
        print("• Interactive battery status window")
        
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        print("\nBattMon Qt6 shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting BattMon Qt6: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

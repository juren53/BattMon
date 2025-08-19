#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BattMon Profile Editor - Standalone GUI for editing JSON profile settings
Version 0.5.12 - Profile Editor Module

This standalone module provides a GUI interface for editing BattMon profile settings
stored in the JSON configuration file.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import sys
import os
import json
import platform

try:
    from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QPushButton, QLineEdit, QCheckBox, 
                                 QSpinBox, QGroupBox, QFormLayout, QScrollArea,
                                 QWidget, QMessageBox, QFrame, QTextEdit)
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QBrush
    QT6_AVAILABLE = True
except ImportError:
    print("PyQt6 not found. Please install it with:")
    print("  pip install PyQt6")
    if platform.system() == "Linux":
        print("  or")
        print("  sudo apt install python3-pyqt6")
    sys.exit(1)

VERSION = '0.5.12'
CURRENT_OS = platform.system()
IS_WINDOWS = CURRENT_OS == "Windows"

class ProfileEditor(QDialog):
    """Profile Editor GUI for BattMon settings"""
    
    def __init__(self, parent=None, profile_path=None):
        super().__init__(parent)
        self.profile_path = profile_path or self.get_default_profile_path()
        self.profile_data = {}
        
        self.init_ui()
        self.load_profile()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"🔧 BattMon Profile Editor - {VERSION}")
        self.setMinimumSize(QSize(600, 700))
        self.resize(QSize(650, 750))
        
        # Set window icon (create a simple settings icon)
        self.setWindowIcon(self.create_settings_icon())
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #363636;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
                background-color: #363636;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: #404040;
                color: #ffffff;
                border: 2px solid #606060;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #0078d4;
                background-color: #454545;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #606060;
                background-color: #404040;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QScrollArea {
                border: 1px solid #555555;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QFrame {
                border: none;
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("🔧 BattMon Profile Editor")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Profile path info
        path_label = QLabel(f"📁 Profile Path: {self.profile_path}")
        path_label.setStyleSheet("color: #b0b0b0; font-size: 12px; margin-bottom: 15px;")
        path_label.setWordWrap(True)
        main_layout.addWidget(path_label)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Notification Settings Group
        self.create_notification_settings_group(scroll_layout)
        
        # Battery Alert Thresholds Group
        self.create_threshold_settings_group(scroll_layout)
        
        # Advanced Settings Group
        self.create_advanced_settings_group(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Reset to defaults button
        reset_button = QPushButton("🔄 Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setStyleSheet("background-color: #d83b01; color: white;")
        reset_button.setToolTip("Reset all settings to default values")
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("background-color: #666666; color: white;")
        button_layout.addWidget(cancel_button)
        
        # Save button
        save_button = QPushButton("💾 Save Profile")
        save_button.clicked.connect(self.save_profile)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px; margin-top: 5px;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        
    def create_notification_settings_group(self, parent_layout):
        """Create notification settings group"""
        group = QGroupBox("🔔 Notification Settings")
        layout = QFormLayout()
        layout.setSpacing(12)
        
        # Notifications enabled
        self.notifications_enabled = QCheckBox()
        self.notifications_enabled.setToolTip("Enable/disable all desktop notifications")
        layout.addRow("Enable Notifications:", self.notifications_enabled)
        
        # Play sound
        self.play_sound = QCheckBox()
        self.play_sound.setToolTip("Play audio alerts with notifications")
        layout.addRow("Play Sound Alerts:", self.play_sound)
        
        # Notification timeout
        self.notification_timeout = QSpinBox()
        self.notification_timeout.setRange(1000, 30000)
        self.notification_timeout.setSuffix(" ms")
        self.notification_timeout.setSingleStep(500)
        self.notification_timeout.setToolTip("How long notifications stay visible (milliseconds)")
        layout.addRow("Notification Duration:", self.notification_timeout)
        
        # Sleep notifications
        self.sleep_notifications_enabled = QCheckBox()
        self.sleep_notifications_enabled.setToolTip("Show notifications when system wakes from sleep")
        layout.addRow("Sleep/Wake Notifications:", self.sleep_notifications_enabled)
        
        # Sleep threshold
        self.sleep_threshold = QSpinBox()
        self.sleep_threshold.setRange(60, 3600)
        self.sleep_threshold.setSuffix(" seconds")
        self.sleep_threshold.setSingleStep(30)
        self.sleep_threshold.setToolTip("Time gap to consider system was asleep")
        layout.addRow("Sleep Detection Threshold:", self.sleep_threshold)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def create_threshold_settings_group(self, parent_layout):
        """Create battery threshold settings group"""
        group = QGroupBox("⚡ Battery Alert Thresholds")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Discharge thresholds
        discharge_label = QLabel("📉 <b>Discharge Alert Levels:</b>")
        discharge_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; margin-bottom: 5px;")
        layout.addWidget(discharge_label)
        
        discharge_help = QLabel("Comma-separated percentage values (e.g., 90, 80, 70, 60, 50, 40, 30, 20, 10)")
        discharge_help.setStyleSheet("font-size: 12px; color: #b0b0b0; margin-bottom: 8px;")
        layout.addWidget(discharge_help)
        
        self.milestone_thresholds = QLineEdit()
        self.milestone_thresholds.setPlaceholderText("90, 80, 70, 60, 50, 40, 30, 20, 10")
        self.milestone_thresholds.setToolTip("Battery percentages that trigger discharge notifications")
        layout.addWidget(self.milestone_thresholds)
        
        # Add some spacing
        layout.addSpacing(10)
        
        # Charging thresholds
        charging_label = QLabel("📈 <b>Charging Alert Levels:</b>")
        charging_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; margin-bottom: 5px;")
        layout.addWidget(charging_label)
        
        charging_help = QLabel("Comma-separated percentage values (e.g., 25, 50, 75, 90, 100)")
        charging_help.setStyleSheet("font-size: 12px; color: #b0b0b0; margin-bottom: 8px;")
        layout.addWidget(charging_help)
        
        self.charging_milestones = QLineEdit()
        self.charging_milestones.setPlaceholderText("25, 50, 75, 90, 100")
        self.charging_milestones.setToolTip("Battery percentages that trigger charging notifications")
        layout.addWidget(self.charging_milestones)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def create_advanced_settings_group(self, parent_layout):
        """Create advanced settings group"""
        group = QGroupBox("⚙️ Advanced Settings")
        layout = QFormLayout()
        layout.setSpacing(12)
        
        # Version info (read-only)
        version_label = QLabel(f"BattMon Version: {VERSION}")
        version_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addRow("", version_label)
        
        # Platform info (read-only)
        platform_label = QLabel(f"Platform: {CURRENT_OS}")
        platform_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addRow("", platform_label)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def create_settings_icon(self):
        """Create a settings icon for the window"""
        try:
            # Create a simple settings icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw gear icon
            painter.setBrush(QBrush(QColor("#0078d4")))
            painter.drawEllipse(8, 8, 16, 16)
            
            # Draw inner circle
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.drawEllipse(12, 12, 8, 8)
            
            painter.end()
            
            return QIcon(pixmap)
        except:
            return QIcon()  # Return empty icon on failure
    
    def get_default_profile_path(self):
        """Get the default profile path based on OS"""
        if IS_WINDOWS:
            config_base = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(config_base, 'BattMon')
        else:
            config_base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            config_dir = os.path.join(config_base, 'battmon')
        
        return os.path.join(config_dir, 'profile.json')
    
    def get_default_profile(self):
        """Get default profile settings"""
        return {
            'milestone_thresholds': [90, 80, 70, 60, 50, 40, 30, 20, 10],
            'charging_milestones': [25, 50, 75, 90, 100],
            'notifications_enabled': True,
            'notification_timeout': 5000,
            'play_sound': True,
            'sleep_notifications_enabled': True,
            'sleep_threshold': 300,
            'version': VERSION
        }
    
    def load_profile(self):
        """Load profile from file"""
        try:
            if os.path.exists(self.profile_path):
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    self.profile_data = json.load(f)
                self.status_label.setText(f"✅ Profile loaded from: {os.path.basename(self.profile_path)}")
            else:
                self.profile_data = self.get_default_profile()
                self.status_label.setText("📄 Using default profile (file will be created on save)")
            
            self.update_ui_from_profile()
            
        except Exception as e:
            self.status_label.setText(f"❌ Error loading profile: {str(e)}")
            self.profile_data = self.get_default_profile()
            self.update_ui_from_profile()
    
    def update_ui_from_profile(self):
        """Update UI elements from loaded profile data"""
        # Notification settings
        self.notifications_enabled.setChecked(self.profile_data.get('notifications_enabled', True))
        self.play_sound.setChecked(self.profile_data.get('play_sound', True))
        self.notification_timeout.setValue(self.profile_data.get('notification_timeout', 5000))
        self.sleep_notifications_enabled.setChecked(self.profile_data.get('sleep_notifications_enabled', True))
        self.sleep_threshold.setValue(self.profile_data.get('sleep_threshold', 300))
        
        # Threshold settings
        milestone_thresholds = self.profile_data.get('milestone_thresholds', [90, 80, 70, 60, 50, 40, 30, 20, 10])
        self.milestone_thresholds.setText(', '.join(map(str, milestone_thresholds)))
        
        charging_milestones = self.profile_data.get('charging_milestones', [25, 50, 75, 90, 100])
        self.charging_milestones.setText(', '.join(map(str, charging_milestones)))
    
    def parse_threshold_list(self, text):
        """Parse comma-separated threshold list from text"""
        try:
            # Split by comma and clean up whitespace
            values = [int(x.strip()) for x in text.split(',') if x.strip().isdigit()]
            # Filter valid percentages (0-100) and remove duplicates
            values = sorted(list(set([v for v in values if 0 <= v <= 100])), reverse=True)
            return values
        except:
            return []
    
    def validate_settings(self):
        """Validate settings before saving"""
        errors = []
        
        # Validate discharge thresholds
        discharge_thresholds = self.parse_threshold_list(self.milestone_thresholds.text())
        if not discharge_thresholds:
            errors.append("Discharge alert levels: Must contain at least one valid percentage (0-100)")
        
        # Validate charging thresholds
        charging_thresholds = self.parse_threshold_list(self.charging_milestones.text())
        if not charging_thresholds:
            errors.append("Charging alert levels: Must contain at least one valid percentage (0-100)")
        
        # Validate notification timeout
        timeout = self.notification_timeout.value()
        if timeout < 1000 or timeout > 30000:
            errors.append("Notification duration: Must be between 1000 and 30000 milliseconds")
        
        # Validate sleep threshold
        sleep_threshold = self.sleep_threshold.value()
        if sleep_threshold < 60 or sleep_threshold > 3600:
            errors.append("Sleep detection threshold: Must be between 60 and 3600 seconds")
        
        return errors
    
    def save_profile(self):
        """Save profile to file"""
        try:
            # Validate settings first
            errors = self.validate_settings()
            if errors:
                error_msg = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
                QMessageBox.warning(self, "Validation Errors", error_msg)
                return
            
            # Update profile data from UI
            self.profile_data.update({
                'notifications_enabled': self.notifications_enabled.isChecked(),
                'play_sound': self.play_sound.isChecked(),
                'notification_timeout': self.notification_timeout.value(),
                'sleep_notifications_enabled': self.sleep_notifications_enabled.isChecked(),
                'sleep_threshold': self.sleep_threshold.value(),
                'milestone_thresholds': self.parse_threshold_list(self.milestone_thresholds.text()),
                'charging_milestones': self.parse_threshold_list(self.charging_milestones.text()),
                'version': VERSION
            })
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            
            # Save to file
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.profile_data, f, indent=2)
            
            self.status_label.setText(f"✅ Profile saved successfully to: {os.path.basename(self.profile_path)}")
            
            # Show success message
            QMessageBox.information(self, "Profile Saved", 
                                  f"Profile settings have been saved successfully!\n\n"
                                  f"File: {self.profile_path}\n\n"
                                  f"Note: Restart BattMon to apply the changes.")
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            error_msg = f"Failed to save profile: {str(e)}"
            self.status_label.setText(f"❌ {error_msg}")
            QMessageBox.critical(self, "Save Error", error_msg)
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(self, "Reset to Defaults", 
                                   "Are you sure you want to reset all settings to default values?\n\n"
                                   "This will overwrite your current settings.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profile_data = self.get_default_profile()
            self.update_ui_from_profile()
            self.status_label.setText("🔄 Settings reset to defaults (not saved yet)")


def main():
    """Main function to run the Profile Editor standalone"""
    app = QApplication(sys.argv)
    app.setApplicationName("BattMon Profile Editor")
    app.setApplicationVersion(VERSION)
    
    # Check command line arguments for profile path
    profile_path = None
    if len(sys.argv) > 1:
        profile_path = sys.argv[1]
    
    editor = ProfileEditor(profile_path=profile_path)
    
    # Center the window
    screen = app.primaryScreen().geometry()
    x = (screen.width() - editor.width()) // 2
    y = (screen.height() - editor.height()) // 2
    editor.move(x, y)
    
    result = editor.exec()
    sys.exit(result)


if __name__ == '__main__':
    main()

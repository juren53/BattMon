#!/usr/bin/env python3
"""
Professional Windows battery popup with native PyQt6 styling
"""

import sys
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QFrame, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import argparse


class BatteryPopup(QWidget):
    """Fixed battery popup for Windows"""
    
    def __init__(self, popup_number=1, manager=None, parent=None):
        super().__init__(parent)
        self.popup_number = popup_number
        self.manager = manager  # Reference to popup manager
        self.user_clicked = False
        self.auto_close_timer = None
        self.init_ui()
        self.start_auto_close_timer()
        
    def init_ui(self):
        """Initialize UI with modern Windows 11 design"""
        self.setWindowTitle(f"Battery Status {self.popup_number}")
        self.setFixedSize(220, 170)
        
        # Use normal window with title bar for predictable layout
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Get battery info
        battery_info = self.get_battery_info()
        
        # Minimal, native-friendly styling
        self.setStyleSheet("""
            QWidget { font-family: system-ui, 'Noto Sans', Ubuntu, Cantarell, 'Segoe UI', sans-serif; background: #ffffff; }
            QLabel { color: #202020; }
        """)
        
        # Main layout with modern spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Large battery percentage display
        percentage_container = QFrame()
        percentage_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        perc_layout = QVBoxLayout(percentage_container)
        perc_layout.setContentsMargins(0, 6, 0, 6)
        perc_layout.setSpacing(6)
        
        percentage_label = QLabel(f"{battery_info['percent']}%")
        percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        percentage_label.setStyleSheet("font-size: 28px; font-weight: 800; color: #0078d4; margin: 0;")
        percentage_label.setMinimumHeight(80)
        percentage_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Center percentage with ample breathing room
        perc_layout.addStretch(1)
        perc_layout.addWidget(percentage_label, alignment=Qt.AlignmentFlag.AlignCenter)
        perc_layout.addStretch(1)
        
        # Status information with conditional color
        status_text = "AC Power Connected" if battery_info['plugged'] else "Running on Battery"
        status_color = "#202020" if battery_info['plugged'] else "#dc3545"  # red when on battery
        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {status_color}; padding: 2px 0;")
        status_label.setWordWrap(False)
        status_label.setFixedHeight(18)
        status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Tip/instructions
        self.instructions = QLabel("Click to close • Auto in 10s")
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions.setStyleSheet("font-size: 10px; color: #5a5a5a; font-style: italic; padding: 2px;")
        
        # Add everything to main layout with clear separation (no lines)
        layout.addWidget(percentage_container, 1)
        layout.addSpacing(6)
        layout.addWidget(self.instructions, 0)
        layout.addSpacing(4)
        layout.addWidget(status_label, 0)
        
        self.setLayout(layout)
        
        # Position bottom-right for better UX
        self.position_bottom_right()
    
    def get_battery_info(self):
        """Get battery info using psutil"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': int(battery.percent),
                    'plugged': battery.power_plugged
                }
            else:
                return {'percent': 100, 'plugged': True}
        except Exception as e:
            print(f"Error getting battery info: {e}")
            return {'percent': 0, 'plugged': False}
    
    def position_bottom_right(self):
        """Position window near bottom-right of the primary screen with slight offset per popup"""
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            margin = 20
            offset = (self.popup_number - 1) * 24
            x = screen.right() - self.width() - margin - offset
            y = screen.bottom() - self.height() - margin - offset
            self.move(max(screen.left(), x), max(screen.top(), y))
        except Exception as e:
            print(f"Error positioning window: {e}")
            self.move(1000, 600)
    
    def start_auto_close_timer(self):
        """Start the auto-close timer"""
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.auto_close)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.start(10000)  # 10 seconds - much longer for testing
        
        # Add countdown timer for user feedback
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # Update every second
        self.seconds_left = 10
    
    def update_countdown(self):
        """Update the countdown display"""
        if not self.user_clicked:
            self.seconds_left -= 1
            if self.seconds_left > 0:
                self.instructions.setText(f"Auto-closes in {self.seconds_left} seconds")
            else:
                self.instructions.setText("Closing now...")
    
    def auto_close(self):
        """Auto-close the popup"""
        if not self.user_clicked:
            print(f"Auto-closing popup #{self.popup_number} after 10 seconds")
            self.close()
    
    
    def mousePressEvent(self, event):
        """Click anywhere to close immediately"""
        print(f"User closing popup #{self.popup_number} by click")
        self.close()
        super().mousePressEvent(event)
    
    def closeEvent(self, event):
        """Clean up when closing and notify manager"""
        if self.auto_close_timer:
            self.auto_close_timer.stop()
        if hasattr(self, 'countdown_timer') and self.countdown_timer:
            self.countdown_timer.stop()
        # Notify manager for immediate exit on 3rd popup
        if self.manager:
            try:
                self.manager.on_popup_closed(self)
            except Exception as e:
                print(f"Manager notification failed: {e}")
        super().closeEvent(event)


class PopupManager:
    """Fixed popup manager using Qt timers only"""
    
    def __init__(self):
        self.popup_count = 0
        self.max_popups = 3
        self.app = None
        self.creation_timer = None
        self.active_popups = []
        self.closed_popups = 0
        
    def start(self):
        """Start the popup manager"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Battery Popup Test - Fixed")
        
        print("Fixed Battery Popup Manager started")
        print(f"Will create {self.max_popups} popup(s), 10 seconds apart, then exit")
        
        # Set up popup creation timer
        self.creation_timer = QTimer()
        self.creation_timer.timeout.connect(self.create_popup)
        
        # Create first popup immediately
        self.create_popup()
        
        # Set timer for subsequent popups (if needed)
        if self.popup_count < self.max_popups:
            self.creation_timer.start(10000)  # 10 seconds
        
        # Remove delayed exit; we'll exit immediately after 3rd popup closes
        
        # Keep app alive even when no windows are visible
        self.app.setQuitOnLastWindowClosed(False)
        
        try:
            return self.app.exec()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.clean_exit()
            return 0
    
    def create_popup(self):
        """Create a new popup"""
        
        if self.popup_count >= self.max_popups:
            print("Maximum popups reached, stopping creation")
            if self.creation_timer:
                self.creation_timer.stop()
            return
            
        self.popup_count += 1
        print(f"Creating popup #{self.popup_count}")
        
        popup = BatteryPopup(self.popup_count, self)
        popup.show()
        self.active_popups.append(popup)
        
        # Stop creation timer if we've reached max
        if self.popup_count >= self.max_popups:
            if self.creation_timer:
                self.creation_timer.stop()
            print("All popups created. Program will exit when the 3rd popup closes.")
    
    def clean_exit(self):
        """Clean exit - close all popups and quit"""
        print("Cleaning up and exiting...")
        
        # Stop timers
        if self.creation_timer:
            self.creation_timer.stop()
        
        # Close all active popups
        for popup in self.active_popups:
            if popup and not popup.isHidden():
                popup.close()
        
        # Quit application
        if self.app:
            self.app.quit()


    def on_popup_closed(self, popup: BatteryPopup):
        """Called by BatteryPopup when it closes"""
        self.closed_popups += 1
        # Exit immediately when the 3rd popup (max) closes
        if getattr(popup, 'popup_number', 0) == self.max_popups:
            print("Third popup closed. Exiting now.")
            if self.app:
                self.app.quit()
        elif self.closed_popups >= self.max_popups:
            # Fallback: if somehow we missed the third's number
            print("All popups closed. Exiting now.")
            if self.app:
                self.app.quit()


def main():
    """Main function"""
    print("Starting Fixed Windows Battery Popup Test...")
    
    manager = PopupManager()
    
    try:
        exit_code = manager.start()
        print("Program completed successfully")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        manager.clean_exit()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        manager.clean_exit()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Battery popup test")
    parser.add_argument("--one", action="store_true", help="Show a single popup and exit when it closes")
    parser.add_argument("--lifetime", type=int, default=10, help="Auto-close seconds for popup")
    args = parser.parse_args()

    if args.one:
        # One-shot mode for critique
        mgr = PopupManager()
        mgr.max_popups = 1
        # Patch lifetime for this run
        orig_init = BatteryPopup.start_auto_close_timer
        def patched_start(self):
            self.auto_close_timer = QTimer()
            self.auto_close_timer.timeout.connect(self.auto_close)
            self.auto_close_timer.setSingleShot(True)
            self.auto_close_timer.start(args.lifetime * 1000)
            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)
            self.seconds_left = args.lifetime
        BatteryPopup.start_auto_close_timer = patched_start
        sys.exit(mgr.start())
    else:
        main()

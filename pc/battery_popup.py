#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battery popup toast for BattMon (PyQt6)

Provides a small, borderless, always-on-top popup that shows the current
battery percentage and state, color-coded by level, and auto-dismisses after
a specified duration.

How to dismiss:
- Auto-dismiss after the specified duration.
- Click anywhere on the popup to close immediately.
- Press Esc (or Q) to close immediately.
- Ctrl+C in the terminal will now also stop the program when running the demo.

Public API:
    show_battery_popup(percentage: int, state: str, duration_ms: int = 3000)

Run as a script to demo:
    python battery_popup.py
"""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout


# Color tiers (match BattMon's scheme as closely as possible)
#  - >= 75: green
#  - >= 50: yellow
#  - >= 30: orange
#  - <  30: red
LEVEL_STYLES = {
    'green': {
        'bg': '#E6F4EA',  # light green
        'fg': '#1B5E20',
        'border': '#81C784'
    },
    'yellow': {
        'bg': '#FFFDE7',  # light yellow
        'fg': '#8D6E63',
        'border': '#FFF176'
    },
    'orange': {
        'bg': '#FFF3E0',  # light orange
        'fg': '#E65100',
        'border': '#FFB74D'
    },
    'red': {
        'bg': '#FFEBEE',  # light red
        'fg': '#B71C1C',
        'border': '#EF9A9A'
    },
}


def level_key(percent: int) -> str:
    if percent >= 75:
        return 'green'
    if percent >= 50:
        return 'yellow'
    if percent >= 30:
        return 'orange'
    return 'red'


class BatteryPopup(QWidget):
    """A small toast-like popup window for battery info."""

    def __init__(self, percentage: int, state: str, duration_ms: int = 3000, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool  # keep it small and above taskbar z-order
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Basic layout
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Title line: percentage large
        self.title_lbl = QLabel(f"Battery: {percentage}%")
        title_font: QFont = self.title_lbl.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_lbl.setFont(title_font)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Subtitle: state
        self.state_lbl = QLabel(state or "")
        state_font: QFont = self.state_lbl.font()
        state_font.setPointSize(9)
        self.state_lbl.setFont(state_font)
        self.state_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.state_lbl)
        self.setLayout(layout)

        # Style per level
        key = level_key(int(percentage))
        style = LEVEL_STYLES[key]
        # Rounded rectangle look
        self.setStyleSheet(f"""
            QWidget {{
                background: {style['bg']};
                color: {style['fg']};
                border: 2px solid {style['border']};
                border-radius: 10px;
            }}
            QLabel {{
                color: {style['fg']};
            }}
        """)

        # Size hint
        self.resize(260, self.sizeHint().height())

        # Position bottom-right corner of the primary screen
        self._position_bottom_right(margin=18)

        # Auto-close timer
        QTimer.singleShot(max(500, int(duration_ms)), self.close)

    # Allow immediate dismissal via click or keyboard
    def mousePressEvent(self, event):  # type: ignore[override]
        self.close()

    def keyPressEvent(self, event):  # type: ignore[override]
        key = event.key()
        if key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.close()
        else:
            super().keyPressEvent(event)

    def _position_bottom_right(self, margin: int = 12) -> None:
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geo: QRect = screen.availableGeometry()
        size: QSize = self.sizeHint()
        x = geo.right() - size.width() - margin
        y = geo.bottom() - size.height() - margin
        # Ensure not negative
        x = max(geo.left() + margin, x)
        y = max(geo.top() + margin, y)
        self.move(x, y)


def show_battery_popup(percentage: int, state: str, duration_ms: int = 3000) -> None:
    """Show a toast-like battery popup. Ensures a QApplication exists.

    Parameters:
        percentage: battery percent (0-100)
        state: human-readable state (e.g., "Charging", "Discharging")
        duration_ms: auto-dismiss delay
    """
    app_created = False
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app_created = True
    popup = BatteryPopup(percentage=percentage, state=state, duration_ms=duration_ms)
    popup.show()
    # If we created the app, run an event loop until popup closes
    if app_created:
        # Quit when window closes or after a failsafe timeout
        popup.destroyed.connect(app.quit)
        # Failsafe: in case the window can't emit destroyed, ensure exit shortly after duration
        QTimer.singleShot(max(1000, int(duration_ms) + 3000), app.quit)
        try:
            app.exec()
        except KeyboardInterrupt:
            # Allow Ctrl+C to terminate cleanly
            app.quit()


if __name__ == "__main__":
    # Demo: cycle through levels. You can:
    # - Click a popup to dismiss immediately
    # - Press Esc or Q to dismiss it
    # - Press Ctrl+C in the terminal to stop the demo early
    def demo_once(p: int, s: str):
        show_battery_popup(p, s, duration_ms=2000)

    sequence = [
        (85, "Full"),
        (62, "Discharging"),
        (41, "Discharging"),
        (25, "Discharging"),
    ]
    for pct, state in sequence:
        demo_once(pct, state)


# BattMon Cross-Platform - Help Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Tray](#system-tray)
3. [Battery Window](#battery-window)
4. [Notifications](#notifications)
5. [Visual Indicators](#visual-indicators)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Configuration](#configuration)
8. [Platform-Specific Features](#platform-specific-features)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Getting Started

BattMon Cross-Platform is a battery monitoring application that runs on Linux, Windows, and macOS. It provides real-time battery status monitoring through a system tray icon with customizable on screen and audible notifications and alerts.

### First Launch
When you start BattMon for the first time:
- A system tray icon will appear showing the current battery percentage
- A startup notification will display the configured milestone thresholds
- The application runs continuously in the background

### Basic Usage
- **Left-click** the tray icon to show the detailed battery status window
- **Right-click** the tray icon to access the context menu
- The tray icon is dynamic and continuously updates to reflect the system's battery 'state of charge'

## System Tray

The system tray icon is the primary interface with BattMon. It provides at-a-glance information about the battery status .

### Tray Icon Features
- **Dynamic battery visualization**: Shows actual battery fill level
- **Color-coded status**:
  - **Green** (75-100%): Good charge level
  - **Yellow** (50-74%): Medium charge level
  - **Orange** (30-49%): Low charge level
  - **Red** (0-29%): Critical charge level
- **Percentage display**: Shows exact battery percentage (on larger icons)
- **Charging indicator**: Lightning bolt symbol when plugged in
- **Pulsing animation**: Activates during low battery warnings

### Context Menu Options
Right-click the tray icon to access:
- **Battery Status**: Current percentage and state (disabled item)
- **Show Battery Window**: Opens detailed battery information
- **🔔 Show Notification Settings**: Displays the current milestone configuration
- **Help**: Opens this help documentation
- **About**: Application information and version details
- **Quit**: Close the application

## Battery Window

The battery window provides detailed information about the battery status in a clean, modern interface.

### Window Features
- **Large percentage display**: Easy-to-read battery level
- **Color-coded progress bar**: Visual representation of charge level
- **Status information**: Current battery state (Charging, Discharging, Full, etc.)
- **Time remaining**: Estimated time to full charge or complete discharge (when available)
- **Platform indicator**: Shows which operating system you're running
- **Always on top**: Window stays visible above other applications

### Window Controls
- **Close button**: Hides the window (application continues running in tray)
- **Window can be moved**: Drag the title bar to reposition
- **Auto-update**: Information refreshes automatically every 2 seconds

## Notifications

BattMon features a comprehensive desktop notification system to keep you informed about the battery status.

### Milestone Notifications
- **Default thresholds**: 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10%
- **Charging milestones**: 25%, 50%, 75%, 90%, 100%
- **Smart notifications**: Prevents spam by tracking last triggered milestone
- **Native platform notifications**: Uses the operating system's notification system

### Notification Types
- **Startup notification**: Shows configured milestones when app starts
- **Discharging alerts**: Warns when battery drops to milestone levels
- **Charging alerts**: Notifies when battery reaches charging milestones
- **Status change alerts**: Notifies when switching between charging/discharging
- **Critical alerts**: Enhanced warnings for very low battery levels

### Audio Alerts
- **Platform-specific sounds**: Uses native system sounds when available
- **Pulse beeping**: Audio cues during low battery pulsing animation
- **Multiple beep patterns**: Different sounds for different urgency levels
- **Fallback support**: Works even when system sounds are disabled

## Visual Indicators

BattMon uses various visual cues to communicate battery status effectively.

### Color Coding System
The 4-tier color system is used throughout the application:

| Range | Color | Meaning | Action Needed |
|-------|--------|---------|---------------|
| 75-100% | Green | Good | None |
| 50-74% | Yellow | Medium | Consider charging soon |
| 30-49% | Orange | Low | Should charge |
| 0-29% | Red | Critical | Charge immediately |

### Animation Effects
- **Pulsing**: Low battery warning with opacity animation
- **Smooth updates**: Gradual color transitions
- **Charging indicator**: Lightning bolt overlay when plugged in
- **Progress bar**: Animated fill level changes

## Keyboard Shortcuts

While BattMon primarily uses mouse interaction, some shortcuts are available:

- **Double-click tray icon**: Alternative way to show battery window
- **Escape key**: Close battery window (when focused)
- **Alt+F4**: Close battery window (Windows/Linux)
- **Cmd+W**: Close battery window (macOS)

## Configuration

BattMon automatically manages its configuration through user profiles.

### User Profile Location
- **Linux**: `~/.config/battmon/profile.json`
- **Windows**: `%APPDATA%\battmon\profile.json`
- **macOS**: `~/Library/Application Support/battmon/profile.json`

### Configurable Settings
```json
{
  "milestone_thresholds": [90, 80, 70, 60, 50, 40, 30, 20, 10],
  "charging_milestones": [25, 50, 75, 90, 100],
  "notifications_enabled": true,
  "last_milestone_triggered": null,
  "last_charging_milestone": null
}
```

### Automatic Saving
- Settings are automatically saved when the application exits
- Profile is loaded on startup
- Changes take effect immediately

## Platform-Specific Features

BattMon adapts to each operating system's conventions and capabilities.

### Linux
- **Native ACPI battery reading**: Direct hardware access
- **Desktop environment integration**: Works with GNOME, KDE, XFCE, etc.
- **Package manager support**: Can be installed via pip or system packages
- **Session management**: Integrates with desktop session handling

### Windows
- **Windows API integration**: Uses native battery information APIs
- **System tray conventions**: Follows Windows UI guidelines
- **Windows notification system**: Uses Windows 10/11 toast notifications
- **High DPI support**: Scales properly on high-resolution displays
- **Windows sound system**: Integrates with system audio settings

### macOS
- **macOS styling**: Uses native macOS UI conventions
- **Notification Center**: Integrates with macOS notification system
- **Menu bar**: Proper macOS menu bar integration
- **Retina display support**: Optimized for high-resolution displays

## Troubleshooting

### Common Issues

#### System Tray Icon Not Visible
- **Linux**: Ensure the desktop environment supports system tray
- **Windows**: Check if system tray icons are enabled in taskbar settings
- **macOS**: Look in the menu bar area

#### No Battery Information
- **Verify battery exists**: Some desktop systems don't have batteries
- **Check permissions**: Application needs access to battery information
- **Restart application**: Sometimes helps refresh battery detection

#### Notifications Not Working
- **Check system settings**: Ensure notifications are enabled for applications
- **Verify profile**: Check if `notifications_enabled` is `true` in profile
- **Platform-specific**: Each OS has different notification permission systems

#### High CPU Usage
- **Normal behavior**: Application updates every 2 seconds
- **Check for issues**: Restart if CPU usage seems excessive
- **Background operation**: Should use minimal resources when not actively displaying

### Getting Help

If you encounter issues not covered here:

1. **Check the GitHub Issues**: [https://github.com/juren53/BattMon/issues](https://github.com/juren53/BattMon/issues)
2. **Review the changelog**: See `CHANGELOG.md` for recent changes
3. **Check system requirements**: Ensure PyQt6 is properly installed
4. **File a bug report**: Include the OS, Python version, and error details

## FAQ

### Q: Does BattMon drain my battery?
A: No, BattMon uses minimal system resources and updates only every 2 seconds. The battery impact is negligible.

### Q: Can I customize the milestone thresholds?
A: Currently, thresholds are set to standard values. Future versions will include a settings interface for customization.

### Q: Why don't I see time remaining information?
A: Time remaining depends on the operating system providing this information. Some systems don't calculate or expose these estimates.

### Q: Can I run multiple instances of BattMon?
A: It's not recommended. BattMon is designed to run as a single instance in the system tray.

### Q: How do I uninstall BattMon?
A: Simply quit the application and delete the executable file. Configuration files in `~/.config/battmon/` can also be removed if desired.

### Q: Does BattMon work with external/multiple batteries?
A: BattMon reads the primary system battery. Support for multiple batteries varies by operating system.

### Q: Can I disable the pulsing animation?
A: The pulsing animation is currently enabled by default for low battery warnings. Future versions will include options to customize this behavior.

### Q: What happens if I close the battery window?
A: Closing the battery window only hides it - the application continues running in the system tray. To fully exit, use the "Quit" option from the context menu.

---

## About This Help

This help documentation covers BattMon Cross-Platform version 0.5.6 and later. Features and interfaces will vary in older versions.

For the most up-to-date information, visit the project repository at:
[https://github.com/juren53/BattMon](https://github.com/juren53/BattMon)

**Last updated**: 2025-08-14 07:20

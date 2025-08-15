# BattMon Cross-Platform - Battery Monitor

A modern, cross-platform battery monitoring application with system tray integration, desktop notifications, and comprehensive battery health information.

## 🚀 Quick Installation (Linux)

**One command to install and run:**

```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash
```

Then start BattMon:
```bash
battmon
```

> **What this does:** Downloads BattMon, installs dependencies (Python 3, PyQt6, ACPI), creates launcher and desktop entry, configures PATH. Works on Ubuntu, Debian, Fedora, Arch, openSUSE, and more.

## ✨ Features

### 🔋 Advanced Battery Monitoring
- **System tray integration** with real-time battery percentage display
- **Color-coded battery levels**: Green (75-100%), Yellow (50-74%), Orange (30-49%), Red (0-29%)
- **Charging indicators** with lightning bolt animation
- **Pulsing low-battery warnings** for critical levels
- **Detailed battery health information** including cycle count, capacity degradation, and manufacturer data

### 📱 Smart Notifications
- **Milestone-based desktop notifications** at configurable battery levels
- **Default discharge alerts**: 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10%
- **Default charging alerts**: 25%, 50%, 75%, 90%, 100%
- **Cross-platform notification system** with native OS integration
- **Configurable sound alerts** with platform-specific audio

### 🖥️ Modern User Interface
- **Interactive battery status window** with comprehensive information
- **Professional Qt6-based design** matching system themes
- **High DPI display support** for crisp icons on all screens
- **Context menu** with quick access to all features
- **Built-in help system** with comprehensive documentation

### 🌐 Cross-Platform Support
- **Linux**: ACPI integration with full battery health data
- **Windows**: WMI/PowerShell integration with chemistry detection
- **macOS**: system_profiler and ioreg integration
- **Universal**: Consistent experience across all platforms

## 📦 Installation Options

### Option 1: Quick Install Script (Recommended)
```bash
# Download and run installer
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash

# Start BattMon
battmon
```

### Option 2: Manual Installation
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt install python3 python3-pip acpi
pip install PyQt6

# Download BattMon
mkdir -p ~/.local/share/battmon
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/battmon.py -o ~/.local/share/battmon/battmon.py
chmod +x ~/.local/share/battmon/battmon.py

# Run directly
python3 ~/.local/share/battmon/battmon.py
```

### Option 3: Development/Git Clone
```bash
git clone https://github.com/juren53/BattMon.git
cd BattMon/pc
pip install PyQt6
python3 battmon.py
```

## 🎯 System Requirements

### Linux:
- Python 3.8 or higher
- PyQt6 (installed automatically)
- ACPI utilities (`acpi` command)
- System tray support in desktop environment

### Windows:
- Python 3.8 or higher
- PyQt6
- PowerShell (built-in) or WMI module

### macOS:
- Python 3.8 or higher
- PyQt6
- Built-in system utilities (pmset, system_profiler)

## 🏃‍♂️ Usage

### Starting BattMon:
- **Command line**: `battmon` (after installation)
- **Application menu**: Search for "BattMon Cross-Platform"
- **Auto-start**: Add to your desktop environment's startup applications

### Interacting with BattMon:
- **Left-click tray icon**: Show detailed battery status window
- **Right-click tray icon**: Context menu with options
- **Hover over tray icon**: Quick battery status tooltip
- **Notifications**: Automatic alerts at milestone battery levels

### Key Features:
- **Battery Status Window**: Comprehensive battery information with refresh capability
- **Notification Settings**: View configured milestone thresholds
- **Help System**: Built-in documentation and troubleshooting
- **About Dialog**: Version information and system details

## ⚙️ Configuration

BattMon automatically creates user profiles in:
- **Linux**: `~/.config/battmon/profile.json`
- **Windows**: `%APPDATA%\battmon\profile.json`
- **macOS**: `~/Library/Application Support/battmon/profile.json`

### Default Settings:
```json
{
  "milestone_thresholds": [90, 80, 70, 60, 50, 40, 30, 20, 10],
  "charging_milestones": [25, 50, 75, 90, 100],
  "notifications_enabled": true,
  "notification_timeout": 5000,
  "play_sound": true
}
```

## 🛠️ Troubleshooting

### Common Issues:

**System tray icon not visible:**
- Ensure your desktop environment supports system tray icons
- Try restarting your desktop environment or panel

**Battery detection not working:**
- **Linux**: Install `acpi` package (`sudo apt install acpi`)
- **Windows**: Ensure PowerShell is available
- **macOS**: Built-in utilities should work automatically

**PyQt6 import errors:**
- Install PyQt6: `pip install PyQt6`
- On Linux, try system packages: `sudo apt install python3-pyqt6`

**Permission issues:**
- Ensure script is executable: `chmod +x battmon.py`
- Check configuration directory permissions

### Getting Help:
- **Built-in help**: Right-click BattMon → Help
- **Command line debugging**: Run `battmon` from terminal to see output
- **GitHub Issues**: [Report bugs and request features](https://github.com/juren53/BattMon/issues)

## 📊 Battery Information Displayed

### Basic Information:
- Current charge percentage
- Battery state (Charging, Discharging, Full)
- Time remaining estimate
- Last update timestamp

### Detailed Health Information:
- Battery technology (Li-ion, Li-poly, etc.)
- Manufacturer information
- Current voltage and power draw
- Health status and percentage
- Design vs. current capacity
- Cycle count (charge cycles completed)

### Visual Indicators:
- Color-coded percentage display
- Battery condition icons (🔋, ⚠️, 🚨)
- Charging indicators (⚡)
- Progress bars and status elements

## 🔄 Updates

To update BattMon to the latest version:

```bash
# Re-run the installer
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash
```

Or manually download the latest `battmon.py`:
```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/battmon.py -o ~/.local/share/battmon/battmon.py
```

## 📜 License

GPL v2+ - See source code for full license text.

## 🤝 Contributing

Contributions welcome! Please:
- Test on different Linux distributions and desktop environments
- Report bugs and suggest features via GitHub Issues
- Submit pull requests with improvements
- Help with Windows and macOS testing

## 📈 Version History

- **v0.5.8**: Enhanced Battery Status Window with comprehensive health info and modern styling
- **v0.5.7**: Added Help system with comprehensive documentation
- **v0.5.6**: Desktop milestone notifications and notification settings
- **v0.5.5**: GitHub integration links and Windows 11 audio fixes
- **v0.5.4**: Streamlined About section
- Previous versions: Various Qt6 improvements and cross-platform enhancements

---

**🔋 BattMon Cross-Platform v0.5.8**  
Real-time battery monitoring and health tracking for Linux, Windows, and macOS.

**GitHub**: https://github.com/juren53/BattMon  
**Documentation**: [INSTALL.md](INSTALL.md) | [HELP.md](HELP.md) | [CHANGELOG.md](CHANGELOG.md)


<div align="left" style="margin-top: 20px; margin-left: 20px;">
<img src="Images/battery_cycle_demo.gif" alt="BattMon Battery Cycle Animation" width="80" height="80">
</div>

# BattMon Cross-Platform - Battery Monitor for Windows, Linux & macOS

A modern **PyQt6-based** cross-platform battery monitoring application with **Profile Editor GUI**, **animated demonstrations**, and professional system integration. Displays battery percentage directly in your system tray with intelligent color coding and comprehensive battery health information.

## 🚀 Quick Installation

### Windows (PowerShell)
```powershell
iwr https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-windows.ps1 -UseBasicParsing | iex
```

### Linux (Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash
```

### Manual Installation (Two Steps)
**Windows:**
```powershell
# Download script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-windows.ps1" -OutFile "install-windows.ps1"
# Review and run
.\install-windows.ps1
```

**Linux:**
```bash
# Download script
curl -fsSL -o install-linux.sh https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh
# Review and run
chmod +x install-linux.sh && ./install-linux.sh
```

### What the Installers Do:
- ✅ **Install Python 3.8+ and PyQt6** dependencies automatically
- ✅ **Download BattMon v0.5.13** with Profile Editor GUI
- ✅ **Create system integration** (shortcuts, launchers, desktop entries)
- ✅ **Set up animated GIF assets** and professional help system  
- ✅ **Configure PATH** for easy command-line access
- ✅ **Test installation** and verify all components

---

## Features

### 🔋 Ultra-Readable Battery Display
- **Dynamic percentage display** directly in system tray with real-time updates
- **Color-coded battery levels**: Red (0-29%), Orange (30-49%), Yellow (50-74%), Green (75-100%)
- **Charging indicators**: Lightning bolt animation and visual feedback
- **Pulsing animation** for low battery warnings
- **High DPI support** for crisp display on all screen types
- **Cross-platform compatibility**: Works on Windows, Linux, and macOS

### 🖱️ Interactive Features (v0.5.13)
- **Left-click**: Show/hide **persistent battery status window** with detailed information
- **Right-click**: Context menu with **Profile Editor**, battery info, about dialog, and help
- **🔧 Profile Editor GUI**: Modern interface for configuring all settings (NEW)
- **🎬 Animated About dialog**: Features battery cycle demonstration GIF (NEW)
- **📖 Professional help system**: Integrated documentation and support (NEW)
- **Smart tooltips**: Hover for current battery status and time remaining
- **Desktop notifications**: Configurable alerts for battery milestones

### ⚡ Advanced Technical Features (PyQt6-based)
- **Modern PyQt6 framework** with native system integration
- **Cross-platform battery detection**: ACPI (Linux), WMI/PowerShell (Windows), pmset (macOS)
- **JSON configuration system** with Profile Editor GUI
- **QDialog battery windows** with auto-refresh and manual refresh buttons
- **QMovie animated GIF support** for visual demonstrations
- **Virtual environment support** on Linux for isolated dependencies
- **Professional error handling** and graceful fallbacks
- **Milestone tracking system** with customizable thresholds

## Requirements

**Automatically handled by installers** - No manual setup needed!

- **Python 3.8+** (auto-installed by installers)
- **PyQt6 6.4.0+** (auto-installed)
- **Platform-specific battery utilities**:
  - **Windows**: WMI/PowerShell (built-in)
  - **Linux**: ACPI utilities (auto-installed)
  - **macOS**: pmset (built-in)

### Manual Installation Requirements:
If not using the automated installers:

**Windows:**
```powershell
pip install "PyQt6>=6.4.0"
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3 python3-pip python3-venv acpi
pip install "PyQt6>=6.4.0"
```

**macOS:**
```bash
brew install python3
pip3 install "PyQt6>=6.4.0"
```

## Usage

### After Installation:
**Windows:**
- Search for "BattMon Cross-Platform" in Start Menu, or
- Run `python "C:\Users\[username]\AppData\Local\BattMon\battmon.py"`

**Linux:**
- Search for "BattMon Cross-Platform" in application menu, or
- Run `battmon` from terminal (if added to PATH)

### Manual Run:
```bash
# If you cloned the repository manually
python3 battmon.py
```

### Add to Startup:
- **Windows**: Use Task Scheduler or Startup folder
- **Linux**: Add to your desktop environment's startup applications
- **macOS**: Add to Login Items in System Preferences

## Configuration

### 🔧 Profile Editor GUI (Recommended)
1. **Right-click** the BattMon system tray icon
2. Select **"Profile Editor"** from context menu
3. Configure settings in the **modern GUI interface**:
   - Notification settings and timeouts
   - Battery alert thresholds (discharge/charging)
   - Audio alerts and sleep/wake notifications
   - Advanced options

### Manual Configuration (JSON)
Configuration is stored in JSON format:
- **Windows**: `%APPDATA%\BattMon\profile.json`
- **Linux**: `~/.config/battmon/profile.json`
- **macOS**: `~/Library/Application Support/battmon/profile.json`

Example profile.json:
```json
{
  "milestone_thresholds": [90, 80, 70, 60, 50, 40, 30, 20, 10],
  "charging_milestones": [25, 50, 75, 90, 100],
  "notifications_enabled": true,
  "notification_timeout": 5000,
  "play_sound": true,
  "sleep_notifications_enabled": true,
  "sleep_threshold": 300
}
```

## Design Philosophy

### Ultra-Readable Design:
1. **Rectangular Battery Shape**: Realistic battery appearance with terminal, stands out in any system tray
2. **Text Improvements**: Font size 9-13 (large and clear) with bold white text
3. **Maximum Contrast**: White text with thick 3-pixel black outline on colored background
4. **Smart Text Positioning**: Adaptive sizing and centering based on digit count (5 vs 50 vs 100)
5. **Prominent Charging Indicator**: Bright yellow lightning bolt with white outline positioned above battery for maximum visibility

### Visual Result:
- **Instantly readable** percentage at any distance
- **Professional appearance** with clean rectangular battery design
- **Works universally** across all desktop themes and environments

## Troubleshooting

### Installation Issues:
- **PowerShell execution policy (Windows)**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` if needed
- **Internet connection**: Ensure stable internet for downloading components
- **Python version**: Verify Python 3.8+ is installed (`python3 --version`)

### Runtime Issues:

**System tray icon not visible:**
- Ensure your desktop environment supports system tray icons
- **Linux**: Check if `acpi -b` works for battery detection
- **Windows**: Verify PyQt6 installation: `python -c "from PyQt6.QtWidgets import QApplication"`
- **macOS**: Check system tray visibility settings

**Profile Editor not opening:**
- Ensure `profile_editor.py` was downloaded during installation
- Check that PyQt6 is properly installed
- Try running: `python profile_editor.py` standalone

**Animated GIF not showing:**
- Verify `Images/animated_battery_cycle_slow.gif` exists in installation directory
- Check PyQt6 QMovie support: `python -c "from PyQt6.QtGui import QMovie"`

**High CPU usage:**
- Normal update interval is 5 seconds
- Check console for error messages
- Restart BattMon if issues persist

### Getting Help:
- Check the built-in **Help** system (right-click tray icon → Help)
- Visit the [GitHub Issues](https://github.com/juren53/BattMon/issues) page
- Review the [CHANGELOG.md](CHANGELOG.md) for recent updates

## Development

**BattMon Cross-Platform** is built with **modern PyQt6** and designed for cross-platform compatibility. The application has evolved from a GTK3-based Linux-only tool to a comprehensive cross-platform solution.

### Architecture (v0.5.13):
- **BattMonCrossPlatform class**: Main application with PyQt6 integration
- **ProfileEditor class**: Standalone GUI configuration module
- **Cross-platform battery detection**: Platform-specific implementations
- **QDialog system**: Modern windowing with persistent status displays
- **JSON configuration**: Human-readable settings with GUI editor
- **QMovie animations**: Integrated GIF demonstrations
- **Professional error handling**: Graceful fallbacks and user feedback

### Key Files:
- `battmon.py` - Main application (v0.5.13)
- `profile_editor.py` - Profile Management GUI (v0.5.12+)
- `HELP.md` - Integrated help system
- `Images/` - Visual assets and animations
- `install-windows.ps1` / `install-linux.sh` - Installation scripts

### Development Setup:
```bash
git clone https://github.com/juren53/BattMon.git
cd BattMon/pc
pip install "PyQt6>=6.4.0"
python3 battmon.py
```

## License

**GPL v2+** - See source code for full license text.

## Contributing

Contributions welcome! Please test on various operating systems and desktop environments.

### Areas for Contribution:
- **macOS testing and optimization**
- **Additional Linux distribution support**
- **Windows feature enhancements**
- **Translation and internationalization**
- **Documentation improvements**
- **UI/UX enhancements**

### Reporting Issues:
1. Check existing [GitHub Issues](https://github.com/juren53/BattMon/issues)
2. Include your OS, Python version, and PyQt6 version
3. Provide console output if available
4. Describe steps to reproduce the issue

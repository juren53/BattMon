
<div align="left" style="margin-top: 20px; margin-left: 20px;">
<img src="Images/battery_cycle_demo.gif" alt="BattMon Battery Cycle Animation" width="80" height="80">
</div>

# BattMon PC - Battery Monitor for Linux, PCs and Macs

A modern Python 3 battery monitoring application that displays battery percentage directly in your system tray with a clean, highly readable rectangular battery icon design.

## Features

### 🔋 Ultra-Readable Battery Display
- **Large percentage numbers** (font size 9-13px) displayed directly in system tray
- **Rectangular battery shape** with terminal for realistic appearance
- **Color-coded background**: Red (0-25%), Orange (26-75%), Green (76-100%)
- **High contrast design**: White text with thick black outline on colored background
- **Prominent charging indicator**: Bright yellow lightning bolt with white outline when plugged in
- **Works on any theme**: Light, dark, or custom system tray themes

### 🖱️ Interactive Features
- **Left-click**: Show detailed battery notification
- **Right-click**: Context menu with battery info, about dialog, and quit option
- **About dialog**: Version information and last update timestamp
- **Tooltip**: Hover for current battery status and time remaining
- **Smart notifications**: Only shows console output for significant changes (5% or state changes)

### ⚡ Technical Features
- **Python 3** with GTK3 system tray integration
- **Custom Cairo graphics** for crisp, scalable icons
- **ACPI integration** for reliable battery status
- **Configurable**: Easy-to-edit configuration file
- **Lightweight**: Minimal resource usage with 2-second update interval

## Requirements

- Python 3.x
- GTK 3 with GObject Introspection
- Cairo graphics library
- ACPI utilities (`acpi` command)
- Linux with system tray support

### Install Dependencies (Ubuntu/Debian/Mint):
```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 acpi
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/juren53/BattMon.git
cd BattMon/pc/
```

2. Make the script executable:
```bash
chmod +x battmon.py
```

3. The configuration file `~/.battmon` will be created automatically on first run with sensible defaults.

## Usage

### Run BattMon:
```bash
python3 battmon.py
# or
./battmon.py
```

### Run in Background:
```bash
python3 battmon.py &
```

### Add to Startup:
Add the following line to your autostart applications:
```bash
/path/to/BattMon/pc/battmon.py
```

## Configuration

The configuration file is located at `~/.battmon`. You can customize:
- Click commands
- Battery level thresholds
- Icon preferences (fallback to system icons if custom drawing fails)

Example config:
```ini
[general]
command = notify-send "Battery Status" "Click to see detailed battery information"

[empty]
percent = 5
icon = battery-level-0-symbolic
charge_icon = battery-level-0-charging-symbolic

[low]
percent = 25
icon = battery-level-20-symbolic
charge_icon = battery-level-20-charging-symbolic

# ... more battery levels
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

### Icon not visible:
- Ensure your desktop environment supports system tray icons
- Check if `acpi` command works: `acpi -b`
- Verify GTK3 dependencies are installed

### Permission issues:
- Make sure the script is executable: `chmod +x battmon.py`
- Verify config file permissions: `ls -la ~/.battmon`

### High CPU usage:
- Normal update interval is 2 seconds
- Check for error messages in console output

## Development

Converted from Python 2 to Python 3 with modern GTK3 integration. The original design was evolved into a rectangular battery shape optimized for maximum text readability and realistic battery appearance.

### Key Components:
- **MainApp class**: Core application logic and GTK integration
- **create_battery_icon_with_text()**: Custom Cairo graphics for battery icon
- **ACPI integration**: Battery status detection via `acpi` command
- **Configuration system**: INI-style config file support

## License

GPL v2+ - See source code for full license text.

## Contributing

Contributions welcome! Please test on various Linux distributions and desktop environments.

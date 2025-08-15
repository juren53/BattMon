# BattMon Cross-Platform - Quick Installation Guide

## 🚀 One-Command Installation (Linux)

For users who want to quickly install and run BattMon without cloning the entire repository:

### Download and Run Installer

```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash
```

### Alternative: Download First, Then Run

```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh -o install-battmon.sh
chmod +x install-battmon.sh
./install-battmon.sh
```

## ✨ What the Installer Does

The installation script automatically:

- **Detects your Linux distribution** and installs appropriate dependencies
- **Installs Python 3, PyQt6, and ACPI utilities** via your package manager
- **Downloads BattMon files** from GitHub (battmon.py, HELP.md)
- **Creates a launcher script** at `~/.local/bin/battmon`
- **Sets up desktop entry** for application menu integration
- **Configures PATH** so you can run `battmon` from anywhere
- **Tests the installation** to ensure everything works

## 📦 What Gets Installed

### Files and Directories:
- `~/.local/share/battmon/` - Main application directory
- `~/.local/share/battmon/battmon.py` - Main application
- `~/.local/share/battmon/HELP.md` - Help documentation
- `~/.local/bin/battmon` - Launcher script
- `~/.local/share/applications/battmon.desktop` - Desktop entry

### System Dependencies:
- Python 3.8+ 
- PyQt6 (system package or pip installation)
- ACPI utilities for battery detection
- curl for downloading files

## 🎯 Supported Linux Distributions

The installer supports:

- **Debian/Ubuntu-based**: Ubuntu, Debian, Linux Mint, Pop!_OS
- **Red Hat-based**: Fedora, CentOS, RHEL, Rocky Linux, AlmaLinux
- **Arch-based**: Arch Linux, Manjaro
- **SUSE-based**: openSUSE, SUSE Linux Enterprise
- **Generic**: Any distribution with Python 3.8+ and basic tools

## 🏃‍♂️ After Installation

### Run BattMon:
```bash
battmon
```

### Or find it in your application menu:
Search for "BattMon Cross-Platform"

### Add to startup applications:
Use your desktop environment's startup applications settings to add `battmon` to autostart.

## 🔧 Manual Installation (Alternative)

If you prefer manual installation or the script doesn't work:

### 1. Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip acpi
pip install PyQt6
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip acpi
pip install PyQt6
```

**Arch:**
```bash
sudo pacman -S python python-pip acpi
pip install PyQt6
```

### 2. Download BattMon

```bash
mkdir -p ~/.local/share/battmon
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/battmon.py -o ~/.local/share/battmon/battmon.py
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/HELP.md -o ~/.local/share/battmon/HELP.md
chmod +x ~/.local/share/battmon/battmon.py
```

### 3. Create Launcher

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/battmon << 'EOF'
#!/bin/bash
python3 "$HOME/.local/share/battmon/battmon.py" "$@"
EOF
chmod +x ~/.local/bin/battmon
```

### 4. Add to PATH

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🆘 Troubleshooting

### Installation Issues:

- **No internet connection**: Check your network connection
- **Permission denied**: Make sure you have sudo access for system packages
- **PyQt6 installation fails**: Try using system packages instead of pip
- **ACPI not working**: Install `acpi` package for your distribution

### Runtime Issues:

- **Icon not visible**: Ensure your desktop environment supports system tray
- **No battery detected**: Run `acpi -b` to test battery detection
- **Import errors**: Verify PyQt6 installation with `python3 -c "from PyQt6.QtWidgets import QApplication"`

### Get Help:

- **Built-in help**: Right-click BattMon tray icon → Help
- **GitHub Issues**: https://github.com/juren53/BattMon/issues
- **Check logs**: Run `battmon` from terminal to see debug output

## 🔄 Updating BattMon

To update to the latest version, simply run the installer again:

```bash
curl -fsSL https://raw.githubusercontent.com/juren53/BattMon/main/pc/install-linux.sh | bash
```

The installer will download the latest files and update your installation.

## 🗑️ Uninstallation

To remove BattMon:

```bash
rm -rf ~/.local/share/battmon
rm -f ~/.local/bin/battmon
rm -f ~/.local/share/applications/battmon.desktop
```

Then remove the PATH entry from your shell config files if desired.

---

**🔋 BattMon Cross-Platform v0.5.8**  
Battery monitoring made simple for Linux, Windows, and macOS.

#!/bin/bash
# BattMon Cross-Platform Linux Installation Script
# Version 1.1 - Installs BattMon v0.5.13 with Profile Editor and animated GIF features
# Designed for BattMon v0.5.13 (August 2025) - includes Profile Management GUI and visual enhancements
#
# New in this version:
# - Downloads profile_editor.py module for GUI configuration management
# - Downloads animated GIF assets for enhanced About dialog
# - Supports all features added in BattMon v0.5.9 through v0.5.13
# - Enhanced testing for new modules and QMovie support

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BATTMON_DIR="$HOME/.local/share/battmon"
DESKTOP_FILE="$HOME/.local/share/applications/battmon.desktop"
BIN_DIR="$HOME/.local/bin"
GITHUB_RAW="https://raw.githubusercontent.com/juren53/BattMon/main/pc"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_LIKE=$ID_LIKE
    else
        DISTRO="unknown"
        DISTRO_LIKE=""
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    detect_distro
    
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            if ! command_exists sudo; then
                print_error "sudo is required but not installed. Please install sudo or run as root."
                exit 1
            fi
            
            print_info "Installing dependencies for Debian/Ubuntu-based system..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv acpi curl
            
            # Try to install PyQt6 from system packages first
            if sudo apt install -y python3-pyqt6 2>/dev/null; then
                print_success "Installed PyQt6 from system packages"
                SYSTEM_PYQT6=true
            else
                print_info "PyQt6 not available in system packages, will install via pip"
                SYSTEM_PYQT6=false
            fi
            ;;
        fedora|centos|rhel|rocky|almalinux)
            if ! command_exists sudo; then
                print_error "sudo is required but not installed. Please install sudo or run as root."
                exit 1
            fi
            
            print_info "Installing dependencies for Red Hat-based system..."
            sudo dnf install -y python3 python3-pip acpi curl
            
            # Try to install PyQt6 from system packages
            if sudo dnf install -y python3-qt6 2>/dev/null; then
                print_success "Installed PyQt6 from system packages"
                SYSTEM_PYQT6=true
            else
                print_info "PyQt6 not available in system packages, will install via pip"
                SYSTEM_PYQT6=false
            fi
            ;;
        arch|manjaro)
            if ! command_exists sudo; then
                print_error "sudo is required but not installed. Please install sudo or run as root."
                exit 1
            fi
            
            print_info "Installing dependencies for Arch-based system..."
            sudo pacman -Sy --noconfirm python python-pip acpi curl
            
            # Try to install PyQt6 from system packages
            if sudo pacman -S --noconfirm python-pyqt6 2>/dev/null; then
                print_success "Installed PyQt6 from system packages"
                SYSTEM_PYQT6=true
            else
                print_info "PyQt6 not available in system packages, will install via pip"
                SYSTEM_PYQT6=false
            fi
            ;;
        opensuse|suse)
            if ! command_exists sudo; then
                print_error "sudo is required but not installed. Please install sudo or run as root."
                exit 1
            fi
            
            print_info "Installing dependencies for openSUSE..."
            sudo zypper install -y python3 python3-pip acpi curl
            
            # Try to install PyQt6 from system packages
            if sudo zypper install -y python3-qt6 2>/dev/null; then
                print_success "Installed PyQt6 from system packages"
                SYSTEM_PYQT6=true
            else
                print_info "PyQt6 not available in system packages, will install via pip"
                SYSTEM_PYQT6=false
            fi
            ;;
        *)
            print_warning "Unknown distribution '$DISTRO'. Attempting generic installation..."
            
            if ! command_exists python3; then
                print_error "Python 3 is required but not installed. Please install Python 3 and try again."
                exit 1
            fi
            
            if ! command_exists pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
                print_error "pip is required but not installed. Please install python3-pip and try again."
                exit 1
            fi
            
            if ! command_exists acpi; then
                print_error "acpi utility is required but not installed. Please install acpi and try again."
                exit 1
            fi
            
            SYSTEM_PYQT6=false
            ;;
    esac
}

# Function to check Python dependencies
check_python_deps() {
    print_info "Checking Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_VERSION_NUM=$(python3 -c "import sys; print(sys.version_info.major * 100 + sys.version_info.minor)")
    
    if [ "$PYTHON_VERSION_NUM" -lt 308 ]; then
        print_error "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected"
    
    # Check if PyQt6 is available
    if [ "$SYSTEM_PYQT6" = "true" ]; then
        if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
            print_success "System PyQt6 installation verified"
            return 0
        else
            print_warning "System PyQt6 package installed but not working, will use pip"
            SYSTEM_PYQT6=false
        fi
    fi
    
    # Install PyQt6 via pip if system package not available
    if [ "$SYSTEM_PYQT6" = "false" ]; then
        print_info "Installing PyQt6 via pip..."
        
        # Create virtual environment to avoid conflicts
        if [ ! -d "$BATTMON_DIR/venv" ]; then
            python3 -m venv "$BATTMON_DIR/venv"
        fi
        
        source "$BATTMON_DIR/venv/bin/activate"
        pip install --upgrade pip
        pip install "PyQt6>=6.4.0"
        
        if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
            print_success "PyQt6 installed successfully via pip"
        else
            print_error "Failed to install PyQt6. Please check your internet connection and try again."
            exit 1
        fi
    fi
}

# Function to download BattMon files
download_battmon() {
    print_info "Creating BattMon directory..."
    mkdir -p "$BATTMON_DIR"
    
    print_info "Downloading BattMon files from GitHub..."
    
    # Download main application
    if curl -fsSL "$GITHUB_RAW/battmon.py" -o "$BATTMON_DIR/battmon.py"; then
        print_success "Downloaded battmon.py"
    else
        print_error "Failed to download battmon.py"
        exit 1
    fi
    
    # Download Profile Editor module (New in v0.5.12)
    if curl -fsSL "$GITHUB_RAW/profile_editor.py" -o "$BATTMON_DIR/profile_editor.py"; then
        print_success "Downloaded profile_editor.py (Profile Management GUI)"
        chmod +x "$BATTMON_DIR/profile_editor.py"
    else
        print_warning "Failed to download profile_editor.py (Profile Editor will not be available)"
    fi
    
    # Download help file
    if curl -fsSL "$GITHUB_RAW/HELP.md" -o "$BATTMON_DIR/HELP.md"; then
        print_success "Downloaded HELP.md"
    else
        print_warning "Failed to download HELP.md (help system will use fallback)"
    fi
    
    # Download animated GIF assets (New in v0.5.13)
    print_info "Downloading animated GIF assets..."
    mkdir -p "$BATTMON_DIR/Images"
    
    # Download animated battery cycle GIF for About dialog
    if curl -fsSL "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/animated_battery_cycle_slow.gif" -o "$BATTMON_DIR/Images/animated_battery_cycle_slow.gif"; then
        print_success "Downloaded animated_battery_cycle_slow.gif (About dialog animation)"
    else
        print_warning "Failed to download animated GIF assets (About dialog will use static fallback)"
    fi
    
    # Optionally download screenshot assets
    if curl -fsSL "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/About_window.png" -o "$BATTMON_DIR/Images/About_window.png" 2>/dev/null; then
        print_success "Downloaded About_window.png"
    else
        print_info "About_window.png not downloaded (optional)"
    fi
    
    if curl -fsSL "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/Status_window.png" -o "$BATTMON_DIR/Images/Status_window.png" 2>/dev/null; then
        print_success "Downloaded Status_window.png"
    else
        print_info "Status_window.png not downloaded (optional)"
    fi
    
    # Make the main script executable
    chmod +x "$BATTMON_DIR/battmon.py"
}

# Function to create launcher script
create_launcher() {
    print_info "Creating launcher script..."
    
    mkdir -p "$BIN_DIR"
    
    # Create launcher script
    cat > "$BIN_DIR/battmon" << EOF
#!/bin/bash
# BattMon Cross-Platform Launcher Script

BATTMON_DIR="\$HOME/.local/share/battmon"
VENV_DIR="\$BATTMON_DIR/venv"

# Check if we need to use virtual environment
if [ -d "\$VENV_DIR" ]; then
    source "\$VENV_DIR/bin/activate"
    python3 "\$BATTMON_DIR/battmon.py" "\$@"
else
    python3 "\$BATTMON_DIR/battmon.py" "\$@"
fi
EOF
    
    chmod +x "$BIN_DIR/battmon"
    print_success "Created launcher script at $BIN_DIR/battmon"
}

# Function to create desktop entry
create_desktop_entry() {
    print_info "Creating desktop entry..."
    
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=BattMon Cross-Platform
Comment=Battery Monitor for Linux with system tray integration
Exec=$BIN_DIR/battmon
Icon=battery
Terminal=false
Type=Application
Categories=System;Monitor;Utility;
Keywords=battery;power;monitor;system;tray;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF
    
    print_success "Created desktop entry at $DESKTOP_FILE"
}

# Function to update PATH
update_path() {
    # Check if ~/.local/bin is already in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        print_info "Adding $BIN_DIR to PATH..."
        
        # Add to .bashrc
        if [ -f "$HOME/.bashrc" ]; then
            echo "" >> "$HOME/.bashrc"
            echo "# Added by BattMon installer" >> "$HOME/.bashrc"
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
        fi
        
        # Add to .profile
        if [ -f "$HOME/.profile" ]; then
            echo "" >> "$HOME/.profile"
            echo "# Added by BattMon installer" >> "$HOME/.profile"
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.profile"
        fi
        
        export PATH="$BIN_DIR:$PATH"
        print_success "Added $BIN_DIR to PATH"
        print_info "You may need to restart your terminal or run 'source ~/.bashrc'"
    fi
}

# Function to test installation
test_installation() {
    print_info "Testing BattMon installation..."
    
    # Test main application
    if [ -f "$BATTMON_DIR/battmon.py" ]; then
        print_success "Main application (battmon.py) verified"
    else
        print_error "BattMon script not found"
        return 1
    fi
    
    # Test Profile Editor module (v0.5.12+)
    if [ -f "$BATTMON_DIR/profile_editor.py" ]; then
        print_success "Profile Editor module (profile_editor.py) verified"
    else
        print_warning "Profile Editor module not found (GUI configuration will not be available)"
    fi
    
    # Test animated GIF assets (v0.5.13+)
    if [ -f "$BATTMON_DIR/Images/animated_battery_cycle_slow.gif" ]; then
        print_success "Animated GIF assets verified"
    else
        print_warning "Animated GIF not found (About dialog will use static fallback)"
    fi
    
    # Test PyQt6 and QMovie support
    if python3 -c "
import sys
sys.path.insert(0, '$BATTMON_DIR')
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QMovie
    print('PyQt6 and QMovie import successful')
except ImportError as e:
    print(f'PyQt6 or QMovie import failed: {e}')
    sys.exit(1)
    " 2>/dev/null; then
        print_success "PyQt6 and QMovie support verified"
    else
        print_error "BattMon dependency check failed"
        return 1
    fi
    
    # Test ACPI
    if command_exists acpi; then
        if acpi -b >/dev/null 2>&1; then
            print_success "ACPI battery detection working"
        else
            print_warning "ACPI battery detection may not work properly"
        fi
    else
        print_warning "ACPI utility not found - battery detection may not work"
    fi
    
    return 0
}

# Function to show usage instructions
show_usage_instructions() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_success "BattMon Cross-Platform has been installed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}📍 Installation Location:${NC} $BATTMON_DIR"
    echo -e "${BLUE}🚀 Launch Command:${NC} battmon"
    echo -e "${BLUE}🖥️  Desktop Entry:${NC} Search for 'BattMon' in your application menu"
    echo ""
    echo -e "${GREEN}How to run BattMon:${NC}"
    echo "  1. From terminal: ${YELLOW}battmon${NC}"
    echo "  2. From application menu: Search for 'BattMon Cross-Platform'"
    echo "  3. Add to startup: Use your DE's startup applications settings"
    echo ""
    echo -e "${GREEN}Features (v0.5.13):${NC}"
    echo "  • System tray battery monitoring with percentage display"
    echo "  • Color-coded battery levels (Red/Orange/Yellow/Green)"
    echo "  • Desktop notifications for battery milestones"
    echo "  • Detailed battery health information window"
    echo "  • 🔧 Profile Editor GUI for settings management (NEW)"
    echo "  • 🎬 Animated GIF demonstrations in About dialog (NEW)"
    echo "  • 💻 Persistent QDialog battery status window (NEW)"
    echo "  • 📖 Professional help system with documentation (NEW)"
    echo "  • Cross-platform compatibility (Linux, Windows, macOS)"
    echo "  • Charging indicators and time remaining estimates"
    echo ""
    echo -e "${GREEN}Usage:${NC}"
    echo "  • Left-click tray icon: Show/hide detailed battery window"
    echo "  • Right-click tray icon: Context menu with Profile Editor"
    echo "  • Hover over tray icon: Battery status tooltip"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Start BattMon: ${YELLOW}battmon${NC}"
    echo "  2. Look for the battery icon in your system tray"
    echo "  3. Add to startup applications for automatic launch"
    echo ""
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        print_info "Note: Restart your terminal or run 'source ~/.bashrc' to use the 'battmon' command"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main installation function
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}🔋 BattMon Cross-Platform Linux Installer${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This installer will:"
    echo "  • Install system dependencies (Python 3, PyQt6, ACPI)"
    echo "  • Download BattMon files from GitHub"
    echo "  • Create launcher script and desktop entry"
    echo "  • Set up proper PATH configuration"
    echo ""
    
    # Check if we have internet connectivity
    if ! curl -fsSL --max-time 5 https://github.com >/dev/null 2>&1; then
        print_error "No internet connection detected. Please check your connection and try again."
        exit 1
    fi
    
    # Check for required tools
    if ! command_exists curl; then
        print_error "curl is required but not installed. Please install curl and try again."
        exit 1
    fi
    
    print_info "Starting installation process..."
    echo ""
    
    # Install system dependencies
    install_system_deps
    echo ""
    
    # Check Python dependencies
    check_python_deps
    echo ""
    
    # Download BattMon files
    download_battmon
    echo ""
    
    # Create launcher and desktop entry
    create_launcher
    create_desktop_entry
    echo ""
    
    # Update PATH
    update_path
    echo ""
    
    # Test installation
    if test_installation; then
        echo ""
        show_usage_instructions
    else
        print_error "Installation test failed. Please check the error messages above."
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo ""; print_error "Installation cancelled by user"; exit 1' INT

# Run main installation
main "$@"

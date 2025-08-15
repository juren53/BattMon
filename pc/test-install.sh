#!/bin/bash
# BattMon Cross-Platform Linux Installation TEST Script
# Test version that doesn't affect your system - installs to temporary location

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Use test directory instead of system locations
TEST_DIR="/tmp/battmon-test-$(date +%s)"
BATTMON_DIR="$TEST_DIR/battmon"
DESKTOP_FILE="$TEST_DIR/battmon.desktop"
BIN_DIR="$TEST_DIR/bin"
GITHUB_RAW="https://raw.githubusercontent.com/juren53/BattMon/main/pc"
# For testing, use local files instead of GitHub
USE_LOCAL_FILES=true

# Function to print colored output
print_info() {
    echo -e "${BLUE}[TEST INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[TEST SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[TEST WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[TEST ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect distribution (simplified for test)
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_LIKE=$ID_LIKE
    else
        DISTRO="unknown"
        DISTRO_LIKE=""
    fi
    print_info "Detected Linux distribution: $DISTRO"
}

# Function to check Python dependencies (no system packages installed)
check_python_deps() {
    print_info "Checking Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_VERSION_NUM=$(python3 -c "import sys; print(sys.version_info.major * 100 + sys.version_info.minor)")
    
    if [ "$PYTHON_VERSION_NUM" -lt 308 ]; then
        print_warning "Python 3.8 or higher is recommended. Found Python $PYTHON_VERSION"
        # Continue anyway for testing
    else
        print_success "Python $PYTHON_VERSION detected"
    fi
    
    # Create test virtual environment
    print_info "Creating test virtual environment..."
    python3 -m venv "$BATTMON_DIR/venv"
    source "$BATTMON_DIR/venv/bin/activate"
    pip install --upgrade pip
    
    # Install PyQt6 in test environment
    print_info "Installing PyQt6 in test environment..."
    pip install "PyQt6>=6.4.0"
    
    if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
        print_success "PyQt6 installed successfully in test environment"
    else
        print_error "Failed to install PyQt6 in test environment"
        return 1
    fi
}

# Function to copy BattMon files
copy_battmon_files() {
    print_info "Creating test BattMon directory..."
    mkdir -p "$BATTMON_DIR"
    
    if [ "$USE_LOCAL_FILES" = true ]; then
        print_info "Copying local BattMon files to test directory..."
        
        # Copy main application
        if cp "$(pwd)/battmon.py" "$BATTMON_DIR/battmon.py"; then
            print_success "Copied battmon.py to test directory"
        else
            print_error "Failed to copy battmon.py"
            exit 1
        fi
        
        # Copy help file
        if cp "$(pwd)/HELP.md" "$BATTMON_DIR/HELP.md" 2>/dev/null; then
            print_success "Copied HELP.md to test directory"
        else
            print_warning "Failed to copy HELP.md (help system will use fallback)"
        fi
    else
        print_info "Downloading BattMon files from GitHub..."
        
        # Download main application
        if curl -fsSL "$GITHUB_RAW/battmon.py" -o "$BATTMON_DIR/battmon.py"; then
            print_success "Downloaded battmon.py to test directory"
        else
            print_error "Failed to download battmon.py"
            exit 1
        fi
        
        # Download help file
        if curl -fsSL "$GITHUB_RAW/HELP.md" -o "$BATTMON_DIR/HELP.md"; then
            print_success "Downloaded HELP.md to test directory"
        else
            print_warning "Failed to download HELP.md (help system will use fallback)"
        fi
    fi
    
    # Make the main script executable
    chmod +x "$BATTMON_DIR/battmon.py"
}

# Function to create test launcher script
create_test_launcher() {
    print_info "Creating test launcher script..."
    
    mkdir -p "$BIN_DIR"
    
    # Create launcher script
    cat > "$BIN_DIR/battmon" << EOF
#!/bin/bash
# BattMon Cross-Platform TEST Launcher Script

BATTMON_DIR="$BATTMON_DIR"
VENV_DIR="\$BATTMON_DIR/venv"

# Activate test virtual environment
source "\$VENV_DIR/bin/activate"
python3 "\$BATTMON_DIR/battmon.py" "\$@"
EOF
    
    chmod +x "$BIN_DIR/battmon"
    print_success "Created test launcher script at $BIN_DIR/battmon"
}

# Function to create test desktop entry (not actually installed)
create_test_desktop_entry() {
    print_info "Creating test desktop entry (not installed to system)..."
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=BattMon Cross-Platform (TEST)
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
    
    print_success "Created test desktop entry at $DESKTOP_FILE"
    print_warning "NOTE: This desktop entry is not installed to your system"
}

# Function to test the installation
test_installation() {
    print_info "Testing BattMon installation in test environment..."
    
    # Test if the script can run
    if [ -f "$BATTMON_DIR/battmon.py" ]; then
        # Activate test virtual environment
        source "$BATTMON_DIR/venv/bin/activate"
        
        if python3 -c "
import sys
sys.path.insert(0, '$BATTMON_DIR')
try:
    from PyQt6.QtWidgets import QApplication
    print('PyQt6 import successful')
except ImportError as e:
    print(f'PyQt6 import failed: {e}')
    sys.exit(1)
        " 2>/dev/null; then
            print_success "BattMon dependencies verified in test environment"
        else
            print_error "BattMon dependency check failed in test environment"
            return 1
        fi
    else
        print_error "BattMon script not found in test directory"
        return 1
    fi
    
    # Test ACPI availability (don't exit on failure)
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

# Function to run BattMon in test environment
run_test_battmon() {
    print_info "Running BattMon from test environment..."
    print_info "This will launch BattMon in a new window. Close it when finished testing."
    print_info "Press Ctrl+C in this terminal to exit the test."
    
    source "$BATTMON_DIR/venv/bin/activate"
    "$BIN_DIR/battmon"
}

# Function to show test results
show_test_results() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_success "BattMon Test Installation Completed Successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}📍 Test Installation Location:${NC} $BATTMON_DIR"
    echo -e "${BLUE}🚀 Test Launch Command:${NC} $BIN_DIR/battmon"
    echo ""
    echo -e "${GREEN}Test Environment Files:${NC}"
    echo "  • Main application: $BATTMON_DIR/battmon.py"
    echo "  • Help file: $BATTMON_DIR/HELP.md"
    echo "  • Virtual environment: $BATTMON_DIR/venv"
    echo "  • Launcher script: $BIN_DIR/battmon"
    echo "  • Desktop entry (not installed): $DESKTOP_FILE"
    echo ""
    echo -e "${YELLOW}To test BattMon from this environment:${NC}"
    echo "  $BIN_DIR/battmon"
    echo ""
    echo -e "${YELLOW}To clean up this test installation:${NC}"
    echo "  rm -rf $TEST_DIR"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to clean up test files
cleanup_test() {
    print_info "Cleaning up test installation..."
    rm -rf "$TEST_DIR"
    print_success "Test installation removed"
}

# Main test function
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}🔋 BattMon Cross-Platform Test Installer${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}⚠️ TEST MODE: No system files will be modified${NC}"
    echo ""
    echo "This test installer will:"
    echo "  • Create a temporary directory at $TEST_DIR"
    echo "  • Install PyQt6 in a test virtual environment"
    echo "  • Copy BattMon files to the test directory"
    echo "  • Create test launcher script and desktop entry (not installed)"
    echo "  • Verify the installation works without modifying your system"
    echo ""
    
    # Check for required tools
    if ! command_exists python3; then
        print_error "Python 3 is required for testing but not installed."
        exit 1
    fi
    
    if ! command_exists venv; then
        print_warning "Python venv module not found, trying to install..."
        sudo apt install python3-venv -y || true
    fi
    
    print_info "Starting test installation process..."
    echo ""
    
    # Detect distribution
    detect_distro
    echo ""
    
    # Copy BattMon files
    copy_battmon_files
    echo ""
    
    # Check Python dependencies
    check_python_deps
    echo ""
    
    # Create launcher and desktop entry
    create_test_launcher
    create_test_desktop_entry
    echo ""
    
    # Test installation
    if test_installation; then
        echo ""
        show_test_results
        
        # Ask if user wants to run BattMon in test environment
        echo -n -e "${YELLOW}Do you want to run BattMon from the test environment? (y/n)${NC} "
        read -r run_choice
        if [[ $run_choice =~ ^[Yy]$ ]]; then
            run_test_battmon
        fi
        
        # Ask if user wants to clean up test files
        echo -n -e "${YELLOW}Do you want to clean up the test installation? (y/n)${NC} "
        read -r cleanup_choice
        if [[ $cleanup_choice =~ ^[Yy]$ ]]; then
            cleanup_test
        else
            echo ""
            print_info "Test installation remains at $TEST_DIR"
            print_info "You can remove it later with: rm -rf $TEST_DIR"
        fi
    else
        print_error "Test installation failed. Please check the error messages above."
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo ""; print_error "Test installation cancelled by user"; cleanup_test; exit 1' INT

# Run main test function
main "$@"

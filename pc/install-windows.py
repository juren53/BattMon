#!/usr/bin/env python3
"""
BattMon Cross-Platform Windows Installation Script (Python Version)
Version 1.0 - Installs BattMon without cloning the entire repository
Alternative to PowerShell script for users with restricted execution policies
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
import json
import tempfile
import shutil
import winreg
from pathlib import Path

# Configuration
GITHUB_RAW = "https://raw.githubusercontent.com/juren53/BattMon/main/pc"
PYTHON_MIN_VERSION = (3, 8)
INSTALL_DIR = Path(os.environ['LOCALAPPDATA']) / 'BattMon'
START_MENU_DIR = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'

# ANSI color codes for Windows
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m' 
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @staticmethod
    def init_windows_colors():
        """Enable ANSI color support on Windows"""
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def print_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.END} {message}")

def print_header(message):
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")

def check_internet():
    """Check if we have internet connectivity"""
    try:
        urllib.request.urlopen('https://github.com', timeout=10)
        return True
    except urllib.error.URLError:
        return False

def check_python_version():
    """Check if Python version meets requirements"""
    current_version = sys.version_info[:2]
    if current_version >= PYTHON_MIN_VERSION:
        print_success(f"Python {sys.version.split()[0]} detected")
        return True
    else:
        print_error(f"Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+ required, found {current_version[0]}.{current_version[1]}")
        return False

def install_pyqt6():
    """Install PyQt6 using pip"""
    print_info("Installing PyQt6...")
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True, text=True)
        
        # Install PyQt6
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyQt6>=6.4.0'], 
                      check=True, capture_output=True, text=True)
        
        # Test PyQt6 import
        subprocess.run([sys.executable, '-c', 'from PyQt6.QtWidgets import QApplication'], 
                      check=True, capture_output=True, text=True)
        
        print_success("PyQt6 installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install PyQt6: {e}")
        if e.stderr:
            print_error(f"Error details: {e.stderr}")
        return False

def install_optional_deps():
    """Install optional Windows dependencies"""
    try:
        response = input("Install optional Windows enhancements (WMI for detailed battery info)? [y/N]: ")
        if response.lower() == 'y':
            print_info("Installing optional Windows dependencies...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'WMI'], 
                          check=True, capture_output=True, text=True)
            print_success("WMI module installed for enhanced battery information")
    except subprocess.CalledProcessError:
        print_warning("Failed to install WMI module")
    except KeyboardInterrupt:
        print_warning("\nOptional dependency installation skipped")

def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        with urllib.request.urlopen(url) as response:
            with open(destination, 'wb') as f:
                shutil.copyfileobj(response, f)
        return True
    except urllib.error.URLError as e:
        print_error(f"Failed to download {url}: {e}")
        return False

def download_battmon_files():
    """Download BattMon files from GitHub"""
    print_info(f"Creating BattMon directory: {INSTALL_DIR}")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    files_to_download = [
        ('battmon.py', 'battmon.py'),
        ('HELP.md', 'HELP.md'),
        ('requirements-windows.txt', 'requirements-windows.txt')
    ]
    
    print_info("Downloading BattMon files from GitHub...")
    
    for filename, local_name in files_to_download:
        url = f"{GITHUB_RAW}/{filename}"
        destination = INSTALL_DIR / local_name
        
        if download_file(url, destination):
            print_success(f"Downloaded {filename}")
        else:
            if filename == 'battmon.py':
                print_error(f"Failed to download required file: {filename}")
                return False
            else:
                print_warning(f"Failed to download optional file: {filename}")
    
    return True

def create_launcher_scripts():
    """Create launcher scripts for BattMon"""
    print_info("Creating launcher scripts...")
    
    # Create batch launcher
    batch_launcher = INSTALL_DIR / 'battmon.bat'
    batch_content = f'''@echo off
cd /d "{INSTALL_DIR}"
"{sys.executable}" "{INSTALL_DIR / 'battmon.py'}" %*
'''
    
    with open(batch_launcher, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print_success(f"Created batch launcher: {batch_launcher}")
    
    # Create Python launcher
    py_launcher = INSTALL_DIR / 'battmon_launcher.py'
    py_content = f'''#!/usr/bin/env python3
"""BattMon Cross-Platform Windows Launcher"""
import os
import sys
import subprocess

os.chdir(r"{INSTALL_DIR}")
subprocess.run([sys.executable, r"{INSTALL_DIR / 'battmon.py'}"] + sys.argv[1:])
'''
    
    with open(py_launcher, 'w', encoding='utf-8') as f:
        f.write(py_content)
    
    print_success(f"Created Python launcher: {py_launcher}")
    
    return batch_launcher

def create_start_menu_shortcut():
    """Create Start Menu shortcut"""
    print_info("Creating Start Menu shortcut...")
    
    try:
        import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = START_MENU_DIR / "BattMon Cross-Platform.lnk"
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{INSTALL_DIR / "battmon.py"}"'
        shortcut.WorkingDirectory = str(INSTALL_DIR)
        shortcut.Description = "BattMon Cross-Platform - Battery Monitor"
        shortcut.IconLocation = f"{os.environ['SystemRoot']}\\System32\\batmeter.dll,0"
        shortcut.save()
        
        print_success(f"Created Start Menu shortcut: {shortcut_path}")
        return True
        
    except ImportError:
        print_warning("win32com not available, creating shortcut manually...")
        
        # Alternative method without win32com
        try:
            import subprocess
            powershell_cmd = f'''
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("{START_MENU_DIR / "BattMon Cross-Platform.lnk"}")
$shortcut.TargetPath = "{sys.executable}"
$shortcut.Arguments = '"{INSTALL_DIR / "battmon.py"}"'
$shortcut.WorkingDirectory = "{INSTALL_DIR}"
$shortcut.Description = "BattMon Cross-Platform - Battery Monitor"
$shortcut.IconLocation = "$env:SystemRoot\\System32\\batmeter.dll,0"
$shortcut.Save()
'''
            subprocess.run(['powershell', '-Command', powershell_cmd], 
                          check=True, capture_output=True, text=True)
            print_success("Created Start Menu shortcut via PowerShell")
            return True
        except subprocess.CalledProcessError:
            print_warning("Failed to create Start Menu shortcut")
            return False

def add_to_path():
    """Add BattMon directory to user PATH"""
    try:
        response = input("Add BattMon to PATH for easy command-line access? [y/N]: ")
        if response.lower() == 'y':
            try:
                # Read current user PATH
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE)
                try:
                    current_path, _ = winreg.QueryValueEx(key, 'Path')
                except FileNotFoundError:
                    current_path = ''
                
                install_dir_str = str(INSTALL_DIR)
                if install_dir_str not in current_path:
                    new_path = f"{current_path};{install_dir_str}" if current_path else install_dir_str
                    winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                    print_success(f"Added {install_dir_str} to user PATH")
                    print_warning("Restart your command prompt/PowerShell to use 'battmon.bat' command")
                else:
                    print_info(f"{install_dir_str} already in PATH")
                
                winreg.CloseKey(key)
                
            except Exception as e:
                print_warning(f"Failed to add to PATH: {e}")
                
    except KeyboardInterrupt:
        print_warning("\nPATH modification skipped")

def test_installation():
    """Test that BattMon installation works"""
    print_info("Testing BattMon installation...")
    
    try:
        battmon_path = INSTALL_DIR / 'battmon.py'
        if not battmon_path.exists():
            print_error("battmon.py not found")
            return False
        
        # Test PyQt6 import
        result = subprocess.run([
            sys.executable, '-c', 
            'from PyQt6.QtWidgets import QApplication; print("Dependencies verified")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("BattMon installation verified")
            return True
        else:
            print_error("PyQt6 import test failed")
            if result.stderr:
                print_error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Installation test failed: {e}")
        return False

def show_completion_message():
    """Show installation completion message"""
    print()
    print("━" * 80)
    print_success("BattMon Cross-Platform has been installed successfully!")
    print("━" * 80)
    print()
    print_info(f"📍 Installation Location: {INSTALL_DIR}")
    print_info(f"🐍 Python Version: {sys.version.split()[0]}")
    print()
    print_header("🚀 How to run BattMon:")
    print("  1. Start Menu: Search for 'BattMon Cross-Platform'")
    print(f"  2. Command Prompt: python \"{INSTALL_DIR / 'battmon.py'}\"")
    print(f"  3. Batch file: \"{INSTALL_DIR / 'battmon.bat'}\"")
    print(f"  4. Double-click: {INSTALL_DIR / 'battmon.py'}")
    print()
    print_header("✨ Features:")
    print("  • System tray battery monitoring with percentage display")
    print("  • Color-coded battery levels and charging indicators")
    print("  • Desktop notifications for battery milestones")
    print("  • Detailed battery health information")
    print("  • Cross-platform compatibility (Windows, Linux, macOS)")
    print()
    print_header("🎯 Usage:")
    print("  • Left-click tray icon: Show detailed battery window")
    print("  • Right-click tray icon: Context menu with options")
    print("  • System tray icon shows real-time battery percentage")
    print()
    print_warning("🔄 To update BattMon, simply re-run this installer")
    print("━" * 80)

def main():
    """Main installation function"""
    Colors.init_windows_colors()
    
    print("━" * 80)
    print_header("🔋 BattMon Cross-Platform Windows Installer (Python)")
    print("━" * 80)
    print()
    print("This installer will:")
    print("  • Verify Python 3.8+ installation")
    print("  • Install PyQt6 and dependencies")
    print("  • Download BattMon files from GitHub")
    print("  • Create launcher scripts and Start Menu shortcut")
    print("  • Configure system integration")
    print()
    
    try:
        # Check Python version
        if not check_python_version():
            print_error("Please install Python 3.8+ and run this script again")
            print_info("Download from: https://www.python.org/downloads/")
            return 1
        
        # Check internet connection
        print_info("Checking internet connection...")
        if not check_internet():
            print_error("No internet connection detected. Please check your connection and try again.")
            return 1
        print_success("Internet connection verified")
        
        # Install PyQt6
        if not install_pyqt6():
            return 1
        
        # Install optional dependencies
        install_optional_deps()
        
        # Download BattMon files
        if not download_battmon_files():
            return 1
        
        # Create launcher scripts
        launcher_path = create_launcher_scripts()
        
        # Create Start Menu shortcut
        create_start_menu_shortcut()
        
        # Add to PATH
        add_to_path()
        
        # Test installation
        if not test_installation():
            return 1
        
        # Show completion message
        show_completion_message()
        
        # Ask to run BattMon
        try:
            run_now = input("\nWould you like to start BattMon now? [y/N]: ")
            if run_now.lower() == 'y':
                print_info("Starting BattMon...")
                subprocess.Popen([sys.executable, str(INSTALL_DIR / 'battmon.py')], 
                               cwd=str(INSTALL_DIR))
        except KeyboardInterrupt:
            print_warning("\nStartup skipped")
        
        return 0
        
    except KeyboardInterrupt:
        print()
        print_error("Installation cancelled by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

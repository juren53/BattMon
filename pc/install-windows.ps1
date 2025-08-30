# BattMon Cross-Platform Windows Installation Script
# Version 1.1 - Installs BattMon v0.5.13 with Profile Editor and animated GIF features
# Designed for BattMon v0.5.13 (August 2025) - includes Profile Management GUI and visual enhancements
# Supports Windows 10/11 with PowerShell 5.1+
#
# New in this version:
# - Downloads profile_editor.py module for GUI configuration management
# - Downloads animated GIF assets for enhanced About dialog
# - Supports all features added in BattMon v0.5.9 through v0.5.13

param(
    [switch]$NoInteractive,
    [switch]$InstallPython,
    [switch]$TestMode,
    [string]$InstallPath = "$env:LOCALAPPDATA\BattMon"
)

# Set error handling
$ErrorActionPreference = "Stop"

# Configuration
$GitHubRaw = "https://raw.githubusercontent.com/juren53/BattMon/main/pc"
$PythonMinVersion = [Version]"3.8.0"
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"

# Color functions for better output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-InternetConnection {
    try {
        $response = Invoke-WebRequest -Uri "https://github.com" -Method Head -TimeoutSec 10 -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Get-PythonInstallation {
    $pythonPaths = @()
    
    # Check common Python installation paths
    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "$env:PROGRAMFILES\Python*\python.exe",
        "${env:PROGRAMFILES(x86)}\Python*\python.exe"
    )
    
    foreach ($path in $commonPaths) {
        $pythonPaths += Get-ChildItem -Path $path -ErrorAction SilentlyContinue
    }
    
    # Check PATH
    try {
        $pathPython = Get-Command python -ErrorAction SilentlyContinue
        if ($pathPython) {
            $pythonPaths += $pathPython.Source
        }
    }
    catch { }
    
    # Check each Python installation
    foreach ($python in $pythonPaths) {
        try {
            $version = & $python.FullName --version 2>&1
            if ($version -match "Python (\d+\.\d+\.\d+)") {
                $pythonVersion = [Version]$matches[1]
                if ($pythonVersion -ge $PythonMinVersion) {
                    return @{
                        Path = $python.FullName
                        Version = $pythonVersion
                    }
                }
            }
        }
        catch { }
    }
    
    return $null
}

function Install-Python {
    Write-Info "Python 3.8+ not found. Installing Python from Microsoft Store..."
    
    if (-not (Test-AdminPrivileges)) {
        Write-Warning "Installing Python requires administrator privileges or Microsoft Store access."
        Write-Info "Please install Python 3.8+ manually from:"
        Write-Info "  1. Microsoft Store: search for 'Python 3.11'"
        Write-Info "  2. Python.org: https://www.python.org/downloads/"
        return $false
    }
    
    try {
        # Try to install via winget (Windows Package Manager)
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Info "Installing Python via Windows Package Manager..."
            winget install --id Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
            
            # Wait a moment for installation to complete
            Start-Sleep -Seconds 5
            
            # Verify installation
            $python = Get-PythonInstallation
            if ($python) {
                Write-Success "Python $($python.Version) installed successfully"
                return $true
            }
        }
        else {
            Write-Warning "Windows Package Manager (winget) not available"
        }
    }
    catch {
        Write-Warning "Automatic Python installation failed: $_"
    }
    
    Write-Error-Custom "Please install Python 3.8+ manually and run this script again"
    return $false
}

function Install-PyQt6 {
    param([string]$PythonPath)
    
    Write-Info "Installing PyQt6..."
    
    try {
        # Upgrade pip first
        & $PythonPath -m pip install --upgrade pip --quiet
        
        # Install PyQt6
        & $PythonPath -m pip install "PyQt6>=6.4.0" --quiet
        
        # Test PyQt6 installation
        & $PythonPath -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 import successful')" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PyQt6 installed successfully"
            return $true
        }
        else {
            throw "PyQt6 import test failed"
        }
    }
    catch {
        Write-Error-Custom "Failed to install PyQt6: $_"
        return $false
    }
}

function Install-OptionalDependencies {
    param([string]$PythonPath)
    
    if (-not $NoInteractive) {
        $install = Read-Host "Install optional Windows enhancements (WMI for detailed battery info)? [y/N]"
        if ($install -eq "y" -or $install -eq "Y") {
            Write-Info "Installing optional Windows dependencies..."
            try {
                & $PythonPath -m pip install WMI --quiet
                Write-Success "WMI module installed for enhanced battery information"
            }
            catch {
                Write-Warning "Failed to install WMI module: $_"
            }
        }
    }
}

function Download-BattMonFiles {
    Write-Info "Creating BattMon directory: $InstallPath"
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    
    try {
        Write-Info "Downloading BattMon files from GitHub..."
        
        # Download main application
        $battmonUrl = "$GitHubRaw/battmon.py"
        $battmonPath = Join-Path $InstallPath "battmon.py"
        Invoke-WebRequest -Uri $battmonUrl -OutFile $battmonPath -UseBasicParsing
        Write-Success "Downloaded battmon.py"
        
        # Download Profile Editor module (New in v0.5.12)
        try {
            $profileEditorUrl = "$GitHubRaw/profile_editor.py"
            $profileEditorPath = Join-Path $InstallPath "profile_editor.py"
            Invoke-WebRequest -Uri $profileEditorUrl -OutFile $profileEditorPath -UseBasicParsing
            Write-Success "Downloaded profile_editor.py (Profile Management GUI)"
        }
        catch {
            Write-Warning "Failed to download profile_editor.py (Profile Editor will not be available)"
        }
        
        # Download help file
        try {
            $helpUrl = "$GitHubRaw/HELP.md"
            $helpPath = Join-Path $InstallPath "HELP.md"
            Invoke-WebRequest -Uri $helpUrl -OutFile $helpPath -UseBasicParsing
            Write-Success "Downloaded HELP.md"
        }
        catch {
            Write-Warning "Failed to download HELP.md (help system will use fallback)"
        }
        
        # Download requirements file
        try {
            $reqUrl = "$GitHubRaw/requirements-windows.txt"
            $reqPath = Join-Path $InstallPath "requirements-windows.txt"
            Invoke-WebRequest -Uri $reqUrl -OutFile $reqPath -UseBasicParsing
            Write-Success "Downloaded requirements-windows.txt"
        }
        catch {
            Write-Warning "Failed to download requirements file"
        }
        
        # Download animated GIF assets (New in v0.5.13)
        try {
            Write-Info "Downloading animated GIF assets..."
            $imagesDir = Join-Path $InstallPath "Images"
            New-Item -ItemType Directory -Path $imagesDir -Force | Out-Null
            
            # Download animated battery cycle GIF for About dialog
            $gifUrl = "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/animated_battery_cycle_slow.gif"
            $gifPath = Join-Path $imagesDir "animated_battery_cycle_slow.gif"
            Invoke-WebRequest -Uri $gifUrl -OutFile $gifPath -UseBasicParsing
            Write-Success "Downloaded animated_battery_cycle_slow.gif (About dialog animation)"
            
            # Optionally download other image assets
            try {
                $aboutPngUrl = "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/About_window.png"
                $aboutPngPath = Join-Path $imagesDir "About_window.png"
                Invoke-WebRequest -Uri $aboutPngUrl -OutFile $aboutPngPath -UseBasicParsing
                Write-Success "Downloaded About_window.png"
            }
            catch {
                Write-Info "About_window.png not downloaded (optional)"
            }
            
            try {
                $statusPngUrl = "https://raw.githubusercontent.com/juren53/BattMon/main/pc/Images/Status_window.png"
                $statusPngPath = Join-Path $imagesDir "Status_window.png"
                Invoke-WebRequest -Uri $statusPngUrl -OutFile $statusPngPath -UseBasicParsing
                Write-Success "Downloaded Status_window.png"
            }
            catch {
                Write-Info "Status_window.png not downloaded (optional)"
            }
        }
        catch {
            Write-Warning "Failed to download animated GIF assets (About dialog will use static fallback)"
        }
        
        return $true
    }
    catch {
        Write-Error-Custom "Failed to download BattMon files: $_"
        return $false
    }
}

function Create-LauncherScript {
    param([string]$PythonPath)
    
    Write-Info "Creating launcher script..."
    
    # Create batch launcher
    $batchPath = Join-Path $InstallPath "battmon.bat"
    $batchContent = @"
@echo off
cd /d "$InstallPath"
"$PythonPath" "$InstallPath\battmon.py" %*
"@
    
    Set-Content -Path $batchPath -Value $batchContent -Encoding UTF8
    Write-Success "Created launcher: $batchPath"
    
    # Create PowerShell launcher  
    $ps1Path = Join-Path $InstallPath "battmon.ps1"
    $ps1Content = @"
# BattMon Cross-Platform Windows Launcher
Set-Location "$InstallPath"
& "$PythonPath" "$InstallPath\battmon.py" @args
"@
    
    Set-Content -Path $ps1Path -Value $ps1Content -Encoding UTF8
    Write-Success "Created PowerShell launcher: $ps1Path"
    
    return $batchPath
}

function Create-StartMenuShortcut {
    param([string]$LauncherPath, [string]$PythonPath)
    
    Write-Info "Creating Start Menu shortcut..."
    
    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcutPath = Join-Path $StartMenuPath "BattMon Cross-Platform.lnk"
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $PythonPath
        $shortcut.Arguments = "`"$InstallPath\battmon.py`""
        $shortcut.WorkingDirectory = $InstallPath
        $shortcut.Description = "BattMon Cross-Platform - Battery Monitor"
        $shortcut.IconLocation = "$env:SystemRoot\System32\batmeter.dll,0"  # Battery icon
        $shortcut.Save()
        
        Write-Success "Created Start Menu shortcut: $shortcutPath"
        return $true
    }
    catch {
        Write-Warning "Failed to create Start Menu shortcut: $_"
        return $false
    }
}

function Add-ToPath {
    param([string]$Directory)
    
    if (-not $NoInteractive) {
        $addPath = Read-Host "Add BattMon to PATH for easy command-line access? [y/N]"
        if ($addPath -eq "y" -or $addPath -eq "Y") {
            try {
                $userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
                if ($userPath -notlike "*$Directory*") {
                    $newPath = "$userPath;$Directory"
                    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
                    Write-Success "Added $Directory to user PATH"
                    Write-Warning "Restart your terminal/PowerShell to use 'battmon.bat' command"
                }
                else {
                    Write-Info "$Directory already in PATH"
                }
            }
            catch {
                Write-Warning "Failed to add to PATH: $_"
            }
        }
    }
}

function Test-Installation {
    param([string]$PythonPath)
    
    Write-Info "Testing BattMon installation..."
    
    try {
        # Test main application
        $battmonPath = Join-Path $InstallPath "battmon.py"
        if (-not (Test-Path $battmonPath)) {
            throw "battmon.py not found"
        }
        Write-Success "Main application (battmon.py) verified"
        
        # Test Profile Editor module (v0.5.12+)
        $profileEditorPath = Join-Path $InstallPath "profile_editor.py"
        if (Test-Path $profileEditorPath) {
            Write-Success "Profile Editor module (profile_editor.py) verified"
        }
        else {
            Write-Warning "Profile Editor module not found (GUI configuration will not be available)"
        }
        
        # Test animated GIF assets (v0.5.13+)
        $gifPath = Join-Path $InstallPath "Images\animated_battery_cycle_slow.gif"
        if (Test-Path $gifPath) {
            Write-Success "Animated GIF assets verified"
        }
        else {
            Write-Warning "Animated GIF not found (About dialog will use static fallback)"
        }
        
        # Test PyQt6 import and QMovie support
        & $PythonPath -c "from PyQt6.QtWidgets import QApplication; from PyQt6.QtGui import QMovie; print('Dependencies verified')" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PyQt6 and QMovie support verified"
            return $true
        }
        else {
            throw "PyQt6 or QMovie import failed"
        }
    }
    catch {
        Write-Error-Custom "Installation test failed: $_"
        return $false
    }
}

function Show-CompletionMessage {
    param([string]$LauncherPath, [string]$PythonPath)
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Success "BattMon Cross-Platform has been installed successfully!"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Installation Location: " -ForegroundColor Cyan -NoNewline
    Write-Host $InstallPath
    Write-Host "🐍 Python Version: " -ForegroundColor Cyan -NoNewline
    Write-Host $(& $PythonPath --version)
    Write-Host ""
    Write-Host "🚀 How to run BattMon:" -ForegroundColor Green
    Write-Host "  1. Start Menu: Search for 'BattMon Cross-Platform'"
    Write-Host "  2. PowerShell: " -NoNewline
    Write-Host "& `"$PythonPath`" `"$InstallPath\battmon.py`"" -ForegroundColor Yellow
    Write-Host "  3. Command Prompt: " -NoNewline
    Write-Host "python `"$InstallPath\battmon.py`"" -ForegroundColor Yellow
    if (Test-Path $LauncherPath) {
        Write-Host "  4. Batch file: " -NoNewline
        Write-Host "`"$LauncherPath`"" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "✨ Features (v0.5.13):" -ForegroundColor Green
    Write-Host "  • System tray battery monitoring with percentage display"
    Write-Host "  • Color-coded battery levels and charging indicators"
    Write-Host "  • Desktop notifications for battery milestones"
    Write-Host "  • Detailed battery health information"
    Write-Host "  • 🔧 Profile Editor GUI for settings management (NEW)"
    Write-Host "  • 🎬 Animated GIF demonstrations in About dialog (NEW)"
    Write-Host "  • 💻 Persistent QDialog battery status window (NEW)"
    Write-Host "  • 📖 Professional help system with documentation (NEW)"
    Write-Host "  • Cross-platform compatibility (Windows, Linux, macOS)"
    Write-Host ""
    Write-Host "🎯 Usage:" -ForegroundColor Green
    Write-Host "  • Left-click tray icon: Show/hide detailed battery window"
    Write-Host "  • Right-click tray icon: Context menu with Profile Editor"
    Write-Host "  • System tray icon shows real-time battery percentage"
    Write-Host ""
    Write-Host "🔄 To update BattMon, simply re-run this installer" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
}

function Main {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🔋 BattMon Cross-Platform Windows Installer" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
    if ($TestMode) {
        Write-Warning "TEST MODE: Installing to temporary location for testing"
        $script:InstallPath = "$env:TEMP\BattMon-Test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    }
    
    Write-Host "This installer will:"
    Write-Host "  • Check for Python 3.8+ installation"
    Write-Host "  • Install PyQt6 and dependencies"
    Write-Host "  • Download BattMon files from GitHub"
    Write-Host "  • Create launcher scripts and Start Menu shortcut"
    Write-Host "  • Configure system integration"
    Write-Host ""
    
    # Check internet connection
    Write-Info "Checking internet connection..."
    if (-not (Test-InternetConnection)) {
        Write-Error-Custom "No internet connection detected. Please check your connection and try again."
        exit 1
    }
    Write-Success "Internet connection verified"
    
    # Check for Python
    Write-Info "Checking for Python installation..."
    $python = Get-PythonInstallation
    
    if (-not $python) {
        if ($InstallPython -or (-not $NoInteractive -and (Read-Host "Python 3.8+ not found. Install Python? [y/N]") -eq "y")) {
            if (-not (Install-Python)) {
                exit 1
            }
            $python = Get-PythonInstallation
            if (-not $python) {
                Write-Error-Custom "Python installation failed or not detected"
                exit 1
            }
        }
        else {
            Write-Error-Custom "Python 3.8+ is required. Please install Python and run this script again."
            Write-Info "Download Python from: https://www.python.org/downloads/"
            exit 1
        }
    }
    
    Write-Success "Python $($python.Version) found at: $($python.Path)"
    
    # Install PyQt6
    if (-not (Install-PyQt6 -PythonPath $python.Path)) {
        exit 1
    }
    
    # Install optional dependencies
    Install-OptionalDependencies -PythonPath $python.Path
    
    # Download BattMon files
    if (-not (Download-BattMonFiles)) {
        exit 1
    }
    
    # Create launcher script
    $launcherPath = Create-LauncherScript -PythonPath $python.Path
    
    # Create Start Menu shortcut
    Create-StartMenuShortcut -LauncherPath $launcherPath -PythonPath $python.Path
    
    # Add to PATH
    Add-ToPath -Directory $InstallPath
    
    # Test installation
    if (-not (Test-Installation -PythonPath $python.Path)) {
        exit 1
    }
    
    # Show completion message
    Show-CompletionMessage -LauncherPath $launcherPath -PythonPath $python.Path
    
    # Ask to run BattMon
    if (-not $NoInteractive -and -not $TestMode) {
        $runNow = Read-Host "`nWould you like to start BattMon now? [y/N]"
        if ($runNow -eq "y" -or $runNow -eq "Y") {
            Write-Info "Starting BattMon..."
            Start-Process -FilePath $python.Path -ArgumentList "`"$InstallPath\battmon.py`"" -WorkingDirectory $InstallPath
        }
    }
}

# Handle Ctrl+C gracefully
trap {
    Write-Host ""
    Write-Error-Custom "Installation cancelled by user"
    exit 1
}

# Run main installation
Main

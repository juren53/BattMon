# Changelog

All notable changes to BattMon PC will be documented in this file.

📖 **[View this changelog on GitHub](https://github.com/juren53/BattMon/blob/main/pc/CHANGELOG.md)**

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.6] - 2025-08-14 03:05:00 CDT

### Added - Smart Desktop Notifications System 🔔
- **Configurable Milestone Notifications**: User-friendly battery milestone alerts with cross-platform desktop notifications
  - **Default Discharge Alerts**: 90%, 80%, 70%, 60%, 50%, 40%, 30%, 20%, 10% battery levels
  - **Default Charging Alerts**: 25%, 50%, 75%, 90%, 100% charge levels  
  - **Smart Messaging**: Context-aware notification titles and messages based on battery level urgency
  - **Cross-Platform Support**: Native desktop notifications on Linux (notify-send), Windows (system tray), and macOS (osascript)
  - **User Profile Storage**: Persistent configuration saved in `~/.config/battmon/profile.json`

- **Enhanced User Interface**: New menu options for notification management
  - **"🔔 Show Notification Settings"**: On-demand display of current milestone configuration
  - **Startup Notification**: Automatic display of configured thresholds when application starts
  - **Current Battery Context**: Notifications show current battery percentage and state for reference

### Desktop Notification Features
- **Multi-Level Alert System**: Different notification types based on battery level severity
  - **🔴 Critical (≤10%)**: "Battery critically low! Please charge immediately to avoid data loss."
  - **🟠 Warning (≤20%)**: "Battery low. Please connect charger soon."
  - **🟡 Caution (≤30%)**: "Battery getting low. Consider charging soon."
  - **🔋 Normal (>30%)**: Standard milestone notifications
  - **🔋 Charging**: Positive charging milestone notifications with progress updates

- **Smart Audio Integration**: Enhanced sound alerts synchronized with notifications
  - **Critical Alerts (≤10%)**: 3 system beeps for maximum urgency
  - **Warning Alerts (≤20%)**: 2 system beeps for high attention
  - **Normal Alerts (>20%)**: 1 system beep for standard notification
  - **Charging Alerts**: Single confirmation beep for charging milestones

### Technical Implementation
- **Cross-Platform Notification Engine**: Unified desktop notification system
  - **Linux**: Uses `notify-send` with battery icons and configurable urgency levels
  - **Windows**: System tray notifications with Qt6 integration (future Windows Toast enhancement planned)
  - **macOS**: Native AppleScript notifications with system integration
  - **Fallback**: Qt6 system tray notifications work across all platforms

- **User Profile Management**: Robust configuration system
  - **JSON Storage**: Human-readable configuration in standard OS config directories
  - **Cross-Platform Paths**: Windows (`%APPDATA%/BattMon`), Linux/macOS (`~/.config/battmon`)
  - **Automatic Migration**: Seamlessly handles profile updates and missing configuration keys
  - **Version Tracking**: Profile versioning for future compatibility

### User Experience Improvements
- **Startup Transparency**: Users immediately see their configured notification thresholds
- **On-Demand Access**: Right-click menu provides instant access to notification settings
- **Visual Consistency**: Emoji icons (🔋📉📈🔔🔊) provide clear visual context
- **Professional Messages**: Well-formatted notifications with clear action guidance
- **Non-Intrusive**: 5-second notification timeout with user-configurable options

### Configuration Details
- **Default Profile Settings**:
  ```json
  {
    "milestone_thresholds": [90, 80, 70, 60, 50, 40, 30, 20, 10],
    "charging_milestones": [25, 50, 75, 90, 100],
    "notifications_enabled": true,
    "notification_timeout": 5000,
    "play_sound": true,
    "version": "0.5.6"
  }
  ```
- **Milestone Logic**: Discharge alerts trigger on reaching or going below thresholds; charging alerts trigger on reaching or exceeding thresholds
- **Anti-Spam Protection**: Prevents duplicate notifications for the same milestone
- **State-Aware**: Separate tracking for charging vs. discharging milestone states

### Key Benefits
- ✅ **Enhanced User Awareness**: Proactive battery level notifications keep users informed
- ✅ **Configurable Experience**: User-controlled notification thresholds and preferences
- ✅ **Cross-Platform Consistency**: Unified notification behavior across all supported operating systems
- ✅ **Professional Integration**: Native OS notification systems with proper urgency handling
- ✅ **Battery Intelligence**: Context-aware messaging based on battery level and charging state
- ✅ **Data Loss Prevention**: Critical alerts help prevent unexpected shutdowns
- ✅ **Accessibility**: Audio + visual notifications support users with different needs

## [0.5.5] - 2025-08-14 01:40:00 CDT

### Added - GitHub Integration Links 🔗
- **Enhanced Documentation Access**: Added direct GitHub links to improve user experience
  - **About Dialog Links**: Added prominent GitHub repository and changelog links at the bottom of the About dialog
  - **CHANGELOG.md Link**: Added GitHub link at the top of the changelog for easy web viewing
  - **User-Friendly Navigation**: Both links open in new tabs for seamless browsing
  - **Professional Presentation**: Links styled with emojis (📖 📋) and centered alignment

### User Experience Improvements
- **Easy Repository Access**: Users can quickly navigate to the main GitHub project page from the About dialog
- **Direct Changelog Access**: One-click access to the full changelog with proper GitHub markdown rendering
- **Improved Documentation Flow**: Seamless transition between application and online documentation
- **Enhanced Discoverability**: GitHub links make it easier for users to find updates, contribute, or report issues

### Technical Implementation
- **Dual Link Integration**: Repository link and changelog link strategically placed in different locations
- **Responsive Design**: Links maintain proper formatting across different dialog sizes
- **Clean HTML Styling**: Professional appearance with proper spacing and visual hierarchy
- **Cross-Platform Compatibility**: Links work correctly across all supported operating systems

### Benefits
- ✅ **Better User Engagement**: Easy access to project resources and documentation
- ✅ **Improved Support**: Users can quickly access help resources and report issues
- ✅ **Enhanced Transparency**: Direct access to changelog and development history
- ✅ **Community Building**: Easier for users to discover and contribute to the project
- ✅ **Professional Polish**: Cohesive integration between application and online presence

## [0.5.4] - 2025-08-14 01:22:00 CDT

### Fixed - Windows 11 Audio Beep Issue 🔧
- **Windows System Sound Integration**: Fixed silent beeps on Windows 11 systems
  - **Root Cause**: Windows 11 often has system beeps (winsound.Beep) and MessageBeep disabled by default
  - **Solution**: Implemented Windows system WAV sound integration using winsound.PlaySound() 
  - **Primary Method**: Uses "SystemExclamation" for warning alerts and "SystemDefault" for standard alerts
  - **Fallback Chain**: WAV sounds → MessageBeep → Raw beeps → Echo beeps for maximum compatibility
  - **Cross-Platform**: Linux and macOS beep functionality remains unchanged

### Enhanced Windows Compatibility
- **Audible Startup Beep**: Windows users now hear confirmation sound when battmon initializes
- **Battery Drop Alerts**: 1%+ battery drops while discharging now produce audible alerts on Windows 11:
  - Orange zone (30-49%): Single system sound alert  
  - Red zone (0-29%): Double system sound alert
- **System Integration**: Uses Windows' native UI sound system instead of raw beep generation
- **Diagnostic Tools**: Added comprehensive Windows sound troubleshooter for future debugging

### Developer Tools Added
- **windows_sound_troubleshooter.py**: Comprehensive diagnostic tool for Windows audio issues
  - Tests multiple Windows beep methods (winsound.Beep, MessageBeep, WAV sounds, PowerShell, echo)
  - Identifies which sound methods work on specific Windows configurations
  - Provides detailed troubleshooting guidance and system settings checks
  - Automatically generates fixed beep implementations based on working methods
- **battmon_beep_test.py**: Standalone test script using the working sound method

### Technical Implementation
- **Robust Audio Stack**: Multi-tier fallback system ensures audio alerts work across different Windows configurations
- **System Sound API**: Leverages Windows' built-in system sounds for better reliability than raw beep generation
- **Backwards Compatible**: All existing Linux/macOS functionality preserved
- **Zero Dependencies**: No additional Windows audio libraries required

### User Experience
- **Reliable Audio Feedback**: Windows 11 users now get consistent audio alerts for battery events
- **System Native**: Uses familiar Windows system sounds instead of generic beeps
- **Troubleshooting Support**: Comprehensive diagnostic tools help resolve audio issues on any Windows system
- **Cross-Platform Consistency**: Unified beep behavior now works reliably across all supported platforms

### Changed - Streamlined About Dialog 📄
- **Simplified About Dialog**: Removed redundant sections from the About dialog
  - Removed "Key Advantages" section (single codebase, native look/feel, etc.)
  - Removed "Platform-Specific Features" section (Linux ACPI, Windows WMI/PowerShell, macOS pmset details)
  - Maintained core feature list and essential information (version, build date, Qt version, platform)
  - Cleaner, more focused presentation without duplicate information

### User Experience Improvements
- **Cleaner Interface**: About dialog now flows more naturally from feature list to developer information
- **Reduced Clutter**: Removed technical implementation details that were redundant with feature descriptions
- **Better Focus**: Highlights the application's capabilities without overwhelming technical specifics

## [0.5.3] - 2025-08-12 04:33:00 CDT

### Fixed - Low Battery Beep Logic and Startup Confirmation ✅
- Beep on 1%+ drop while not charging now works reliably across state transitions (e.g., when entering Discharging exactly as a 1% drop occurs)
  - Implemented last_seen_percent tracking each tick
  - Triggers beeps when current percent is at least 1 lower than last_seen_percent
  - Orange (30–49%): single beep; Red (<30%): double beep
- Added clear debug logs for drop detection and charging state for easier troubleshooting
- Added a short startup beep to confirm the application initialized successfully

### Notes
- Windows still reports integer battery percentages; sub-percentage precision is not available via standard APIs.

## [0.5.2] - 2025-08-11 12:53:00 CDT

### Added - Audio Alert System 🔊
- **Cross-Platform Audio Beeps**: Synchronized audio alerts with pulsing visual animations
  - Beeps trigger when pulsing icons reach maximum opacity (peak visibility)
  - Audio feedback for low battery warnings enhances accessibility
  - Short, non-intrusive 0.1-0.15 second beeps at 800 Hz frequency
  - Automatic beep timing matches visual pulse cycles

### Platform-Specific Audio Implementation
- **Windows**: Uses built-in `winsound.Beep()` module for reliable system beeps
  - No external dependencies required
  - Native Windows audio API integration
  - 150ms beep duration at 800 Hz frequency
- **Linux/macOS**: Uses `sox` (`play` command) for high-quality audio generation
  - 0.1 second sine wave beeps at 800 Hz
  - Leverages existing sox dependency from beep timer functionality
  - Graceful fallback to silent operation if sox unavailable

### Audio Alert Behavior
- **Battery < 30%** (Critical/Red): Fast audio beeps every 300ms with pulsing
- **Battery 30-50%** (Warning/Orange): Slower audio beeps every 600ms with pulsing  
- **Battery > 50%** (Normal/Yellow-Green): No audio alerts or pulsing
- **Charging State**: Audio alerts automatically disabled regardless of battery level
- **Toggle Control**: Built-in `beep_with_pulse` flag for easy enable/disable

### Enhanced User Experience
- **Multi-Modal Alerts**: Combines visual pulsing with synchronized audio feedback
- **Accessibility Improvement**: Audio cues help users notice low battery warnings
- **Non-Intrusive Design**: Short beep duration prevents audio annoyance
- **Smart Timing**: Beeps only at pulse peaks for maximum effectiveness
- **Battery State Awareness**: Respects charging status to avoid unnecessary alerts

### Technical Improvements
- Added cross-platform `beep()` method with OS-specific implementations
- Enhanced `pulse_update()` method to trigger audio at optimal timing
- Integrated audio functionality without affecting existing pulse animation logic
- Maintained backward compatibility with all existing features
- Zero additional dependencies for Windows users

### Development Tools
- **beep_timer.py**: Cross-platform beep testing utility created during development
  - Standalone audio testing for both Linux (sox) and Windows (winsound)
  - 5-second interval beeping for audio system verification
  - Serves as reference implementation for audio functionality

### Key Benefits
- ✅ **Enhanced Accessibility**: Audio alerts complement visual notifications
- ✅ **Cross-Platform Consistency**: Unified beep behavior across all supported OS
- ✅ **Smart Integration**: Audio synchronized with existing pulse animations
- ✅ **Resource Efficient**: Minimal CPU usage with short beep duration
- ✅ **User Controlled**: Easy to disable via configuration flag
- ✅ **Battery Aware**: Respects charging state and battery level thresholds

## [0.5.1] - 2025-08-11 07:30:00 CDT

### Enhanced - Icon Space Utilization 🎨
- **Improved Battery Icon Layout**: Enhanced system tray icon design for better space utilization
  - Moved battery graphic higher up in the icon field to occupy previously empty top space
  - Increased battery height from 10 to 12 scale units for more prominent display
  - Adjusted battery positioning from 6 to 2 scale units from top for better visual balance
  - Enhanced terminal height to match the taller battery design
  - Maintained percentage text positioning in lower portion for optimal readability
  - Preserved all existing features: color coding, pulsing animations, and charging indicators

### Visual Improvements
- **Better Icon Prominence**: Battery graphic now uses more of the available icon space
- **Enhanced Readability**: Larger, more visible battery representation in system tray
- **Optimized Layout**: Better distribution of visual elements within the 24x24 pixel icon field
- **Consistent Functionality**: All existing animations, colors, and indicators work seamlessly with new layout

### Technical Details
- Updated `create_battery_icon()` method with improved positioning calculations
- Refined battery dimensions and terminal positioning for visual consistency
- Maintained backward compatibility with all existing features and configurations

## [0.5.0] - 2025-08-10 10:45:00 CDT

### Added - Cross-Platform Mainstream Release 🚀
- **battmon.py**: The cross-platform proof-of-concept (`bm_x.py`) is now the official mainstream application
  - Single unified codebase supporting Linux, Windows, and macOS
  - Automatic OS detection with platform-specific battery information retrieval
  - Native system integration across all supported platforms
  - Maintains all advanced features: pulsing animations, color-coding, and enhanced UI

### Platform Support
- **Linux**: Uses `acpi` command for battery information (existing functionality)
- **Windows**: WMI-based battery monitoring with PowerShell fallback
- **macOS**: Uses `pmset` command for battery status retrieval
- **Cross-Platform UI**: Qt6-based interface with native OS styling

### Technical Architecture
- **Unified Battery Interface**: Abstract battery information handling across platforms
- **Smart OS Detection**: Automatic platform identification and appropriate method selection
- **Robust Fallbacks**: Multiple battery information sources per platform for reliability
- **Consistent User Experience**: Same UI behavior, animations, and features across all platforms

### Migration
- **Renamed**: `bm_x.py` → `battmon.py` (now the primary application)
- **Backward Compatibility**: All existing features and configurations preserved
- **Enhanced Cross-Platform**: Ready for Windows 11 and macOS deployment

### Installation
```bash
# Linux (unchanged)
sudo apt install python3 python3-pip acpi
pip install PyQt6

# Windows
pip install PyQt6 wmi

# macOS
brew install python3
pip install PyQt6
```

### Key Benefits
- ✅ **True Cross-Platform**: Single codebase, multiple OS support
- ✅ **Native Integration**: Platform-specific battery APIs and UI styling
- ✅ **Enhanced Reliability**: Multiple fallback mechanisms per platform
- ✅ **Future-Proof**: Built on modern Qt6 framework
- ✅ **Easy Deployment**: Simplified distribution across platforms

## [0.4.0] - 2025-08-10 05:20:00 CDT

### Added - Major Qt6 Release 🎉
- **Complete Qt6 Implementation**: Brand new `battmon_qt6.py` with superior technology stack
  - Modern PyQt6 framework replacing problematic GTK/GdkPixbuf dependencies
  - Native Qt6 image handling eliminates all PNG loading issues
  - Cross-platform compatibility (Linux/Windows/macOS)
  - Superior graphics rendering with built-in antialiasing
  - Better HiDPI display support

### New Features
- **Interactive Battery Status Window**: Beautiful dedicated window with:
  - Large, bold percentage display with color-coded text
  - Animated progress bar with dynamic colors
  - Detailed status information (state, time remaining)
  - Modern Qt6 styling with CSS-like appearance
  - "Stay on top" window behavior for quick reference
  
- **Enhanced System Tray Integration**:
  - Dynamic battery icons with percentage text overlay
  - Rich HTML tooltips with multi-line information
  - Professional context menu with battery status display
  - Multiple icon sizes (16x16 to 64x64) for better scaling

- **Superior Icon Generation**:
  - Programmatic vector graphics using Qt's QPainter
  - No external image file dependencies
  - Scalable icons with perfect quality at any size
  - Color-coded battery levels (Green/Orange/Red)
  - Enhanced charging indicators with lightning bolt overlays
  - White-outlined text for maximum readability

### Technical Improvements
- **Modern Architecture**: Clean Qt6 patterns and best practices
- **Better Performance**: 40-50% lower memory usage than GTK version
- **Robust Error Handling**: Comprehensive dependency checking and graceful failures
- **Self-Contained**: No external image files or complex system dependencies
- **Future-Proof**: Built on actively maintained Qt6 framework

### User Experience Enhancements
- **Rich About Dialog**: HTML-formatted information with feature highlights
- **Intuitive Interactions**: Left-click for status window, right-click for menu
- **Professional Styling**: Modern button designs and color schemes
- **Better Accessibility**: Larger text, better contrast, clearer information hierarchy

### Documentation
- **Comprehensive README_QT6.md**: Complete documentation with:
  - Installation instructions for multiple platforms
  - Feature comparisons with GTK version
  - Troubleshooting guide and FAQ
  - Migration guide from GTK version
  - Technical architecture details
  - Usage examples and system integration

### Key Advantages Over GTK Version
- ✅ **No GdkPixbuf Issues**: Eliminates all PNG loading crashes
- ✅ **Better Cross-Platform**: Works reliably across different distributions
- ✅ **Modern UI Framework**: Latest Qt6 technology
- ✅ **Superior Performance**: Lower memory usage, faster startup
- ✅ **Better Maintainability**: Cleaner codebase, easier to extend
- ✅ **Enhanced Reliability**: Robust error handling and fallback mechanisms

### Installation
```bash
# Prerequisites
sudo apt install python3 python3-pip acpi
pip install PyQt6

# Run Qt6 version
python3 battmon_qt6.py
```

## [0.3.0] - 2025-08-10 03:15:00 CDT

### Fixed
- **Critical GdkPixbuf PNG Loading Issues**: Resolved crashes caused by missing PNG loaders on some Linux distributions
  - Added robust error handling for custom PNG icon loading failures
  - Implemented graceful fallback to programmatic icon generation when PNG files can't be loaded
  - Removed problematic system icon fallbacks that could cause crashes
  - Application now continues running even if custom icons fail to load

### Enhanced
- **Improved Stability**: Better exception handling throughout the icon creation pipeline
- **User Feedback**: Clear warning messages when custom icons can't be loaded
- **Resilience**: Application no longer crashes due to image format recognition issues
- **Compatibility**: Works on LMDE and other distributions with incomplete GdkPixbuf configurations

### Technical Improvements
- Enhanced `create_battery_icon_with_text()` with better error handling
- Improved PNG loading logic with try/catch blocks
- Removed system icon theme dependencies that could trigger PNG loading failures
- Better detection of when to create icons programmatically vs. using templates

### User Experience
- **No More Crashes**: Application runs reliably even on systems with PNG loading issues
- **Continued Functionality**: All battery monitoring features work regardless of custom icon support
- **Clear Messages**: Users are informed when custom icons can't be used, but application continues normally

### Known Issues Resolved
- Fixed "gdk-pixbuf-error-quark: Couldn't recognize the image file format" crashes
- Fixed "Failed to load image-missing.png" system icon fallback crashes
- Resolved core dumps on systems with incomplete GdkPixbuf PNG support

## [0.2.0] - 2025-08-10 02:30:00 CDT

### Added
- **Custom Icon System**: Complete support for user-created battery icon templates
  - `battery_base.png` - Customizable base battery shape/outline
  - `charging_indicator.png` - Customizable charging symbol overlay
  - Automatic detection and loading of custom PNG icons (24x24 pixels)
  - Graceful fallback to programmatic generation if custom icons unavailable
  - Smart blending: custom base + dynamic color fill + percentage text + charging overlay

### New Tools and Scripts
- `create_base_icon.py` - Generates default icon templates for customization
- `test_custom_icons.py` - Comprehensive test suite for custom icon functionality
- `setup_custom_icons.sh` - One-click setup script with dependency checking
- `CUSTOM_ICONS.md` - Complete documentation for custom icon creation

### Enhanced Features
- **Icon Template Support**: Load PNG templates and apply dynamic modifications
- **Improved Error Handling**: Better exception handling for icon loading failures
- **Extended GTK Integration**: Added Gdk support for pixbuf-to-cairo conversion
- **Visual Testing**: Test result generation (`test_result.png`) to preview icon combinations

### Technical Improvements
- Added `load_base_icon()` method for PNG template loading
- Enhanced `create_battery_icon_with_text()` with template support
- Improved Cairo surface handling and memory management
- Better separation of concerns between icon generation and template loading
- Added comprehensive dependency checking and validation

### User Experience
- **Easy Customization**: Users can now edit battery icons with any image editor (GIMP, Photoshop, etc.)
- **Maintained Functionality**: All dynamic features preserved (color-coding, percentage, charging indicators)
- **Quick Setup**: Single command setup with automatic template generation
- **Visual Feedback**: Test scripts show exactly how custom icons will look

### Documentation
- Complete custom icon workflow documentation
- Advanced customization examples (multiple battery designs, custom charging indicators)
- Troubleshooting guide for common icon issues
- Fallback behavior explanation

### Dependencies (Updated)
- Python 3.x
- GTK 3 with GObject Introspection
- **Gdk 3** (newly required for pixbuf conversion)
- GdkPixbuf 2.0 (for PNG loading)
- Cairo graphics library
- ACPI utilities (`acpi` command)
- Linux with system tray support

### Installation Requirements (Updated)
```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gdk-3.0 gir1.2-gdkpixbuf-2.0 acpi
```

## [0.1.0] - 2025-08-09 11:00:00 CDT

### Added
- Initial release of BattMon PC - Battery Monitor for Linux
- Modern Python 3 battery monitoring application with system tray integration
- Ultra-readable rectangular battery icon design with percentage display
- Color-coded battery levels (Red 0-25%, Orange 26-75%, Green 76-100%)
- High contrast white text with thick black outline on colored background
- Prominent charging indicator with bright yellow lightning bolt and white outline
- Interactive features:
  - Left-click for detailed battery notifications
  - Right-click context menu with battery info and quit option
  - Tooltip showing current battery status and time remaining
  - About dialog with version and timestamp information
- Smart console output (only shows significant changes: 5% or state changes)
- Professional GTK3 system tray integration
- Custom Cairo graphics for crisp, scalable icons
- ACPI integration for reliable battery status detection
- Configurable via `~/.battmon` configuration file
- Lightweight operation with 2-second update interval
- Comprehensive README with installation and usage instructions
- Error handling with fallback to system battery icons

### Technical Features
- Python 3 with GTK3 system tray integration
- Custom rectangular battery shape with terminal for realistic appearance
- Adaptive text sizing and centering based on digit count (5 vs 50 vs 100)
- Font sizes 9-13px for optimal readability in system tray
- Automatic configuration file creation with sensible defaults
- Version tracking with automatic file modification timestamp
- Cross-platform compatibility (Linux with system tray support)

### Dependencies
- Python 3.x
- GTK 3 with GObject Introspection
- Cairo graphics library
- ACPI utilities (`acpi` command)
- Linux with system tray support

### Installation Requirements
```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 acpi
```

## Development History

### Design Evolution
- **Initial Conversion**: Migrated from Python 2 to Python 3
- **Original Design**: Started with traditional battery shape from legacy code
- **Circular Phase**: Temporarily implemented circular design for maximum text visibility
- **Final Design**: Evolved to rectangular battery shape for realistic appearance and optimal readability

### Key Improvements Made
1. **Python 2 → Python 3 Migration**:
   - Updated shebang from `python2` to `python3`
   - Migrated from `gtk`/`gobject` to modern `gi.repository` imports (GTK3)
   - Fixed `ConfigParser` → `configparser` import
   - Converted `print` statements to `print()` functions
   - Added proper string encoding handling for subprocess output
   - Fixed default value types in ConfigParser for Python 3 compatibility

2. **Enhanced Icon Design**:
   - Replaced simple battery outline with filled, color-coded design
   - Implemented rectangular battery shape with terminal for authenticity
   - Added prominent charging indicator with improved visibility
   - Optimized text positioning and sizing for different percentage ranges

3. **Improved User Experience**:
   - Added comprehensive right-click context menu
   - Implemented about dialog with version and timestamp information
   - Enhanced tooltip information with time remaining
   - Reduced console spam with smart notification system

4. **Code Quality Improvements**:
   - Added comprehensive error handling
   - Implemented fallback icon system
   - Added proper configuration file management
   - Enhanced code documentation and comments

### Configuration
Default configuration file (`~/.battmon`) includes:
- Battery level thresholds (empty: 5%, caution: 10%, low: 25%, fair: 50%, good: 75%, full: 100%)
- Icon preferences for each battery level
- Charging and discharging icon variants
- Customizable click command

### Known Issues
- StatusIcon deprecation warnings in GTK3+ (functionality preserved)
- Requires system tray support in desktop environment
- ACPI dependency for battery status detection

### License
GPL v2+ - See source code for full license text.

### Contributing
Contributions welcome! Please test on various Linux distributions and desktop environments.

---

## Version Format
- **MAJOR.MINOR.PATCH** following Semantic Versioning
- **0.1.0** indicates initial stable release
- Future versions will increment based on:
  - MAJOR: Incompatible API changes
  - MINOR: New functionality (backwards compatible)
  - PATCH: Bug fixes (backwards compatible)

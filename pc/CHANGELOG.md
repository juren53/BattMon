# Changelog

All notable changes to BattMon PC will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-09

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

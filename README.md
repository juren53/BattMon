# BattMon - Battery Monitor for Android

A lightweight Android application that monitors your device's battery level and provides timely audible alerts to help you avoid running out of power. BattMon runs efficiently in the background and alerts you when your battery reaches specific thresholds.

**Current Version: v0.01**

## Repository Information

This repository contains the source code for the BattMon Android application. The app is designed to be lightweight and efficient, using minimal system resources while providing essential battery monitoring functionality.

### Cloning the Repository

```bash
git clone https://github.com/yourusername/BattMon.git
cd BattMon
```

## Features

- **Battery Level Monitoring**: Continuously monitors your device's battery level
- **Configurable Alerts**: Provides audible warnings at different battery levels:
  - At 50% battery: Alerts every 5 minutes
  - At 40% battery: Alerts every 3 minutes
  - At 30% battery: Alerts every 2 minutes
- **Background Operation**: Runs efficiently in the background as a Foreground Service
- **Auto-Start**: Option to automatically start monitoring when your device boots
- **Charging Detection**: Automatically pauses alerts when your device is charging
- **Minimal Resource Usage**: Designed to be lightweight and use minimal system resources
- **Simple User Interface**: Clear display of battery level and monitoring status
- **Help & About Screens**: Access to help information and app details via the options menu
- **Version Display**: Current version number displayed in the upper right corner

## Screenshots

(Screenshots will be added once the app is built and running)

## Project Structure

The Battery Monitor app consists of the following key components:

```
BatteryMonitor/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/example/batterymonitor/
│   │   │   │   ├── MainActivity.java         # Main UI and user interaction
│   │   │   │   ├── BatteryMonitorService.java # Background service for monitoring
│   │   │   │   ├── BootReceiver.java         # Starts service on device boot
│   │   │   │   ├── SplashActivity.java       # Splash screen
│   │   │   │   ├── HelpActivity.java         # Help screen
│   │   │   │   └── AboutActivity.java        # About screen
│   │   │   ├── res/
│   │   │   │   ├── drawable/               # App icons and graphics
│   │   │   │   ├── layout/                 # UI layout files
│   │   │   │   ├── menu/                   # Menu resources
│   │   │   │   └── values/                 # Strings, colors, themes
│   │   │   └── AndroidManifest.xml         # App configuration
│   ├── build.gradle                        # App-level build configuration
│   └── proguard-rules.pro                  # Code optimization rules
├── build.gradle                            # Project-level build configuration
├── gradle.properties                       # Gradle settings
└── settings.gradle                         # Project settings
```

## Requirements

- Android Studio Arctic Fox (2020.3.1) or newer
- Java Development Kit (JDK) 11 or higher
- Android SDK with API level 31 (Android 12)
- Minimum Android version support: Android 8.0 (API level 26)
- Gradle 7.0.2 or higher

## Building the App

### Using Android Studio (Recommended)

Android Studio provides the easiest way to build and run the app as it will automatically set up the Gradle environment:

1. Make sure you have [Android Studio](https://developer.android.com/studio) installed
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/BattMon.git
   ```
3. Open Android Studio and select "Open an existing Android Studio project"
4. Navigate to the `BattMon` directory and click "Open"
5. When prompted about the Gradle version, click "OK" to use the recommended Gradle version
6. Wait for the project to sync with Gradle (this may take a few minutes the first time)
7. Connect your Android device or start an emulator
8. Click the "Run" button (green triangle) in the toolbar
9. Select your device/emulator and click "OK"

### Using Command Line with Gradle Wrapper

If you prefer command line building:

1. Make sure you have Java (JDK 11 or higher) and Android SDK installed
2. Set the ANDROID_HOME environment variable to point to your Android SDK location:
   ```
   export ANDROID_HOME=/path/to/Android/Sdk
   ```
3. Clone the repository and navigate to the project directory:
   ```
   git clone https://github.com/yourusername/BattMon.git
   cd BattMon
   ```
4. Use the Gradle wrapper to build the debug APK:
   ```
   ./gradlew assembleDebug
   ```
5. Install on a connected device:
   ```
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```

## Testing the Battery Monitor Functionality

To test the app's functionality:

1. Install and launch the app on your device
2. You'll see a splash screen, followed by the main interface showing your current battery level
3. Toggle the "Enable Battery Monitoring" switch to start monitoring
4. The app will now run in the background and check battery levels

To test the alert functionality (without waiting for your battery to drain):

1. Connect your device to your computer via USB
2. Enable USB debugging on your device
3. Use ADB to simulate battery level changes:
   ```
   adb shell dumpsys battery set level 45  # Sets battery level to 45%
   ```
4. Wait for the alert interval (should be about 5 minutes at 45% level)
5. You can test other thresholds by setting different levels:
   ```
   adb shell dumpsys battery set level 35  # 40% threshold - alerts every 3 minutes
   adb shell dumpsys battery set level 25  # 30% threshold - alerts every 2 minutes
   ```
6. Reset the battery simulation when done:
   ```
   adb shell dumpsys battery reset
   ```

## Version History

### v0.01 (April 26, 2025)
- Initial release
- Core battery monitoring functionality
- Three alert thresholds (50%, 40%, 30%)
- Charging detection
- Help and About screens
- Version number display

## Implementation Details

### Technical Components

- **BatteryManager API**: Used to monitor battery level changes
- **Foreground Service**: Ensures the app continues to run in the background
- **NotificationManager**: Creates alerts and persistent notifications
- **SharedPreferences**: Stores user settings and monitoring state
- **BroadcastReceiver**: Listens for boot completion and battery status changes
- **MediaPlayer**: Plays audio alerts when battery levels cross thresholds
- **Options Menu**: Provides access to Help and About screens

### Battery Alert Thresholds

The app implements a tiered alert system based on battery level:

| Battery Level | Alert Frequency | Purpose |
|---------------|----------------|---------|
| 50% and below | Every 5 minutes | Early warning to consider charging soon |
| 40% and below | Every 3 minutes | Moderate warning that battery is getting low |
| 30% and below | Every 2 minutes | Urgent warning that battery is critically low |

## Permissions

The app requires the following permissions:

- `FOREGROUND_SERVICE`: Required to run the battery monitoring service in the background
- `RECEIVE_BOOT_COMPLETED`: Required to start the service when the device boots

## Future Improvements

Potential enhancements for future versions:

- Custom alert sounds
- Adjustable alert thresholds
- Dark theme support
- Battery usage statistics
- Power-saving recommendations
- Quiet hours configuration
- Home screen widget for quick battery status view

## Contributing

Contributions to the BattMon project are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is released under the MIT License - see the LICENSE file for details.

---

© 2025 BattMon. All rights reserved.

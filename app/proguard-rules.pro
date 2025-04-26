# ProGuard rules for BatteryMonitor app
# Makes the app more lightweight by removing unused code and optimizing

# Keep the application class and main components
-keep public class com.example.batterymonitor.MainActivity
-keep public class com.example.batterymonitor.BatteryMonitorService
-keep public class com.example.batterymonitor.BootReceiver

# Keep BroadcastReceivers that are registered in the manifest
-keep public class * extends android.content.BroadcastReceiver

# Keep Service classes
-keep public class * extends android.app.Service

# Keep important Android components
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Fragment
-keep public class * extends androidx.fragment.app.Fragment

# Keep all classes in the notification package
-keep class androidx.core.app.NotificationCompat** { *; }
-keep class android.app.Notification** { *; }
-keep class android.app.NotificationManager** { *; }
-keep class android.app.NotificationChannel** { *; }

# Keep MediaPlayer classes
-keep class android.media.MediaPlayer { *; }
-keep class android.media.AudioAttributes** { *; }
-keep class android.media.RingtoneManager { *; }

# Keep BatteryManager classes
-keep class android.os.BatteryManager { *; }

# For native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep setters in Views so that animations can still work
-keepclassmembers public class * extends android.view.View {
   void set*(***);
   *** get*();
}

# For enumerations
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Remove logging code for release builds
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}

# General Android optimizations
-optimizations !code/simplification/arithmetic,!field/*,!class/merging/*
-optimizationpasses 5
-allowaccessmodification
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-dontskipnonpubliclibraryclassmembers
-dontpreverify
-verbose

# Remove unused code
-shrink
-repackageclasses ''
-allowaccessmodification

# Keep R classes
-keepclassmembers class **.R$* {
    public static <fields>;
}


package com.example.batterymonitor;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * BroadcastReceiver that starts the BatteryMonitorService when the device boots
 * if battery monitoring was enabled before the device was shut down.
 */
public class BootReceiver extends BroadcastReceiver {
    private static final String TAG = "BootReceiver";
    private static final String PREFS_NAME = "BatteryMonitorPrefs";
    private static final String KEY_MONITORING_ENABLED = "monitoring_enabled";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            Log.d(TAG, "Boot completed");
            
            // Check if monitoring was enabled before shutdown
            SharedPreferences sharedPreferences = 
                    context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            boolean monitoringEnabled = sharedPreferences.getBoolean(KEY_MONITORING_ENABLED, false);
            
            if (monitoringEnabled) {
                Log.d(TAG, "Monitoring was enabled before shutdown, starting service");
                
                // Start the battery monitor service
                Intent serviceIntent = new Intent(context, BatteryMonitorService.class);
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent);
                } else {
                    context.startService(serviceIntent);
                }
            } else {
                Log.d(TAG, "Monitoring was disabled before shutdown, not starting service");
            }
        }
    }
}


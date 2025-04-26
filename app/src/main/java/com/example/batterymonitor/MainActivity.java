package com.example.batterymonitor;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.BatteryManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    private static final String PREFS_NAME = "BatteryMonitorPrefs";
    private static final String KEY_MONITORING_ENABLED = "monitoring_enabled";

    private TextView textBatteryLevel;
    private ProgressBar progressBattery;
    private SwitchCompat switchMonitor;
    private TextView textStatus;
    
    private boolean isMonitoringEnabled = false;
    private SharedPreferences sharedPreferences;
    
    private BroadcastReceiver batteryReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            updateBatteryUI(intent);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize views
        textBatteryLevel = findViewById(R.id.textBatteryLevel);
        progressBattery = findViewById(R.id.progressBattery);
        switchMonitor = findViewById(R.id.switchMonitor);
        textStatus = findViewById(R.id.textStatus);
        
        // Initialize shared preferences
        sharedPreferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        isMonitoringEnabled = sharedPreferences.getBoolean(KEY_MONITORING_ENABLED, false);
        
        // Set initial switch state
        switchMonitor.setChecked(isMonitoringEnabled);
        updateStatusText();
        
        // If monitoring was enabled, start the service
        if (isMonitoringEnabled) {
            startBatteryMonitorService();
        }
        
        // Set up switch change listener
        switchMonitor.setOnCheckedChangeListener((buttonView, isChecked) -> {
            isMonitoringEnabled = isChecked;
            saveMonitoringState();
            updateStatusText();
            
            if (isMonitoringEnabled) {
                startBatteryMonitorService();
                Toast.makeText(this, "Battery monitoring enabled", Toast.LENGTH_SHORT).show();
            } else {
                stopBatteryMonitorService();
                Toast.makeText(this, "Battery monitoring disabled", Toast.LENGTH_SHORT).show();
            }
        });
        
        // Get the initial battery level
        IntentFilter filter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        Intent batteryStatus = registerReceiver(null, filter);
        if (batteryStatus != null) {
            updateBatteryUI(batteryStatus);
        }
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Register battery level receiver
        IntentFilter filter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        registerReceiver(batteryReceiver, filter);
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // Unregister battery level receiver
        unregisterReceiver(batteryReceiver);
    }
    
    private void updateBatteryUI(Intent intent) {
        int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
        int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
        
        if (level != -1 && scale != -1) {
            int batteryPct = (int) ((level / (float) scale) * 100);
            textBatteryLevel.setText(getString(R.string.battery_level_display, batteryPct));
            progressBattery.setProgress(batteryPct);
            
            // Show battery status in logs
            Log.d(TAG, "Battery level updated: " + batteryPct + "%");
            
            // If we're in a low battery situation, also update the status text
            if (batteryPct <= 30) {
                textStatus.setText("CRITICAL: " + getString(R.string.status_monitoring));
            } else if (isMonitoringEnabled) {
                textStatus.setText(R.string.status_monitoring);
            }
        }
        
        // Also check if the device is charging
        int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
        boolean isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || 
                            status == BatteryManager.BATTERY_STATUS_FULL;
        
        if (isCharging && isMonitoringEnabled) {
            textStatus.setText("Charging - Alerts paused");
        }
    }
    
    private void saveMonitoringState() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putBoolean(KEY_MONITORING_ENABLED, isMonitoringEnabled);
        editor.apply();
        
        Log.d(TAG, "Saved monitoring state: " + isMonitoringEnabled);
    }
    
    private void updateStatusText() {
        textStatus.setText(isMonitoringEnabled ? 
                R.string.status_monitoring : R.string.status_idle);
    }
    
    private void startBatteryMonitorService() {
        Intent serviceIntent = new Intent(this, BatteryMonitorService.class);
        
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
        
        Log.d(TAG, "Started battery monitor service");
    }
    
    private void stopBatteryMonitorService() {
        Intent serviceIntent = new Intent(this, BatteryMonitorService.class);
        stopService(serviceIntent);
        
        Log.d(TAG, "Stopped battery monitor service");
    }
    
    @Override
    public boolean onCreateOptionsMenu(android.view.Menu menu) {
        // Inflate the menu resource
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(android.view.MenuItem item) {
        // Handle menu item selections
        int id = item.getItemId();
        
        if (id == R.id.action_help) {
            // Launch the Help activity
            Intent helpIntent = new Intent(this, HelpActivity.class);
            startActivity(helpIntent);
            return true;
        }
        else if (id == R.id.action_about) {
            // Launch the About activity
            Intent aboutIntent = new Intent(this, AboutActivity.class);
            startActivity(aboutIntent);
            return true;
        }
        
        return super.onOptionsItemSelected(item);
    }
}

package com.example.batterymonitor;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.BatteryManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;

import java.io.IOException;

public class BatteryMonitorService extends Service {

    private static final String TAG = "BatteryMonitorService";
    private static final String CHANNEL_ID = "BatteryMonitorChannel";
    private static final int NOTIFICATION_ID = 1;

    // Alert threshold battery levels and intervals
    private static final int LEVEL_HIGH = 50; // 50% - alert every 5 minutes
    private static final int LEVEL_MEDIUM = 40; // 40% - alert every 3 minutes
    private static final int LEVEL_LOW = 30; // 30% - alert every 2 minutes
    
    private static final long ALERT_INTERVAL_HIGH = 5 * 60 * 1000; // 5 minutes in ms
    private static final long ALERT_INTERVAL_MEDIUM = 3 * 60 * 1000; // 3 minutes in ms
    private static final long ALERT_INTERVAL_LOW = 2 * 60 * 1000; // 2 minutes in ms

    private Handler handler = new Handler(Looper.getMainLooper());
    private Runnable alertRunnable;
    private MediaPlayer mediaPlayer;
    private NotificationManager notificationManager;
    private int currentBatteryLevel = 100;
    private boolean isCharging = false;

    private BroadcastReceiver batteryReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            updateBatteryStatus(intent);
        }
    };

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "Battery Monitor Service created");
        
        notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        createNotificationChannel();
        
        // Register battery receiver
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_BATTERY_CHANGED);
        filter.addAction(Intent.ACTION_POWER_CONNECTED);
        filter.addAction(Intent.ACTION_POWER_DISCONNECTED);
        registerReceiver(batteryReceiver, filter);
        
        // Initialize MediaPlayer for alerts
        initMediaPlayer();
        
        // Set up alert runnable
        alertRunnable = () -> {
            if (!isCharging && shouldAlert()) {
                playAlertSound();
                scheduleNextAlert();
            }
        };
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "Battery Monitor Service started");
        
        // Start as a foreground service with notification
        startForeground(NOTIFICATION_ID, createNotification());
        
        // Check current battery status
        Intent batteryStatus = registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
        if (batteryStatus != null) {
            updateBatteryStatus(batteryStatus);
        }
        
        // Schedule initial alert check if necessary
        if (!isCharging && shouldAlert()) {
            scheduleNextAlert();
        }
        
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        Log.d(TAG, "Battery Monitor Service destroyed");
        
        // Unregister battery receiver
        unregisterReceiver(batteryReceiver);
        
        // Remove any scheduled alerts
        handler.removeCallbacks(alertRunnable);
        
        // Release MediaPlayer
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
        
        super.onDestroy();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null; // Not supporting binding
    }

    private void updateBatteryStatus(Intent intent) {
        String action = intent.getAction();
        
        if (Intent.ACTION_POWER_CONNECTED.equals(action)) {
            isCharging = true;
            handler.removeCallbacks(alertRunnable); // Cancel alerts when charging
            updateNotification();
        } else if (Intent.ACTION_POWER_DISCONNECTED.equals(action)) {
            isCharging = false;
            if (shouldAlert()) {
                scheduleNextAlert();
            }
            updateNotification();
        } else if (Intent.ACTION_BATTERY_CHANGED.equals(action)) {
            int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
            int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
            
            if (level != -1 && scale != -1) {
                int oldLevel = currentBatteryLevel;
                currentBatteryLevel = (int) ((level / (float) scale) * 100);
                
                // Update notification with new battery level
                updateNotification();
                
                // If battery level dropped to a new threshold and not charging
                if (!isCharging && currentBatteryLevel < oldLevel && shouldAlert()) {
                    // Cancel previous alert schedule
                    handler.removeCallbacks(alertRunnable);
                    // Play alert immediately for threshold change and schedule next one
                    playAlertSound();
                    scheduleNextAlert();
                }
                
                int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
                isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || 
                             status == BatteryManager.BATTERY_STATUS_FULL;
                
                if (isCharging) {
                    handler.removeCallbacks(alertRunnable); // Cancel alerts when charging
                }
            }
        }
    }

    private boolean shouldAlert() {
        return currentBatteryLevel <= LEVEL_HIGH;
    }

    private long getAlertInterval() {
        if (currentBatteryLevel <= LEVEL_LOW) {
            return ALERT_INTERVAL_LOW;
        } else if (currentBatteryLevel <= LEVEL_MEDIUM) {
            return ALERT_INTERVAL_MEDIUM;
        } else if (currentBatteryLevel <= LEVEL_HIGH) {
            return ALERT_INTERVAL_HIGH;
        }
        return ALERT_INTERVAL_HIGH; // Default to longest interval
    }

    private void scheduleNextAlert() {
        long interval = getAlertInterval();
        Log.d(TAG, "Scheduling next alert in " + (interval / 1000) + " seconds");
        handler.postDelayed(alertRunnable, interval);
    }

    private void playAlertSound() {
        Log.d(TAG, "Playing alert sound for battery level: " + currentBatteryLevel + "%");
        
        if (mediaPlayer != null) {
            mediaPlayer.start();
            
            // Show a warning notification
            showWarningNotification();
        }
    }

    private void initMediaPlayer() {
        mediaPlayer = new MediaPlayer();
        try {
            // Use default notification sound
            Uri alertSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            mediaPlayer.setDataSource(this, alertSound);
            
            AudioAttributes audioAttributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();
            mediaPlayer.setAudioAttributes(audioAttributes);
            
            mediaPlayer.setOnPreparedListener(MediaPlayer::start);
            mediaPlayer.setOnCompletionListener(mp -> mp.reset());
            mediaPlayer.prepareAsync();
        } catch (IOException e) {
            Log.e(TAG, "Failed to set data source for MediaPlayer", e);
        }
    }

    private void createNotificationChannel() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    getString(R.string.notification_channel_name),
                    NotificationManager.IMPORTANCE_LOW);
            channel.setDescription(getString(R.string.notification_channel_description));
            notificationManager.createNotificationChannel(channel);
            
            // Create a separate high-importance channel for warning notifications
            NotificationChannel alertChannel = new NotificationChannel(
                    CHANNEL_ID + "Alerts",
                    "Battery Alert Warnings",
                    NotificationManager.IMPORTANCE_HIGH);
            alertChannel.setDescription("High priority battery alerts");
            notificationManager.createNotificationChannel(alertChannel);
        }
    }

    private Notification createNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);

        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle(getString(R.string.notification_title))
                .setContentText(getString(R.string.notification_text, currentBatteryLevel))
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .build();
    }
    
    private void updateNotification() {
        notificationManager.notify(NOTIFICATION_ID, createNotification());
    }
    
    private void showWarningNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);
                
        Notification warningNotification = new NotificationCompat.Builder(this, CHANNEL_ID + "Alerts")
                .setContentTitle(getString(R.string.warning_battery_low, currentBatteryLevel))
                .setContentText(getString(R.string.plugin_reminder))
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentIntent(pendingIntent)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setAutoCancel(true)
                .build();
                
        // Use a different notification ID so it doesn't replace our foreground notification
        notificationManager.notify(NOTIFICATION_ID + 1000, warningNotification);
    }
}

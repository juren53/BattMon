package com.example.batterymonitor;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ImageView;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Splash screen that displays briefly when the app is launched
 */
public class SplashActivity extends AppCompatActivity {

    private static final long SPLASH_DISPLAY_TIME = 1500; // 1.5 seconds

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        // Simple fade-in animation for the battery icon
        try {
            ImageView batteryIcon = findViewById(R.id.imageViewBattery);
            Animation fadeIn = AnimationUtils.loadAnimation(this, android.R.anim.fade_in);
            fadeIn.setDuration(1000);
            batteryIcon.startAnimation(fadeIn);
        } catch (Exception e) {
            // If animation fails, simply continue - keeps the app lightweight
        }

        // Use handler to delay loading the main activity
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            // Start the main activity
            Intent mainIntent = new Intent(SplashActivity.this, MainActivity.class);
            startActivity(mainIntent);
            
            // Close the splash screen activity
            finish();
            
            // Add a simple transition
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
        }, SPLASH_DISPLAY_TIME);
    }
}


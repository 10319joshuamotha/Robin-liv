package com.robin.companion

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat

class AlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val manager = context.getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel("robin_alarm", "Robin alarms", NotificationManager.IMPORTANCE_HIGH))
        val label = intent.getStringExtra("label") ?: "Robin alarm"
        val notification = NotificationCompat.Builder(context, "robin_alarm")
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm).setContentTitle("Robin")
            .setContentText(label).setAutoCancel(true).build()
        manager.notify((System.currentTimeMillis() and 0x7fffffff).toInt(), notification)
    }
}

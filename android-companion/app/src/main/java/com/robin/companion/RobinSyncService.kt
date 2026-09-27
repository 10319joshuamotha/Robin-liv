package com.robin.companion

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.IBinder
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class RobinSyncService : Service() {
    private var socket: WebSocket? = null
    private val client = OkHttpClient.Builder().pingInterval(25, TimeUnit.SECONDS).build()

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(7, notification())
        val prefs = getSharedPreferences("robin", MODE_PRIVATE)
        val url = intent?.getStringExtra("url") ?: prefs.getString("ws_url", null)
        val token = intent?.getStringExtra("token") ?: prefs.getString("token", null)
        if (!url.isNullOrBlank() && !token.isNullOrBlank()) connect(url, token)
        return START_STICKY
    }

    private fun connect(url: String, token: String) {
        socket?.cancel()
        val sep = if (url.contains("?")) "&" else "?"
        val request = Request.Builder().url(url + sep + "token=" + token).build()
        socket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) { runCatching { execute(JSONObject(text)) } }
        })
    }

    private fun execute(obj: JSONObject) {
        if (obj.optString("type") != "task") return
        val id = obj.optString("task_id")
        val payload = obj.optJSONObject("payload") ?: JSONObject()
        val result = when (obj.optString("capability")) {
            "phone.call" -> PhoneActions(this).call(payload.optString("contact"))
            "phone.alarm" -> PhoneActions(this).alarm(payload.optInt("hour"), payload.optInt("minute"), payload.optString("label", "Robin"))
            else -> Result.failure(UnsupportedOperationException("Unsupported capability: " + obj.optString("capability")))
        }
        socket?.send(JSONObject().apply {
            put("type", "task_result"); put("task_id", id); put("ok", result.isSuccess)
            put("message", result.exceptionOrNull()?.message ?: "completed")
        }.toString())
    }

    private fun notification(): Notification {
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel("robin_sync", "Robin sync", NotificationManager.IMPORTANCE_LOW))
        return Notification.Builder(this, "robin_sync").setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Robin").setContentText("Assistant connection active").build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

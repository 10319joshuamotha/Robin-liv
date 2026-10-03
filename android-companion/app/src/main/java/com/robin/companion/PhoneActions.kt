package com.robin.companion

import android.Manifest
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.ContactsContract
import androidx.core.content.ContextCompat
import java.util.Calendar

class PhoneActions(private val context: Context) {
    fun call(contact: String): Result {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED)
            return Result.failure(SecurityException("CALL_PHONE permission is required"))
        val number = resolveContact(contact) ?: contact.takeIf { it.matches(Regex("[+0-9 ()-]{3,}")) }
            ?: return Result.failure(IllegalArgumentException("Contact or phone number not found: " + contact))
        context.startActivity(Intent(Intent.ACTION_CALL, Uri.parse("tel:" + Uri.encode(number))).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        return Result.success(Unit)
    }

    fun alarm(hour: Int, minute: Int, label: String): Result {
        require(hour in 0..23 && minute in 0..59)
        val intent = Intent(context, AlarmReceiver::class.java).putExtra("label", label)
        val requestCode = (System.currentTimeMillis() and 0x7fffffff).toInt()
        val pending = PendingIntent.getBroadcast(context, requestCode, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val cal = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour); set(Calendar.MINUTE, minute); set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
            if (timeInMillis <= System.currentTimeMillis()) add(Calendar.DAY_OF_YEAR, 1)
        }
        context.getSystemService(AlarmManager::class.java).setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, cal.timeInMillis, pending)
        return Result.success(Unit)
    }

    private fun resolveContact(name: String): String? {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) return null
        val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val projection = arrayOf(ContactsContract.CommonDataKinds.Phone.NUMBER)
        context.contentResolver.query(uri, projection, ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " LIKE ?", arrayOf(name), null)?.use { c ->
            if (c.moveToFirst()) return c.getString(0)
        }
        return null
    }
}

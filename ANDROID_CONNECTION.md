# Windows ↔ Android connection

Robin uses the Windows PC as the host and an Android phone as a local companion/control device.

## What the connection provides

- QR-based one-time pairing from the Robin desktop.
- Android control through the Robin dashboard in the phone browser.
- Text commands from Android to Robin.
- Android microphone audio streamed to Robin's Gemini Live session.
- Robin status, messages, wake state, and connection events streamed back to Android.
- File upload from Android to the Windows host.
- Persistent device token support so a previously paired Android device can reconnect without scanning the QR every time.
- Device revocation from the authenticated dashboard.
- LAN-only operation; the phone and Windows PC should be on the same Wi-Fi/LAN.

## Windows setup

1. On the Windows PC, clone or download this repository.
2. Open PowerShell in the repository folder.
3. Run:

   powershell -ExecutionPolicy Bypass -File .\install_windows.ps1

4. Start Robin:

   .\start_robin_windows.bat

5. Allow the Windows Firewall/UAC request when Robin asks to expose the dashboard on the local network.

Robin's dashboard listens on the LAN interface. The existing dashboard code creates a local self-signed certificate and QR pairing key at runtime; private certificate material is not stored in Git.

## Android pairing

1. Make sure Android and the Windows PC are on the same Wi-Fi/LAN.
2. Start Robin on Windows.
3. Select Remote Control in the Robin desktop UI.
4. Scan the displayed QR code with the Android camera.
5. Android opens the Robin dashboard and establishes a one-time authenticated session.
6. Keep the dashboard open for live remote control and phone microphone use.

The QR key is one-time and expires. A new QR code can be generated if pairing expires.

## Reconnecting

After the first successful pairing, Robin stores a device token in the Android browser's local storage. When the dashboard is opened again on that browser, the device can obtain a fresh session token without repeating QR pairing.

If the browser's site data is cleared, pair the phone again.

## Phone microphone

Use the microphone button in the Android dashboard. The browser requests microphone permission and sends PCM audio over the authenticated WebSocket to Robin.

If Android reports a microphone permission error, allow microphone access for the browser in Android settings and retry.

## Network notes

- This is intended for a trusted home/local network.
- Do not port-forward the Robin dashboard to the public internet.
- The Windows firewall setup is best-effort and may require an administrator/UAC approval.
- HTTPS uses a machine-local self-signed certificate. Android may display a certificate warning on first use; the QR flow is still bound to the local host.
- If the phone cannot connect, verify both devices are on the same LAN, Windows Firewall allows Robin's dashboard port, and the PC's network profile is appropriate for local device discovery.

## Architecture

Windows host: Robin desktop -> DashboardServer -> authenticated WebSocket/HTTP -> LAN

Android companion: Chrome/Android browser -> QR-paired dashboard -> WebSocket + HTTP -> Windows host

The Android side intentionally uses the browser dashboard rather than requiring a separate APK. This keeps pairing and updates local to the Robin installation and avoids an Android build toolchain for the companion.

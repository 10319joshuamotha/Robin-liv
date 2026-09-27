# Robin connection architecture

## Roles

### Windows
The Windows machine is the authoritative Robin host.

- Runs the desktop UI and Gemini Live session.
- Owns the dashboard server.
- Generates the local TLS certificate.
- Generates one-time pairing keys.
- Owns authenticated sessions and persistent device tokens.
- Relays Android microphone audio into the live audio queue.
- Relays Robin status and messages back to connected clients.

### Android
Android is a companion device.

- Opens the dashboard from the QR code.
- Uses a browser session rather than a native APK.
- Sends commands over authenticated HTTP/WebSocket.
- Can stream microphone PCM audio.
- Receives Robin status/log events.
- Can upload files to the Windows host.

## Connection lifecycle

1. Windows starts DashboardServer.
2. Robin generates a LAN address and one-time pairing key when Remote Control requests pairing.
3. The desktop displays a QR code containing the local dashboard pairing URL.
4. Android scans the QR code.
5. Windows consumes the one-time key and issues:
   - a session bearer token for the current browser session;
   - a persistent device token for subsequent reconnects.
6. The Android browser stores the device token locally.
7. Subsequent dashboard opens can exchange the device token for a fresh session token.
8. Commands and microphone traffic are accepted only for authenticated tokens.
9. The Windows host can revoke all persistent device tokens from the authenticated dashboard.

## Security boundary

Pairing is local-network authentication, not internet authentication. The QR key is single-use and expires. Session tokens are random bearer credentials. The dashboard does not expose a public cloud relay.

Do not expose the dashboard port to the public internet or configure router port forwarding for it.

## Failure handling

- Expired pairing key -> generate a new QR code.
- Cleared Android site data -> pair again.
- Lost Wi-Fi -> reopen the dashboard after reconnecting to the same LAN.
- Windows firewall blocks the port -> approve the UAC/firewall setup or allow the configured dashboard TCP port manually.
- Invalid session token -> dashboard returns to the login/pairing flow.

## Why browser-based Android

A browser companion is the smallest deployable Android connection type for Robin: no APK signing, Play Store distribution, Android Studio, or separate update channel is required. The Windows host remains the single source of truth and the phone connects directly over the LAN.

# Windows ↔ Android companion

Robin is moving from a LAN-only phone dashboard toward a **hybrid assistant**.

## Intended behavior

The Windows PC remains the main Robin host, while Android becomes a native
phone-side executor.

Examples:

- "Robin, call John." -> Android handles the phone call.
- "Set an alarm for 6:30 AM." -> Android creates the alarm locally.
- "Remind me at 8 PM to send the report." -> Android stores/delivers the reminder.
- "Open my project on the PC." -> Windows executes the task.
- When Windows and Android are on different networks, a cloud relay synchronizes
  the request/result.

## Connectivity

Robin should use this order:

1. **Direct LAN connection** when Windows and Android are reachable locally.
2. **Authenticated cloud relay** when they are on different networks.
3. **Android-local execution** for tasks that Android can complete without Robin
   being online, such as an already-scheduled alarm or reminder.

Internet connectivity is therefore useful for cross-network synchronization, but
it must not be a prerequisite for every phone action.

## Current state

The existing browser companion remains available as a prototype. It provides
QR pairing, authenticated sessions, phone microphone streaming, status/messages,
and file transfer.

The native Android assistant, cloud relay, background execution, phone calling,
contacts, alarms, notifications, and full voice-assistant experience are the
next implementation stage.

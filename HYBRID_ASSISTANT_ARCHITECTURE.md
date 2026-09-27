# Robin hybrid Windows + Android assistant

Robin is being built as a **distributed assistant**, not just a phone remote-control
page.

## Target architecture

```
                         Internet
                    ┌────────────────┐
                    │  Robin Cloud   │
                    │ relay/sync     │
                    └───────┬────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          Windows Robin             Android Robin
          main assistant            native companion
                │                       │
                └──── local LAN ────────┘
```

The cloud is a **transport and synchronization layer**. It is not required to
execute every action.

### Where actions execute

| Request | Preferred executor |
|---|---|
| Open an app / edit a Windows file | Windows |
| Run a Windows automation | Windows |
| "Call John" | Android |
| "Set an alarm for 6:30" | Android |
| Phone notification/reminder | Android |
| Read phone contacts | Android |
| Ask Robin to do a Windows task while away from the PC | Cloud relay -> Windows |
| Windows + Android on same LAN | Direct local connection |

When both devices can see each other locally, Robin should prefer the local
connection. When they are on different networks, the cloud relay carries the
task.

## Important offline behavior

Phone-local tasks must be scheduled/executed on Android rather than depending
on a live Windows connection. For example, once Android has accepted
"set an alarm for 6:30 AM", the alarm belongs to Android's OS and should fire
even if Windows is off and the internet is unavailable.

Likewise, a reminder that has already been synchronized to Android should be
deliverable locally.

## Voice-assistant examples

The eventual native Android app should support requests such as:

- "Robin, call John."
- "Robin, set an alarm for 6:30 tomorrow morning."
- "Remind me at 8 PM to send the report."
- "Tell Robin on my PC to open the project."
- "What did I ask Robin to remind me about?"

Actions that can cause an external side effect, especially calls/messages,
should use Robin's existing confirmation policy where appropriate.

## Current implementation vs target

The repository currently has a browser/PWA companion with QR pairing,
authenticated WebSocket communication, phone microphone streaming, file
transfer, and a persistent device token held in the running Windows server.

That browser companion is a **prototype transport/UI**, not the final Android
assistant. The native Android app still needs to be built.

The companion protocol in `core/companion_protocol.py` is the first shared
contract for that next stage. It deliberately has no cloud-provider dependency,
so a cloud relay can be added later without changing the task format.

## Security requirements for the next stage

- Pair devices with short-lived one-time credentials.
- Replace those credentials with revocable long-lived device credentials.
- Never expose the Windows control API directly to the public internet.
- Use authenticated, encrypted cloud transport.
- Bind every task and result to a device identity and task ID.
- Expire stale scheduled commands.
- Require explicit confirmation for sensitive phone actions when policy calls for it.
- Keep phone-local alarms/reminders usable without an internet connection.

## Android direction

The final Android companion should be a native app rather than relying only on
the browser. It will provide the OS integrations needed for calling, alarms,
notifications, contacts, background synchronization, and voice interaction.

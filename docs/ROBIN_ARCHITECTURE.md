# Robin architecture — foundation requirements

This document defines the target architecture for Robin before device-specific implementation is added.

## 1. Identity

Robin is one persistent personal assistant, not separate PC and phone assistants. Device clients are interfaces to the same Robin identity, memory, preferences, relationships, permissions, and skills.

The authoritative host for the current build is Windows. The Android device is a companion client. The design must not make the identity permanently dependent on either device so future platforms can be added.

## 2. Storage model

The Windows PC contains Robin's primary brain: executable/core runtime, essential configuration, safety policy, and the minimum data required to start and operate without the external drive.

The user's approximately 117 GB USB drive is the external knowledge/data layer. It is intended for long-term memory, knowledge, documents, datasets, media/assets, and other high-volume non-essential data.

The USB must be treated as optional external storage. If it is disconnected, Robin remains able to start and operate with the local brain and reports that external memory is unavailable. Code must never assume a fixed drive letter; the external data root must be discovered/configured safely.

No physical USB migration or repository-wide storage change is part of this foundation commit.

## 3. Device operating states

### Windows PC

- `ACTIVE`: normal Robin operation.
- `SLEEPING`: Robin does not process microphone audio, camera input, screen input, Gemini conversation, or ordinary background assistant activity. A minimal local keyboard wake path remains available for ESC.
- `OFFLINE`: Robin is not running.

When the user says `sleep`, the PC client enters `SLEEPING`. Pressing ESC is the local wake mechanism. After waking, normal listening/wake-word behavior can resume.

### Android phone

- `ACTIVE`: normal companion operation.
- `PRIVATE`: screen/visual access is disabled at the capability boundary. Robin must not capture, inspect, stream, or use the phone screen as context. Audio and unrelated capabilities are not implicitly disabled by Private Mode.
- `OFFLINE`: companion disconnected/not running.

The user command `private mode off` returns the phone to `ACTIVE`.

Privacy is a system-enforced permission state, not a prompt instruction to the model.

## 4. Capability enforcement

Every sensitive capability must consult the device state before executing. In particular:

- Phone screen capture/inspection is denied in `PRIVATE`.
- PC microphone processing is denied in `SLEEPING`.
- PC camera/screen capture is denied in `SLEEPING`.
- PC AI/session processing is denied in `SLEEPING`.
- ESC wake handling is allowed while the PC is `SLEEPING`.

The model must not be the authority that decides whether a restricted capability is permitted.

## 5. Cross-device identity

A command received on the phone and a command received on the PC are inputs to the same Robin identity. Memory, preferences, relationships, and persistent user facts belong to Robin rather than to a single device.

Device-specific permissions and capabilities remain local to each device.

## 6. Calling requirement

Robin should eventually be able to initiate a real incoming VoIP call to the user's Android phone, with Android's native incoming-call/Telecom experience and two-way voice conversation.

The current browser-based Android dashboard is not itself a native phone-call implementation. The calling layer should therefore be introduced as a separate Android native companion capability rather than pretending the browser dashboard is a cellular/Telecom caller.

## 7. Future platforms

The core should expose device-neutral operations while clients provide platform-specific capabilities. Future clients may include iOS, macOS, Linux, web, or other devices without creating a second Robin identity.

## 8. Implementation order

1. Establish explicit state and permission primitives.
2. Separate Robin identity/memory from device clients.
3. Make PC sleep and phone privacy state enforceable at capability boundaries.
4. Establish external USB storage discovery and graceful absence handling.
5. Harden the existing Windows/Android connection layer.
6. Add a native Android calling client using Android Telecom/VoIP APIs.
7. Move remaining runtime responsibilities out of the monolithic `main.py` behind these boundaries.

This foundation intentionally avoids rewriting the existing runtime in one step. Existing behavior should be preserved until each subsystem has a replacement and tests.

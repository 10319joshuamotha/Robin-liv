# Robin final specification

## Product goal

Robin is a persistent personal AI assistant shared across Joshua's PC and phone, with a device-independent identity, persistent memory, explicit permissions, offline fallback capabilities, a lightweight animated 2D character, cross-device task continuity, and optional proactive communication.

## Identity and users

- Primary user: Joshua.
- Secondary authorized user: Joshua's wife, with a separate profile/memory context.
- PC authentication: wake sentence + enrolled voice verification.
- Phone authentication: device biometric authentication (fingerprint/face where supported) plus enrolled voice verification for voice access.
- Robin must not infer authorization from conversation content alone.

## Memory

Robin should maintain structured long-term understanding of:

- preferences
- routines
- relationships
- user-specific context
- useful personal facts
- task history where enabled
- device context
- user-provided knowledge

Users can ask what Robin remembers and request deletion. Credentials may be stored only in an encrypted credential vault; they must never be ordinary AI memory or plaintext knowledge.

## Security and prohibited/guarded domains

- GPay and money-related actions are disabled by default.
- Any future financial capability requires a three-step verification/authorization flow and explicit implementation-level safeguards.
- Gallery access is forbidden by default and can be granted for the explicitly selected picture or tab/task; authorization expires when the authorized task completes unless explicitly extended.
- Phone screen capture/viewing must be impossible while Phone Private Mode is active.
- PC Sleep must stop all normal Robin processing until ESC wakes the system.

## Phone Private Mode

Command: `Private mode`.

While active:

- screen viewing/capture: OFF
- screen-derived context: OFF
- cloud screen transmission: OFF
- microphone/voice interaction: ON unless the user separately disables it
- camera: ON only if a separate camera command is explicitly requested; no screen access is implied
- normal Robin processing: ON

`Private mode off` restores normal phone capabilities.

## PC Sleep

Command: `Robin, sleep`.

While sleeping:

- microphone processing: OFF
- wake-word detection: OFF
- camera processing: OFF
- screen monitoring: OFF
- Gemini/AI sessions: OFF
- normal assistant processing: OFF
- background Robin activity: OFF
- ESC listener: ON only for wake
- animation: sleeping state / no active animation

Pressing ESC wakes Robin, activates the animation, restores listening, and returns the PC to ACTIVE state.

Wake word: `Robin`.

## Offline operation

Offline support is a resilience/fallback mode, not a replacement for cloud reasoning.

The PC should retain enough local capability for:

- wake word
- speech recognition
- text-to-speech
- basic command routing
- core memory lookup
- local PC automation where safe
- state/privacy enforcement
- animation

When Internet/Gemini services are unavailable, advanced reasoning/search features should degrade gracefully rather than making Robin unusable.

## Voice

Default language: English.

Robin understands multilingual input and can respond in another language when explicitly requested. She should retain the selected language preference until changed.

Voice target: mature woman around 30, warm, soothing, natural. Offline TTS is required for fallback operation.

## Personality

Personality is situation-aware. Humor is adaptive, dry/witty and conversational, inspired by the user's requested Chandler-like style without copying protected dialogue or impersonating the character.

## PC automation

Robin may autonomously perform ordinary low-risk actions based on established user routines. High-risk actions require explicit confirmation. Destructive, security-sensitive, financial and credential operations are subject to stronger authorization.

When Joshua says he is leaving/done for the day, Robin should:

1. identify active work;
2. close ordinary tabs/applications automatically;
3. detect unsaved work and ask before closing it;
4. terminate active Robin PC work cleanly;
5. shut down/sleep the PC according to the configured leaving routine;
6. remain active through the phone client.

## Cross-device continuity

Tasks started on one device can be continued from another. The user can explicitly tell Robin they are continuing on the phone, and Robin should restore task context safely.

The phone can request/send files to the PC and the PC can send files to the phone. Transfers must use authenticated encrypted transport and explicit file-selection/permission boundaries.

## Phone screen casting

The user can request the phone screen to be displayed on the PC. Screen capture/control must respect Private Mode. Control of the phone from the PC is a separate capability and must require explicit authorization.

## Calling

Robin may initiate a real incoming VoIP-style call to the user's phone when authorized by the user's calling rules. Proactive calling follows the user's requested autonomous behavior, subject to privacy, identity and permission rules.

## Animation

Robin is a full-body 2D character named Nico Robin, presented as a desktop companion.

The character should:

- idle naturally
- walk around the taskbar/desktop region
- jump/interact with available visual elements/fidgets
- react to voice and situation
- show listening/thinking/speaking states
- use task-specific animations during automation
- show success/error/completion states
- sleep with Robin when PC Sleep is active
- become active when ESC wakes Robin
- support animation on/off independently of assistant operation

Animation is a presentation layer driven by explicit assistant/tool/device states, not an independent AI decision-maker.

Example: `open Projects and rename it Work` should produce a listening -> thinking -> executing/working -> success sequence while the actual file automation runs.

The renderer must be optimized for the user's GT 710 / 8 GB baseline and have a performance-safe mode without materially reducing PC responsiveness.

## Engineering knowledge

Robin should be able to assist with learning/design/problem-solving in:

- mechanical engineering
- electrical/electronics
- CAD workflows
- civil engineering
- MEP
- HVAC
- materials/reference information
- chemistry and all periodic-table elements

This knowledge should be treated as reference/assistant capability. Safety-critical engineering decisions must include appropriate warnings and should not be presented as professional certification.

## Hardware efficiency

The implementation must include resource-aware configuration for the user's baseline:

- Intel i5-9400F
- 8 GB RAM initially, with 16 GB as the preferred upgrade
- NVIDIA GT 710 2 GB
- Windows 11 Pro 25H2
- approximately 117 GB detachable USB storage
- POCO X6 5G

Robin should minimize idle CPU, RAM, GPU and network use; pause unnecessary background work; cap animation/render frequency; reuse connections; avoid persistent screen polling; and degrade visual effects before compromising system responsiveness.

The phone client should similarly minimize battery, CPU, memory, camera/microphone and network usage.

## Storage architecture

PC internal storage holds the primary brain/runtime and required local/offline assets.

The detachable ~117 GB USB holds external knowledge, long-term data, documents, engineering references, large datasets, archives and other non-boot-critical content.

The USB is optional at runtime. Absence must not prevent Robin from starting.

A segregation manifest must be shipped with the project so the user can identify what belongs on the PC versus the USB after extraction.

## Portability

Robin's core and external data must be exportable as separate packages. A second machine should be able to install the core and attach/import a compatible external data package without copying device-specific secrets.

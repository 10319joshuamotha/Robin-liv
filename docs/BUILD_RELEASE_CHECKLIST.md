# Robin build/release checklist

This is the release gate for the requested Robin implementation. A checked item means the implementation exists and has been integration-tested on the target device; documentation alone does not qualify.

## Core

- [x] Central capability policy
- [x] Structured user memory model
- [x] PC/phone state model
- [x] Detachable storage discovery
- [x] Animation state model
- [x] Resource profile
- [ ] Runtime wiring to live audio/Gemini/action loop
- [ ] Encrypted credential vault
- [ ] Voice identity enrollment/verification
- [ ] Offline STT/TTS runtime
- [ ] Cross-device authenticated task/session protocol

## PC

- [ ] Actual PC Sleep stops Robin's microphone/AI/background processing
- [ ] ESC-only wake path remains alive during Sleep
- [ ] Wake word resumes after ESC wake
- [ ] Full task-driven Nico Robin animation
- [ ] Animation on/off command
- [ ] Safe leaving-home shutdown workflow
- [ ] Unsaved-work detection/confirmation

## Phone

- [ ] Native Android client
- [ ] Biometric + voice authorization
- [ ] Enforced Private Mode at capture/API boundaries
- [ ] One-shot gallery/tab authorization
- [ ] Phone↔PC file transfer
- [ ] Phone screen casting to PC
- [ ] Authorized remote phone control
- [ ] Cross-device continuation

## Communication

- [ ] Authenticated Robin-to-phone calling
- [ ] Reminder/proactive-call policy
- [ ] Offline fallback behavior

## Knowledge

- [ ] External USB knowledge package
- [ ] Portable segregation manifest and exporter
- [ ] Engineering knowledge/reference ingestion pipeline
- [ ] Chemistry/periodic-table reference package

## Security

- [ ] Hard GPay/payment boundary
- [ ] Three-step financial verification
- [ ] Secret redaction in logs/prompts
- [ ] Separate Joshua/wife profiles
- [ ] Explicit memory deletion

## Release criteria

Do not call the project complete until all required boxes above are implemented, tested, and verified against the Windows PC and Android target. If a platform capability cannot be safely implemented through the available APIs, document the limitation instead of simulating completion.

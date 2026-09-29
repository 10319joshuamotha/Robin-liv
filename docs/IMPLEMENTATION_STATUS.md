# Robin implementation status

This file distinguishes implemented foundations from features that still require device-specific integration/testing. It is intentionally conservative: a specification or state model is not marked as a completed product feature until it is wired into the runtime.

## Implemented foundations

- Device state/capability model for PC Sleep and phone Private Mode.
- Central deny-by-default policy for sensitive capabilities.
- Structured user-scoped memory schema with deletion.
- Marker-based detachable external storage discovery.
- Deterministic animation state controller.
- Conservative low-resource desktop performance profile.
- Unified runtime coordinator connecting device and animation states.
- Existing repository action discovery, browser/file automation, audio/Gemini runtime and avatar/viseme layers remain available.

## Requires integration before release

- Wire `RobinRuntime` into the live Gemini/audio loop so state changes actually gate I/O.
- Connect ESC to a true PC sleep transition and guarantee microphone/Gemini/screen/camera shutdown.
- Connect phone Private Mode to the Android screen-capture pipeline.
- Implement real two-user voice enrollment and biometric handoff.
- Implement encrypted credential vault; never use ordinary memory for passwords.
- Implement three-step financial authorization and keep GPay/payment capabilities disabled by default.
- Implement one-shot gallery/tab grants at the media access layer.
- Implement durable memory storage and retrieval on PC/USB.
- Implement PC/USB export/import manifests and portable data packaging.
- Implement native Android client integration for cross-device tasks, file transfer and screen casting.
- Implement Android Telecom/VoIP calling service.
- Replace/extend the current drawn overlay with the full task-aware 2D character behavior requested by the user.
- Implement offline STT/TTS fallback and resource-aware model loading.
- Integrate multilingual response selection and persistent language preference.
- Add engineering knowledge ingestion/retrieval without claiming professional certification.
- Add end-to-end tests on Windows and Android; CI compile/tests alone are not sufficient.

## Release rule

Do not describe Robin as complete until the integration items above have passed their relevant tests on the target PC/phone environment.

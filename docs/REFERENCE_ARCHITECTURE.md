# Robin reference architecture

This document records implementation patterns reviewed from several public JARVIS projects. It is an architecture reference, not copied source code.

## Patterns to adopt

### 1. Windows-native local voice pipeline
Use a local wake-word detector -> local STT -> reasoning/tool loop -> TTS pipeline. The reviewed samonti86 project uses openWakeWord and faster-whisper locally, with a TTS fallback, and explicitly treats Windows-native audio as a design requirement. This fits Robin's offline-first requirement. [Source: https://github.com/samonti86/jarvis]

### 2. Preflight / doctor command
Add a read-only environment diagnostic that reports Python, microphone, speaker, model availability, storage paths, GPU/RAM and missing optional components without changing the machine. The reviewed samonti86 project exposes `python scripts/doctor.py`, and D3v0ps exposes `--preflight`/repair behavior. [Sources: https://github.com/samonti86/jarvis, https://github.com/D3v0ps/JARVIS]

### 3. Local LLM abstraction
Keep the reasoning layer provider-independent so Robin can use a local Ollama/LM Studio model offline and a cloud provider only when explicitly configured. PanPenek's project supports Ollama, LM Studio, OpenAI-compatible providers and offline voice components. [Source: https://github.com/PanPenek/JarvisAi]

### 4. Tool registry with a single security boundary
Keep tool discovery separate from execution, but require every sensitive tool to pass RobinPolicy immediately before invocation. Alan7149's architecture uses purpose-built tools behind a permission engine; samonti86 uses an agentic tool layer and per-origin boundaries. Robin's policy remains the final authority. [Sources: https://github.com/Alan7149/JARVIS, https://github.com/samonti86/jarvis]

### 5. Explicit confirmation for destructive operations
Dangerous actions should be announced and confirmed before execution. D3v0ps demonstrates a confirm-before-PowerShell interaction. Robin additionally hard-denies financial operations regardless of verification. [Source: https://github.com/D3v0ps/JARVIS]

### 6. Persistent memory plus profile and RAG
Separate conversational history, user profile facts, and document knowledge. yontanbe's project separates memory/profile/RAG; PanPenek uses SQLite/ChromaDB semantic memory. Robin should keep secrets out of ordinary profile memory and store credentials only in a dedicated encrypted vault. [Sources: https://github.com/yontanbe/jarvis, https://github.com/PanPenek/JarvisAi]

### 7. Phone bridge rather than embedding Android behavior into the PC core
Use a narrow authenticated bridge for phone actions. Alan7149 combines ADB/scrcpy/webhook-style phone control, while samonti86 exposes phone/Discord clients. Robin should preserve Private Mode and explicit media grants at the phone boundary. [Sources: https://github.com/Alan7149/JARVIS, https://github.com/samonti86/jarvis]

### 8. UI/animation as a separate presentation layer
Do not make animation part of the assistant's core decision loop. D3v0ps uses an ambient overlay and explicit overlay tests; samonti86 caches animation frames so rendering stays cheap. Robin's 2D character should consume runtime state events and never block the assistant. [Sources: https://github.com/D3v0ps/JARVIS, https://github.com/samonti86/jarvis]

### 9. Installer/update discipline
A working Robin needs preflight, install, repair and update entry points. D3v0ps keeps config, memory, models and virtual environment stable during updates; yontanbe keeps runtime data out of source control. Robin should follow the same separation for its PC core and detachable USB brain. [Sources: https://github.com/D3v0ps/JARVIS, https://github.com/yontanbe/jarvis]

## Corrections to avoid

- Do not use a generic action-name substring alone as the final security authority; capabilities must be explicit metadata where possible.
- Do not treat a green unit-test suite as proof of Windows or Android integration.
- Do not store passwords in ordinary memory/profile files.
- Do not make screen capture a background default; Private Mode must gate it at the lowest practical layer.
- Do not make the animation renderer part of the AI/tool execution path.
- Do not require the internet for the basic voice loop if an offline model is installed.

## Robin target pipeline

`microphone -> wake word -> local STT -> session/auth/privacy gate -> reasoning -> explicit tool policy -> tool -> result -> local TTS -> animation event`

Phone: `Android bridge -> authentication/privacy gate -> narrow capability API -> PC core`.

Storage: `PC core = executable/runtime/security/config`; `USB = knowledge/models/memory/backups/portable copy`.

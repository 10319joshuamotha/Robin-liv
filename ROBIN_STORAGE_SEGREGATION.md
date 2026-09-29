# Robin storage segregation

This document defines the intended separation between Robin's **system/core installation** and the detachable **external data/knowledge drive**.

## System/core (PC internal storage)

Keep on the PC's internal drive:

- Robin executable/runtime code
- Python environment and required application dependencies
- device-state and privacy enforcement
- authentication/authorization logic
- action/tool definitions and safety policy
- local wake-word and offline speech components
- offline text-to-speech components and voice assets required for basic operation
- core configuration (without plaintext secrets)
- encrypted credential-vault client and local vault metadata
- the active local index/database needed to boot and operate without the USB
- UI/animation runtime and lightweight character assets
- PC↔phone transport/client runtime
- crash recovery, health monitoring and update logic

The PC core must be able to start and provide basic assistant functionality when the USB is absent.

## Detachable USB (~117 GB available)

The USB is Robin's external data/knowledge layer. It should contain:

- long-term memory data
- user/profile knowledge that is safe to externalize
- relationship/context records
- large knowledge collections
- engineering reference material
- mechanical/electrical/CAD/civil/MEP/HVAC references
- periodic-table/reference datasets
- documents and user-provided knowledge
- conversation archives where enabled
- large media/character assets that are not required for boot
- model/reference files that are explicitly designated as external
- non-critical logs and historical telemetry
- backups/snapshots of the Robin data layer

## USB independence rule

If the USB is disconnected, Robin must **not** fail to start. It should enter an `external_memory_unavailable` condition and continue with the PC-resident core and whatever local memory is available.

The USB should be identified by a Robin-specific marker/manifest rather than a fixed Windows drive letter.

## Portable copy rule

The external data layer must have a portable/replicable form so that a user can copy the Robin data package to another supported installation. The portable package must contain a manifest describing:

- schema/version
- data categories
- compatibility version
- integrity hashes where applicable
- encrypted-vault references (never plaintext credentials)

A second copy of the **core installation package** should be buildable/exportable for installing Robin on another machine. The core package must not silently copy secrets or device-specific authentication material.

## Security boundaries

- Passwords, tokens, API keys and other secrets must be encrypted at rest.
- Plaintext passwords must never be written to ordinary knowledge files, prompts, logs or Git.
- Financial/GPay/payment capabilities are **completely forbidden by policy**. No voice confirmation, biometric confirmation, or multi-step verification can enable them.
- Gallery/photo access is denied by default and may be authorized only for one explicitly selected picture/tab/task.
- Screen access must obey Private Mode and the same capability boundary.
- Private Mode and PC Sleep are enforced by runtime state/capability code, not by model instructions alone.

## Installation segregation

When the repository is packaged for installation, generate a machine-readable segregation manifest alongside this document. The manifest must identify every large/static asset as either:

- `core` — required on the PC
- `external` — intended for the detachable USB
- `optional` — installable on demand
- `generated` — created at runtime

Do not move repository files into the USB solely because they are large; dependency/runtime requirements must be evaluated first.

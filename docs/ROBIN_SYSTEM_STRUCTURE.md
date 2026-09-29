# ROBIN — SYSTEM STRUCTURE

Target architecture for the personal AI assistant described in the project requirements.

## 1. High-level architecture

| Layer | Primary responsibility |
|---|---|
| Identity & Security | User authentication, voice identity, biometrics, authorization levels, sensitive-action gates |
| Core Brain | Reasoning/orchestration, intent understanding, planning, memory retrieval, task management |
| Memory | Preferences, relationships, routines, facts, device context, task history; sensitive secrets kept separately |
| Knowledge | General knowledge plus engineering, CAD, mechanical, electrical, civil, MEP/HVAC and chemistry references |
| Action Engine | File, browser, application, OS and device automation with confirmation/policy checks |
| Device Runtime | PC and phone state, Sleep, Private Mode, offline/online state, wake behavior |
| Voice | Wake word, speech recognition, speech synthesis, language selection, offline fallback |
| Character/UI | 2D Nico Robin-style avatar, idle behavior, task animations, speaking/listening/thinking states |
| Cross-device Layer | Authenticated PC↔phone sessions, task continuation, files, casting and device commands |
| Storage | PC core + detachable USB knowledge/portable package |

## 2. Core Brain

- Input normalization → intent detection → context retrieval → planning → policy check → action/tool execution → result verification → response.
- The brain should be platform-independent so the same personality, memory and task state can be used from the PC or phone.
- Internet services are an enhancement, not the only operating mode; offline fallback is a first-class requirement.
- The brain should never directly bypass the security/policy layer to execute a sensitive action.

## 3. Memory architecture

| Memory area | Examples | Location/handling |
|---|---|---|
| Profile | Name, language, communication preferences | PC core + encrypted sync |
| Preferences | Humor, response style, routines | Persistent memory |
| Relationships | Family/authorized people and relationship context | Persistent, access-controlled |
| Tasks | Open task, progress, device continuation | Shared task state |
| Device context | PC/phone state, current task/device | Runtime + persistent context where appropriate |
| Secrets | Passwords, tokens, credentials | Separate encrypted vault; never ordinary memory |

## 4. PC structure

- PC controller → Windows automation/action layer → applications/files/browser.
- Sleep state: normal Robin processing is stopped; the isolated ESC wake mechanism remains available.
- Wake flow: ESC → runtime wake → animation wake → wake-word/listening becomes available.
- “Robin, I am leaving” → detect intent → inspect active work → ask about unsaved work → close requested tabs/apps safely → keep phone-side Robin active.
- Performance manager should dynamically reduce animation/background workload so Robin does not unnecessarily consume system resources.

## 5. Phone structure

- Native Android client → biometric authentication → voice identity → phone runtime.
- Private Mode is a hard capability boundary for screen/camera-derived access.
- Gallery access is normally blocked; a specific user-authorized picture/tab creates a one-shot grant.
- Phone can continue tasks started on the PC and send/receive authorized files.
- Phone can request PC casting/remote operations through an authenticated cross-device session.

## 6. Security hierarchy

| Level | Purpose |
|---|---|
| Unauthenticated | No personal/sensitive operations |
| Authenticated | Normal assistant operation within permitted capabilities |
| Confirmed | Explicit confirmation for sensitive device/file/media operations |
| Multi-step verified | High-risk operations such as any future financial capability |
| Hard deny | GPay/payment boundary, protected media while unauthorized, Private Mode screen access, and PC Sleep processing |

## 7. Character / animation system

- Idle: subtle autonomous movement.
- Listening: attentive pose/animation.
- Thinking: thinking animation while reasoning.
- Speaking: lip-sync/viseme animation.
- Task: character visually performs an appropriate representation of the requested computer task.
- Success/error: corresponding reaction.
- Sleep: character sleeps when PC Robin sleeps.
- Animation Off: renderer becomes inactive while the assistant can continue operating.
- The animation layer must not be allowed to override security or device-state restrictions.

## 8. Knowledge system

- General assistant knowledge.
- Engineering reference layer: mechanical, electrical, civil, CAD, MEP/HVAC.
- Chemistry reference layer including all periodic-table elements and associated reference data.
- The knowledge package is designed to live primarily on the detachable USB storage so the PC core remains smaller and portable.
- Engineering outputs should be treated as assistance/reference and not as a substitute for professional verification where safety or regulated design is involved.

## 9. Storage / portability

### PC SYSTEM / CORE

- Runtime and executable code
- Core configuration
- Primary brain/orchestration
- Minimal required models/resources
- Encrypted local memory/vault components

### USB / DETACHABLE KNOWLEDGE

- Large knowledge/reference datasets
- Engineering reference package
- Chemistry/periodic-table package
- Portable copy of the required Robin package
- Manifest/integrity metadata

If the USB is absent, Robin should remain operational with reduced knowledge rather than failing completely.

## 10. Cross-device flow

1. Joshua starts a task on PC.
2. Robin records task state and authorization context.
3. Joshua says he will continue on phone.
4. Phone authenticates and resumes the task context.
5. Robin continues from the stored task state.
6. Results/files can be transferred through the authenticated channel.

## 11. Current implementation boundary

The repository currently contains foundations for several of these layers, but this document describes the target structure—not a claim that every layer is already fully implemented. The known release requirement remains: every capability must be wired to its real runtime path and integration-tested before Robin is declared complete.

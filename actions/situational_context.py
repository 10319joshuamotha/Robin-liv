"""On-demand God's Eye View-style situational-context tools for Robin.

GEV is user-controlled and OFF by default. These tools never capture a screen,
camera, GPS position, or identify a person. Protected states always override
GEV and clear visual/selection context.
"""
from __future__ import annotations

from core.spatial_context import spatial_context


def _get_context(parameters: dict, **_) -> str:
    return spatial_context.prompt_context()


def _set_gev(parameters: dict, **_) -> str:
    raw = parameters.get("enabled")
    if isinstance(raw, bool):
        enabled = raw
    else:
        enabled = str(raw).strip().lower() in {"on", "true", "yes", "enable", "enabled"}
    spatial_context.set_gev(enabled)
    return f"God's Eye View is now {'ON' if spatial_context.gev_enabled else 'OFF'}."


def _set_task(parameters: dict, **_) -> str:
    task = str(parameters.get("task", "")).strip()
    if not task:
        return "Please provide the task description."
    spatial_context.set_task(task)
    return f"Situational task context set to: {task}"


def _select_entity(parameters: dict, **_) -> str:
    entity_id = str(parameters.get("entity_id", "")).strip()
    kind = str(parameters.get("kind", "item")).strip() or "item"
    label = str(parameters.get("label", "")).strip()
    if not entity_id or not label:
        return "Entity selection requires entity_id and label."
    attributes = parameters.get("attributes") or {}
    if not isinstance(attributes, dict):
        attributes = {"value": str(attributes)}
    if spatial_context.select_entity(entity_id, kind, label, **attributes):
        return f"Selected local context item: {label} ({kind})."
    return "Selection was blocked because GEV is off, Private Mode is active, or the PC is sleeping."


def _clear_context(parameters: dict, **_) -> str:
    spatial_context.clear_selection()
    spatial_context.set_task("")
    return "Situational task and selection context cleared."


TOOL = {
    "name": "situational_context",
    "description": (
        "Control or read Robin's on-demand local situational context. GEV is "
        "OFF by default and should be enabled only when useful for the current "
        "task. It never captures screens or cameras itself and never bypasses "
        "Private Mode or PC Sleep."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "operation": {
                "type": "STRING",
                "description": "get_context, set_gev, set_task, select_entity, or clear"
            },
            "enabled": {"type": "BOOLEAN"},
            "task": {"type": "STRING"},
            "entity_id": {"type": "STRING"},
            "kind": {"type": "STRING"},
            "label": {"type": "STRING"},
            "attributes": {"type": "OBJECT"},
        },
        "required": ["operation"],
    },
    "handler": lambda parameters, **ctx: {
        "get_context": _get_context,
        "set_gev": _set_gev,
        "set_task": _set_task,
        "select_entity": _select_entity,
        "clear": _clear_context,
    }.get(str(parameters.get("operation", "")).strip().lower(),
          lambda p, **c: "Unknown situational_context operation.")(parameters, **ctx),
}

"""Correlate explicit visual observations with Robin's current task.

This is the bridge between GEV perception and action execution. It records
only local observation metadata (not image bytes) in SpatialContext.
"""
from __future__ import annotations

from pathlib import Path
from core.device_state import get_pc_controller
from core.spatial_context import spatial_context


def observation_context(parameters: dict, **ctx) -> str:
    controller = get_pc_controller()
    if not controller.allows("screen_capture"):
        return "Observation context blocked: PC screen capability is disabled."
    if bool(ctx.get("private_mode", False)):
        return "Observation context blocked: Private Mode is active."

    observation = str(parameters.get("observation", "")).strip()
    task = str(parameters.get("task", "")).strip()
    if not observation:
        return "Please provide the observation description."

    record = {
        "kind": "visual_observation",
        "description": observation,
        "source": "local",
    }
    path = str(parameters.get("path", "")).strip()
    if path:
        try:
            record["path"] = str(Path(path).expanduser().resolve())
        except Exception:
            record["path"] = path

    if task:
        spatial_context.set_task(task)
    spatial_context.set_layer("screen", [record], enabled=True)

    selected = parameters.get("selected_entity")
    if isinstance(selected, dict) and selected.get("id") and selected.get("label"):
        spatial_context.select_entity(
            str(selected["id"]),
            str(selected.get("kind", "ui_element")),
            str(selected["label"]),
            **(selected.get("attributes") or {}),
        )

    return spatial_context.prompt_context()


TOOL = {
    "name": "observation_context",
    "description": (
        "Correlate one explicitly permitted local visual observation with Robin's "
        "current task and optional selected UI element. This records metadata only; "
        "it never captures a screen and cannot bypass Private Mode or PC Sleep."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "observation": {"type": "STRING"},
            "task": {"type": "STRING"},
            "path": {"type": "STRING"},
            "selected_entity": {"type": "OBJECT"},
        },
        "required": ["observation"],
    },
    "capability": "screen",
    "behavior": "BLOCKING",
    "scheduling": "INTERRUPT",
    "handler": observation_context,
}

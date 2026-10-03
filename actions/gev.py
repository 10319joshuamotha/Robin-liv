"""Explicit user controls for Robin's on-demand God's Eye View context."""
from core.spatial_context import spatial_context


def _run(parameters: dict, **_) -> str:
    op = str(parameters.get("operation", "status")).strip().lower()
    if op == "on":
        return "God's Eye View is now ON." if spatial_context.set_gev(True) else "God's Eye View could not be enabled because screen access is currently unavailable or a protected mode is active."
    if op == "off":
        spatial_context.set_gev(False)
        return "God's Eye View is now OFF and visual context has been cleared."
    if op == "status":
        return spatial_context.prompt_context()
    if op == "task":
        task = str(parameters.get("task", "")).strip()
        if not spatial_context.gev_enabled:
            return "God's Eye View is OFF. Enable it before setting visual task context."
        spatial_context.set_task(task)
        return "GEV task context updated." if task else "GEV task context cleared."
    if op == "clear":
        spatial_context.clear_selection()
        spatial_context.set_task("")
        return "GEV task and selection context cleared."
    return "Unknown GEV operation."


TOOL = {
    "name": "gev_control",
    "description": "Explicitly turn Robin's God's Eye View situational context on or off, inspect status, set a task context, or clear context. GEV is off by default and never captures anything by itself.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "operation": {"type": "STRING", "description": "on, off, status, task, or clear"},
            "task": {"type": "STRING", "description": "Optional task description when operation is task"},
        },
        "required": ["operation"],
    },
    "handler": _run,
}

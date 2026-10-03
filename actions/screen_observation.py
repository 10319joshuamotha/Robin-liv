"""Explicit, policy-gated desktop observation for Robin's GEV layer.

This is intentionally separate from general mouse/keyboard control. The tool
only captures a local desktop observation when both the central policy context
and the shared PC capability controller permit screen access.
"""
from __future__ import annotations

from pathlib import Path
from time import strftime

from core.device_state import get_pc_controller
from core.spatial_context import spatial_context

try:
    import pyautogui
except ImportError:  # pragma: no cover - dependency is optional
    pyautogui = None


def observe_screen(parameters: dict, **ctx) -> str:
    controller = get_pc_controller()
    if not controller.allows("screen_capture"):
        return "Screen observation blocked: Robin's PC screen capability is disabled."
    if bool(ctx.get("private_mode", False)):
        return "Screen observation blocked: Private Mode is active."
    if pyautogui is None:
        return "Screen observation unavailable: PyAutoGUI is not installed."

    requested = str(parameters.get("path", "")).strip()
    if requested:
        path = Path(requested).expanduser().resolve()
        if not path.is_relative_to(Path.home().resolve()):
            return "Screen observation blocked: output path must be inside the user profile."
    else:
        path = Path.home() / "Desktop" / f"robin_observation_{strftime('%Y%m%d_%H%M%S')}.png"

    path.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot(str(path))

    # Store only an observation reference. The context layer remains disabled
    # automatically when Private Mode or PC Sleep is enabled.
    spatial_context.set_layer(
        "screen",
        [{"kind": "desktop_observation", "path": str(path), "source": "local"}],
        enabled=True,
    )
    return f"Desktop observation captured locally: {path}"


TOOL = {
    "name": "screen_observation",
    "description": (
        "Capture one explicit local desktop observation for Robin's situational "
        "context. Never use continuously. Blocked during Private Mode or PC Sleep."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "Optional output path; must be inside the current user profile."
            }
        },
        "required": [],
    },
    "capability": "screen",
    "behavior": "BLOCKING",
    "scheduling": "INTERRUPT",
    "handler": observe_screen,
}

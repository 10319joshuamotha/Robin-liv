"""AutoCAD guidance layer.

This does not pretend that a generic mouse click is an AutoCAD API. It gives
Robin a structured map of common commands and can open AutoCAD; actual drawing
changes should use AutoLISP/AutoCAD APIs or the existing computer-control layer
with confirmation where appropriate.
"""
from __future__ import annotations
import os
import shutil
import subprocess

COMMANDS = {
    "line":"LINE", "polyline":"PLINE", "rectangle":"RECTANG", "circle":"CIRCLE",
    "arc":"ARC", "move":"MOVE", "copy":"COPY", "rotate":"ROTATE",
    "mirror":"MIRROR", "scale":"SCALE", "offset":"OFFSET", "trim":"TRIM",
    "extend":"EXTEND", "fillet":"FILLET", "chamfer":"CHAMFER", "array":"ARRAY",
    "hatch":"HATCH", "dimension":"DIM", "layer":"LAYER", "block":"BLOCK",
    "explode":"EXPLODE", "join":"JOIN", "measure":"MEASUREGEOM",
    "properties":"PROPERTIES", "purge":"PURGE", "audit":"AUDIT",
    "units":"UNITS", "zoom":"ZOOM", "pan":"PAN"
}

def autocad_help(parameters: dict, **_) -> str:
    task = str(parameters.get("task","")).strip().lower()
    for key, cmd in COMMANDS.items():
        if key in task:
            return f"Recommended AutoCAD command: {cmd}. Explain the required selections and options before executing it."
    return ("I can map common AutoCAD tasks to commands such as LINE, PLINE, OFFSET, "
            "TRIM, EXTEND, FILLET, CHAMFER, ARRAY, HATCH, DIM, LAYER and BLOCK. "
            "For a specific task, describe what you want to create or edit.")

def open_autocad(parameters: dict, **_) -> str:
    candidates = [
        os.environ.get("AUTOCAD_EXE",""),
        r"C:\Program Files\Autodesk\AutoCAD 2026\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2025\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2024\acad.exe"
    ]
    exe = next((x for x in candidates if x and os.path.exists(x)), None)
    if not exe:
        exe = shutil.which("acad.exe")
    if not exe:
        return "AutoCAD was not found. If it is installed elsewhere, set AUTOCAD_EXE to its acad.exe path."
    subprocess.Popen([exe])
    return "AutoCAD opened."

TOOL_HELP = {
    "name": "autocad_help",
    "description": "Identify the appropriate AutoCAD command/tool for a requested drawing task.",
    "parameters": {"type":"OBJECT","properties":{"task":{"type":"STRING","description":"What the user wants to do in AutoCAD."}},"required":["task"]},
    "handler": autocad_help
}

TOOL = TOOL_HELP

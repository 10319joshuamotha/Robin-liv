"""
Action discovery, validation, and policy-aware dispatch.

Every actions/*.py module exposing TOOL is discovered here.  The registry is also
Robin's common enforcement boundary: sensitive actions are checked against the
central RobinPolicy before a handler is invoked.
"""
from __future__ import annotations

import importlib.util
import inspect
import re
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from core.robin_policy import Capability, RobinPolicy

_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")
_DEFAULT_PARAMS = {"type": "OBJECT", "properties": {}}
_CTX_KEYS = ("player", "speak", "response", "session_memory")
_BEHAVIORS = ("BLOCKING", "NON_BLOCKING")
_SCHEDULING = ("WHEN_IDLE", "SILENT", "INTERRUPT")

# Action names are deliberately conservative.  Unknown actions remain subject to
# the existing application behavior; only actions that clearly cross one of
# Robin's protected boundaries are mapped here.
_FINANCE_WORDS = ("payment", "payments", "gpay", "bank", "banking", "upi", "wallet", "transfer_money", "send_money", "pay")
_GALLERY_WORDS = ("gallery", "photo", "photos", "picture", "pictures", "camera_roll", "google_photos")
_SCREEN_WORDS = ("screen", "screenshot", "screen_capture", "screen_record", "screen_process")
_PC_CONTROL_WORDS = ("shutdown", "restart", "sleep_pc", "poweroff", "system_control")
_PHONE_CONTROL_WORDS = ("phone_control", "send_document", "cast_screen", "remote_phone")


def _capability_for_action(name: str) -> Capability | None:
    n = name.lower()
    if any(x in n for x in _FINANCE_WORDS):
        return Capability.FINANCE
    if any(x in n for x in _GALLERY_WORDS):
        return Capability.GALLERY
    if any(x in n for x in _SCREEN_WORDS):
        return Capability.SCREEN
    if any(x in n for x in _PC_CONTROL_WORDS):
        return Capability.PC_CONTROL
    if any(x in n for x in _PHONE_CONTROL_WORDS):
        return Capability.PHONE_CONTROL
    return None


def _policy_decision(policy: RobinPolicy, name: str, ctx: dict) -> tuple[bool, str]:
    capability = _capability_for_action(name)
    if capability is None:
        return True, ""
    decision = policy.decide(
        capability,
        authenticated=bool(ctx.get("authenticated", False)),
        confirmed=bool(ctx.get("confirmed", False)),
        multi_step_verified=bool(ctx.get("multi_step_verified", False)),
        private_mode=bool(ctx.get("private_mode", False)),
        explicit_media_grant=bool(ctx.get("explicit_media_grant", False)),
    )
    return decision.allowed, decision.reason


def _opt_upper(value, allowed: tuple[str, ...]) -> Optional[str]:
    v = str(value or "").strip().upper()
    return v if v in allowed else None


@dataclass
class ActionRecord:
    name: str
    description: str = ""
    parameters: dict = field(default_factory=lambda: dict(_DEFAULT_PARAMS))
    handler: Optional[Callable] = None
    file: str = ""
    valid: bool = False
    error: str = ""
    behavior: Optional[str] = None
    scheduling: Optional[str] = None


class ActionRegistry:
    def __init__(self, actions: dict[str, ActionRecord], logger: Callable[[str], None], policy: RobinPolicy | None = None):
        self._actions = actions
        self._all_records: list[ActionRecord] = []
        self._logger = logger
        self._policy = policy or RobinPolicy()

    def get_tool_declarations(self) -> list[dict]:
        out = []
        for rec in self._actions.values():
            decl = {"name": rec.name, "description": rec.description, "parameters": rec.parameters}
            if rec.behavior:
                decl["behavior"] = rec.behavior
            out.append(decl)
        return out

    def has(self, name: str) -> bool:
        return name in self._actions

    def scheduling(self, name: str) -> Optional[str]:
        rec = self._actions.get(name)
        return rec.scheduling if rec else None

    def names(self) -> set[str]:
        return set(self._actions.keys())

    def run(self, name: str, parameters: dict, ctx: dict | None = None) -> str:
        rec = self._actions.get(name)
        if rec is None or not rec.valid:
            return f"Action '{name}' is not available."
        context = ctx or {}
        allowed, reason = _policy_decision(self._policy, name, context)
        if not allowed:
            self._logger(f"POLICY BLOCK: {name} — {reason}")
            return f"Action '{name}' blocked by Robin security policy: {reason}"
        try:
            return _call_handler(rec.handler, parameters, context) or "Done."
        except Exception as e:
            self._logger(f"Action '{name}' crashed during run(): {e}")
            traceback.print_exc()
            return f"Tool '{name}' failed: {e}"


def _call_handler(fn: Callable, parameters: dict, ctx: dict) -> str:
    sig = inspect.signature(fn)
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    kwargs = {}
    for key in _CTX_KEYS:
        if has_var_kw or key in sig.parameters:
            kwargs[key] = ctx.get(key)
    return fn(parameters=parameters, **kwargs)


def _validate(module, filename: str) -> ActionRecord:
    tool = getattr(module, "TOOL", None)
    if not isinstance(tool, dict):
        return ActionRecord(name=Path(filename).stem, file=filename, error="No module-level TOOL dict (not a discoverable action).")
    name = tool.get("name")
    if not isinstance(name, str) or not _NAME_RE.match(name):
        return ActionRecord(name=str(name or Path(filename).stem), file=filename, error="TOOL['name'] missing or not a valid identifier.")
    description = tool.get("description")
    if not isinstance(description, str) or not description.strip():
        return ActionRecord(name=name, file=filename, error="TOOL['description'] missing or empty.")
    parameters = tool.get("parameters", _DEFAULT_PARAMS)
    if not isinstance(parameters, dict) or parameters.get("type") != "OBJECT":
        return ActionRecord(name=name, file=filename, error='TOOL[\'parameters\'] must be a dict with "type": "OBJECT".')
    handler = tool.get("handler")
    if not callable(handler):
        return ActionRecord(name=name, file=filename, error="TOOL['handler'] missing or not callable.")
    return ActionRecord(
        name=name, description=description.strip(), parameters=parameters,
        handler=handler, file=filename, valid=True, error="",
        behavior=_opt_upper(tool.get("behavior"), _BEHAVIORS),
        scheduling=_opt_upper(tool.get("scheduling"), _SCHEDULING),
    )


def discover_actions(actions_dir: Path, reserved_names: set[str] | None = None, logger: Callable[[str], None] = print) -> ActionRegistry:
    reserved = reserved_names or set()
    actions_dir.mkdir(parents=True, exist_ok=True)
    valid: dict[str, ActionRecord] = {}
    all_records: list[ActionRecord] = []
    for path in sorted(actions_dir.glob("*.py"), key=lambda p: p.name):
        if path.name.startswith("_"):
            continue
        try:
            module_name = f"actions.{path.stem}"
            module = sys.modules.get(module_name)
            if module is None:
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError("could not build import spec")
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                try:
                    spec.loader.exec_module(module)
                except Exception:
                    sys.modules.pop(module_name, None)
                    raise
            if getattr(module, "TOOL", None) is None:
                continue
            rec = _validate(module, path.name)
            if rec.valid and rec.name in reserved:
                rec = ActionRecord(name=rec.name, file=path.name, error=f"Name '{rec.name}' collides with a reserved core tool — rejected.")
            elif rec.valid and rec.name in valid:
                other = valid[rec.name].file
                rec = ActionRecord(name=rec.name, file=path.name, error=f"Name '{rec.name}' already used by action '{other}' — rejected.")
        except Exception as e:
            rec = ActionRecord(name=path.stem, file=path.name, error=f"Failed to load: {e}")
            traceback.print_exc()
        all_records.append(rec)
        if rec.valid:
            valid[rec.name] = rec
            logger(f"Action loaded: {rec.name} ({path.name})")
        else:
            logger(f"Action rejected: {path.name} — {rec.error}")
    registry = ActionRegistry(valid, logger)
    registry._all_records = all_records
    logger(f"Action discovery complete: {len(valid)} active.")
    return registry

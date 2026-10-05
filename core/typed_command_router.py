"""Deterministic routing for explicitly typed Robin commands.

Natural-language conversation remains handled by the configured brain. Commands
using the explicit `run`/`/action` syntax are parsed locally, validated against
the action registry, and executed through the registry's policy boundary.
"""
from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TypedCommand:
    action: str
    parameters: dict[str, Any]


def parse_typed_command(text: str) -> TypedCommand | None:
    """Parse an explicit command; return None for ordinary conversation.

    Supported forms:
      run action
      run action {"key": "value"}
      /action
      /action key=value other="hello world"
    """
    raw = (text or "").strip()
    if not raw:
        return None

    if raw.startswith("/"):
        tokens = shlex.split(raw[1:])
        if not tokens:
            return None
        action = tokens.pop(0).strip()
        if not action:
            return None
        return TypedCommand(action=action, parameters=_parse_params(tokens))

    tokens = shlex.split(raw)
    if len(tokens) < 2 or tokens[0].lower() != "run":
        return None

    action = tokens[1].strip()
    if not action:
        return None

    remainder = raw.split(None, 2)
    if len(remainder) == 2:
        params: dict[str, Any] = {}
    else:
        payload = remainder[2].strip()
        if payload.startswith("{"):
            try:
                params = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON parameters: {exc.msg}") from exc
            if not isinstance(params, dict):
                raise ValueError("Command parameters must be a JSON object")
        else:
            params = _parse_params(shlex.split(payload))
    return TypedCommand(action=action, parameters=params)


def _parse_params(tokens: list[str]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"Expected key=value parameter, got '{token}'")
        key, value = token.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("Parameter name cannot be empty")
        params[key] = _coerce(value)
    return params


def _coerce(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def execute_typed_command(text: str, registry, ctx: dict | None = None) -> str | None:
    """Execute an explicit typed command through ActionRegistry.

    Returns None when the input is ordinary conversation. All actual action
    execution is delegated to registry.run(), preserving its security policy.
    """
    command = parse_typed_command(text)
    if command is None:
        return None
    if not registry.has(command.action):
        return f"Action '{command.action}' is not available."
    return registry.run(command.action, command.parameters, ctx or {})

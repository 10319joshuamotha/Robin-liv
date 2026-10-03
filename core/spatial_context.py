"""God's Eye View-inspired local situational context for Robin.

This adapts the useful architecture of God's Eye View—layered context,
scene summaries, selected-entity context, and honest tool-facing state—without
importing its globe/OSINT surveillance stack. Robin's context is local-device
first and respects Private Mode and PC Sleep.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Any


@dataclass
class ContextLayer:
    name: str
    enabled: bool = True
    records: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class SelectedEntity:
    entity_id: str
    kind: str
    label: str
    attributes: dict[str, Any]


class SpatialContext:
    """Small, deterministic context store suitable for feeding Robin tools/LLM."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._private = False
        self._sleeping = False
        self._task = ""
        self._selected: SelectedEntity | None = None
        self._layers: dict[str, ContextLayer] = {
            "system": ContextLayer("system"),
            "task": ContextLayer("task"),
            "screen": ContextLayer("screen"),
            "knowledge": ContextLayer("knowledge"),
            "selection": ContextLayer("selection"),
        }
        self._updated = time.time()

    def set_privacy(self, *, private_mode: bool, sleeping: bool = False) -> None:
        with self._lock:
            self._private = bool(private_mode)
            self._sleeping = bool(sleeping)
            # GEV-style visual context is unavailable in either protected state.
            self._layers["screen"].enabled = not self._private and not self._sleeping
            self._layers["selection"].enabled = not self._private and not self._sleeping
            if self._private or self._sleeping:
                self._layers["screen"].records.clear()
                self._layers["selection"].records.clear()
                self._selected = None
            self._updated = time.time()

    def set_task(self, task: str) -> None:
        with self._lock:
            self._task = task.strip()
            self._layers["task"].records = ([{"task": self._task}] if self._task else [])
            self._updated = time.time()

    def set_layer(self, name: str, records: list[dict[str, Any]], *, enabled: bool = True) -> None:
        if name not in self._layers:
            raise ValueError(f"Unknown context layer: {name}")
        with self._lock:
            if name in {"screen", "selection"} and (self._private or self._sleeping):
                self._layers[name].enabled = False
                self._layers[name].records.clear()
            else:
                self._layers[name].enabled = bool(enabled)
                self._layers[name].records = [dict(r) for r in records]
            self._updated = time.time()

    def select_entity(self, entity_id: str, kind: str, label: str, **attributes: Any) -> bool:
        with self._lock:
            if self._private or self._sleeping:
                return False
            self._selected = SelectedEntity(entity_id, kind, label, dict(attributes))
            self._layers["selection"].records = [asdict(self._selected)]
            self._updated = time.time()
            return True

    def clear_selection(self) -> None:
        with self._lock:
            self._selected = None
            self._layers["selection"].records.clear()
            self._updated = time.time()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            layers = {
                name: {
                    "enabled": layer.enabled,
                    "records": [dict(r) for r in layer.records],
                }
                for name, layer in self._layers.items()
                if layer.enabled and not (self._private and name in {"screen", "selection"})
            }
            return {
                "timestamp": self._updated,
                "private_mode": self._private,
                "sleeping": self._sleeping,
                "task": self._task,
                "selected_entity": asdict(self._selected) if self._selected else None,
                "layers": layers,
            }

    def prompt_context(self) -> str:
        """Compact, non-authoritative context for the model.

        This is deliberately phrased as observations, not facts, so the model
        cannot treat stale/unknown context as ground truth.
        """
        s = self.snapshot()
        lines = ["Robin situational context (observations only):"]
        lines.append(f"Private mode: {'ON' if s['private_mode'] else 'OFF'}")
        lines.append(f"PC sleeping: {'YES' if s['sleeping'] else 'NO'}")
        if s["task"]:
            lines.append(f"Current task: {s['task']}")
        if s["selected_entity"]:
            e = s["selected_entity"]
            lines.append(f"Selected item: {e['label']} ({e['kind']})")
        for name, layer in s["layers"].items():
            if name in {"task", "selection"} or not layer["records"]:
                continue
            lines.append(f"{name}: {len(layer['records'])} observation(s)")
        return "\n".join(lines)


spatial_context = SpatialContext()

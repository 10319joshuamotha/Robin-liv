"""On-demand God's Eye View-inspired local situational context for Robin."""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Any

from core.device_state import get_pc_controller


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
    """Task-scoped situational context. GEV is opt-in and deny-by-default."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._private = False
        self._sleeping = False
        self._gev_enabled = False
        self._task = ""
        self._selected: SelectedEntity | None = None
        self._layers: dict[str, ContextLayer] = {
            "system": ContextLayer("system"),
            "task": ContextLayer("task"),
            "screen": ContextLayer("screen", enabled=False),
            "knowledge": ContextLayer("knowledge"),
            "selection": ContextLayer("selection", enabled=False),
        }
        self._updated = time.time()

    @property
    def gev_enabled(self) -> bool:
        with self._lock:
            return self._gev_enabled

    def _screen_allowed(self) -> bool:
        return get_pc_controller().allows("screen_capture")

    def _clear_visual(self) -> None:
        self._layers["screen"].enabled = False
        self._layers["selection"].enabled = False
        self._layers["screen"].records.clear()
        self._layers["selection"].records.clear()
        self._selected = None

    def set_gev(self, enabled: bool) -> bool:
        with self._lock:
            requested = bool(enabled)
            self._gev_enabled = requested and not self._private and not self._sleeping and self._screen_allowed()
            if not self._gev_enabled:
                self._clear_visual()
            else:
                self._layers["screen"].enabled = True
                self._layers["selection"].enabled = True
            self._updated = time.time()
            return self._gev_enabled

    def set_privacy(self, *, private_mode: bool, sleeping: bool = False) -> None:
        with self._lock:
            self._private = bool(private_mode)
            self._sleeping = bool(sleeping)
            if self._private or self._sleeping or not self._screen_allowed():
                self._gev_enabled = False
                self._clear_visual()
            elif self._gev_enabled:
                self._layers["screen"].enabled = True
                self._layers["selection"].enabled = True
            self._updated = time.time()

    def refresh_device_gate(self) -> bool:
        """Re-evaluate the PC capability gate before visual context is consumed."""
        with self._lock:
            if self._gev_enabled and (self._private or self._sleeping or not self._screen_allowed()):
                self._gev_enabled = False
                self._clear_visual()
            return self._gev_enabled

    def set_task(self, task: str) -> None:
        with self._lock:
            self._task = task.strip()
            self._layers["task"].records = ([{"task": self._task}] if self._task else [])
            self._updated = time.time()

    def set_layer(self, name: str, records: list[dict[str, Any]], *, enabled: bool = True) -> None:
        if name not in self._layers:
            raise ValueError(f"Unknown context layer: {name}")
        with self._lock:
            if name in {"screen", "selection"}:
                self.refresh_device_gate()
                if not self._gev_enabled:
                    self._layers[name].enabled = False
                    self._layers[name].records.clear()
                    return
            self._layers[name].enabled = bool(enabled)
            self._layers[name].records = [dict(r) for r in records]
            self._updated = time.time()

    def select_entity(self, entity_id: str, kind: str, label: str, **attributes: Any) -> bool:
        with self._lock:
            self.refresh_device_gate()
            if not self._gev_enabled:
                return False
            self._selected = SelectedEntity(entity_id, kind, label, dict(attributes))
            self._layers["selection"].enabled = True
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
            self.refresh_device_gate()
            layers = {
                name: {"enabled": layer.enabled, "records": [dict(r) for r in layer.records]}
                for name, layer in self._layers.items()
                if layer.enabled
            }
            return {
                "timestamp": self._updated,
                "gev_enabled": self._gev_enabled,
                "private_mode": self._private,
                "sleeping": self._sleeping,
                "task": self._task,
                "selected_entity": asdict(self._selected) if self._selected else None,
                "layers": layers,
            }

    def prompt_context(self) -> str:
        s = self.snapshot()
        lines = ["Robin situational context (observations only):"]
        lines.append(f"GEV: {'ON' if s['gev_enabled'] else 'OFF'}")
        lines.append(f"Private mode: {'ON' if s['private_mode'] else 'OFF'}")
        lines.append(f"PC sleeping: {'YES' if s['sleeping'] else 'NO'}")
        if s["task"]:
            lines.append(f"Current task: {s['task']}")
        if s["selected_entity"]:
            e = s["selected_entity"]
            lines.append(f"Selected item: {e['label']} ({e['kind']})")
        return "\n".join(lines)


spatial_context = SpatialContext()

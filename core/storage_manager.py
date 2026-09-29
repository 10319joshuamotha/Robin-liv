"""Portable core/external storage discovery for Robin.

The removable drive is identified by a marker file, never by a Windows drive
letter. The core remains usable when the external data drive is absent.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MARKER = ".robin-external.json"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class StorageRoots:
    core: Path
    external: Path | None

    @property
    def external_available(self) -> bool:
        return self.external is not None and self.external.exists()


def _is_marker(path: Path) -> bool:
    try:
        data = json.loads((path / MARKER).read_text(encoding="utf-8"))
        return data.get("application") == "robin" and int(data.get("schema", 0)) == SCHEMA_VERSION
    except Exception:
        return False


def create_external_marker(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    marker = root / MARKER
    if not marker.exists():
        marker.write_text(json.dumps({
            "application": "robin",
            "schema": SCHEMA_VERSION,
            "role": "external-memory",
        }, indent=2), encoding="utf-8")
    return marker


def find_external_roots(search_roots: Iterable[Path]) -> list[Path]:
    """Find candidate Robin external drives without assuming a drive letter."""
    found: list[Path] = []
    for root in search_roots:
        try:
            if root.exists() and _is_marker(root):
                found.append(root)
        except Exception:
            continue
    return found


def discover(core_root: Path, candidates: Iterable[Path] | None = None) -> StorageRoots:
    """Return core + first valid external root; absence is non-fatal."""
    roots = list(candidates or ())
    # On Windows, enumerate existing drive roots when no explicit candidates are supplied.
    if not roots and os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            p = Path(f"{letter}:\\")
            if p.exists():
                roots.append(p)
    matches = find_external_roots(roots)
    return StorageRoots(core=core_root, external=matches[0] if matches else None)

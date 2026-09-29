"""Robin's local-brain and external-knowledge storage layout.

The actual external-drive location is supplied at runtime. Do not hard-code a
Windows drive letter: removable media letters can change between boots.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


EXTERNAL_ROOT_ENV = "ROBIN_EXTERNAL_ROOT"
EXTERNAL_MARKER = ".robin-external"


@dataclass(frozen=True)
class RobinStorage:
    """Resolved paths for Robin's two-tier storage model."""

    brain_root: Path
    external_root: Path | None

    @property
    def local_memory(self) -> Path:
        return self.brain_root / "memory"

    @property
    def external_knowledge(self) -> Path | None:
        return self.external_root / "knowledge" if self.external_root else None

    @property
    def external_memory(self) -> Path | None:
        return self.external_root / "memory" if self.external_root else None

    @property
    def external_documents(self) -> Path | None:
        return self.external_root / "documents" if self.external_root else None

    @property
    def external_media(self) -> Path | None:
        return self.external_root / "media" if self.external_root else None

    @property
    def external_logs(self) -> Path | None:
        return self.external_root / "logs" if self.external_root else None

    @property
    def available(self) -> bool:
        return self.external_root is not None and self.external_root.exists()


def resolve_external_root(brain_root: Path) -> Path | None:
    """Resolve the external Robin data root without assuming a drive letter.

    The environment variable is the first source of truth. The fallback looks
    only for a deliberately named `.robin-external` marker near the configured
    runtime; it does not scan arbitrary removable drives.
    """

    configured = os.environ.get(EXTERNAL_ROOT_ENV, "").strip()
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()
        return None

    marker = brain_root / EXTERNAL_MARKER
    if marker.is_dir():
        return marker.resolve()

    return None


def resolve_storage(brain_root: Path) -> RobinStorage:
    """Build the current storage view. Missing external storage is valid."""

    root = brain_root.resolve()
    return RobinStorage(brain_root=root, external_root=resolve_external_root(root))


def initialize_external_layout(external_root: Path) -> RobinStorage:
    """Create only Robin's top-level external directories.

    This is intentionally not called automatically at startup. Formatting or
    populating a removable drive is an explicit user/setup operation.
    """

    external_root = external_root.expanduser().resolve()
    external_root.mkdir(parents=True, exist_ok=True)
    (external_root / EXTERNAL_MARKER).touch(exist_ok=True)
    for name in ("knowledge", "memory", "documents", "datasets", "media", "logs"):
        (external_root / name).mkdir(exist_ok=True)
    return RobinStorage(brain_root=Path.cwd().resolve(), external_root=external_root)

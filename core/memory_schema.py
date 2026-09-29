"""Structured schema for Robin's persistent user memory.

This is deliberately a data model, not a storage backend. Secrets belong in a
separate encrypted credential vault and must never be written as ordinary
memory records.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    ROUTINE = "routine"
    TASK = "task"
    DEVICE_CONTEXT = "device_context"


@dataclass
class MemoryRecord:
    kind: MemoryKind
    subject: str
    value: Any
    owner_id: str = "joshua"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "conversation"
    sensitivity: str = "normal"
    deleted: bool = False

    def mark_deleted(self) -> None:
        self.deleted = True
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class UserProfile:
    user_id: str
    display_name: str
    language: str = "en"
    memories: list[MemoryRecord] = field(default_factory=list)

    def add_memory(self, record: MemoryRecord) -> None:
        if record.owner_id != self.user_id:
            raise ValueError("Memory owner does not match profile")
        self.memories.append(record)

    def active_memories(self) -> list[MemoryRecord]:
        return [m for m in self.memories if not m.deleted]

    def forget(self, record_id: str) -> bool:
        for memory in self.memories:
            if memory.id == record_id and not memory.deleted:
                memory.mark_deleted()
                return True
        return False

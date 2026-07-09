"""Mason mission memory storage.

This module gives Mason a durable JSON-backed memory store for mission-critical
notes that Atlas or Mason need to recall later.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MEMORY_PATH = Path(r"C:\Users\User\Desktop\PUTER\mason_workspace\mason_memory.json")


def _load_memories() -> list[dict[str, Any]]:
    """Load Mason memory entries from disk."""
    if not MEMORY_PATH.exists():
        return []

    with MEMORY_PATH.open("r", encoding="utf-8") as memory_file:
        data = json.load(memory_file)

    if not isinstance(data, list):
        raise ValueError(f"Mason memory file must contain a JSON list: {MEMORY_PATH}")

    return data


def _save_memories(memories: list[dict[str, Any]]) -> None:
    """Persist Mason memory entries to disk."""
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("w", encoding="utf-8") as memory_file:
        json.dump(memories, memory_file, indent=4, ensure_ascii=False)
        memory_file.write("\n")


def mason_remember(entry: Any) -> dict[str, Any]:
    """Save a Mason mission memory entry with a UTC timestamp.

    Args:
        entry: The memory payload to store. Strings are expected for normal
            mission notes, but any JSON-serializable value is supported.

    Returns:
        The timestamped memory record that was saved.
    """
    memory_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": entry,
    }

    memories = _load_memories()
    memories.append(memory_entry)
    _save_memories(memories)
    return memory_entry


def mason_recall(limit: int = 10) -> list[dict[str, Any]]:
    """Recall Mason's most recent mission memories.

    Args:
        limit: Maximum number of entries to return. Defaults to 10.

    Returns:
        The latest memory entries, preserving chronological order.
    """
    if limit is None:
        limit = 10

    limit = int(limit)
    if limit <= 0:
        return []

    memories = _load_memories()
    return memories[-limit:]


__all__ = ["mason_remember", "mason_recall", "MEMORY_PATH"]


if __name__ == "__main__":
    print(json.dumps(mason_recall(), indent=4, ensure_ascii=False))

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import portalocker

AUDIT_LOG_PATH = Path(__file__).parent.parent / "audit_log.jsonl"

_LOCK_TIMEOUT = 5.0  # seconds to wait for exclusive lock before giving up

logger = logging.getLogger(__name__)


def write_audit_entry(
    user: str,
    role: str,
    action: str,
    policy_decision: str,
    workflow_id: str = "",
    agent_output: str = "",
    execution_status: str = "",
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "role": role,
        "action": action,
        "policy_decision": policy_decision,
        "workflow_id": workflow_id,
        "agent_output": agent_output,
        "execution_status": execution_status,
    }
    line = json.dumps(entry) + "\n"
    try:
        # portalocker.Lock acquires an exclusive OS-level lock before writing,
        # preventing interleaved bytes from concurrent requests.
        with portalocker.Lock(
            AUDIT_LOG_PATH,
            mode="a",
            timeout=_LOCK_TIMEOUT,
            encoding="utf-8",
        ) as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())  # ensure bytes reach disk before releasing lock
    except portalocker.LockException:
        logger.error(
            "audit: failed to acquire file lock within %.1fs — entry: %s",
            _LOCK_TIMEOUT,
            line.strip(),
        )
        raise


def read_audit_entries() -> list[dict]:
    """Return all valid audit entries. Used internally and by tests."""
    if not AUDIT_LOG_PATH.exists():
        return []
    entries = []
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except (json.JSONDecodeError, ValueError):
                logger.warning(
                    "audit: skipping malformed entry at line %d: %r", i, line
                )
    return entries


def read_audit_entries_paginated(limit: int = 50, offset: int = 0) -> dict:
    """Return a paginated slice of audit entries with metadata."""
    all_entries = read_audit_entries()
    total = len(all_entries)
    items = all_entries[offset : offset + limit]
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }

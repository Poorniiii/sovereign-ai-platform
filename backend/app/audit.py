import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_PATH = Path(__file__).parent.parent / "audit_log.jsonl"


def write_audit_entry(
    user: str,
    role: str,
    action: str,
    policy_decision: str,
    workflow_id: str = "",
    agent_output: str = "",
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "role": role,
        "action": action,
        "policy_decision": policy_decision,
        "workflow_id": workflow_id,
        "agent_output": agent_output,
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_audit_entries() -> list[dict]:
    if not AUDIT_LOG_PATH.exists():
        return []
    entries = []
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

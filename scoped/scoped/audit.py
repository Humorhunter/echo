from __future__ import annotations

import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS = "0" * 64
SECRET_MARKERS = (
    "secret",
    "token",
    "password",
    "passwd",
    "pwd",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "session_key",
    "refresh_token",
    "credentials",
    "bearer",
    "authorization",
    "cookie",
)
MAX_PREVIEW = 400


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in SECRET_MARKERS):
                result[key] = "***"
            else:
                result[key] = redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str) and len(value) > MAX_PREVIEW:
        return value[:MAX_PREVIEW] + f"... <truncated {len(value) - MAX_PREVIEW} chars>"
    return value


def hash_entry(entry: dict[str, Any]) -> str:
    body = {key: value for key, value in entry.items() if key != "hash"}
    return sha256(canonical(body))


class AuditLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        entries = []
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {number}: {exc}") from exc
        return entries

    def last(self) -> dict[str, Any] | None:
        entries = self._entries()
        return entries[-1] if entries else None

    def append(
        self,
        *,
        agent: str,
        tool: str,
        args: dict[str, Any],
        decision: str,
        policy_decision: str,
        rule: str,
        reason: str,
        approval: str | None = None,
    ) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.seek(0)
            entries = []
            for line in handle:
                if line.strip():
                    entries.append(json.loads(line))
            previous = entries[-1]["hash"] if entries else GENESIS
            entry = {
                "seq": len(entries) + 1,
                "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "agent": agent,
                "tool": tool,
                "args_hash": sha256(canonical(args)),
                "args_preview": redact(args),
                "decision": decision,
                "policy_decision": policy_decision,
                "rule": rule,
                "reason": reason,
                "approval": approval,
                "prev": previous,
            }
            entry["hash"] = hash_entry(entry)
            handle.seek(0, os.SEEK_END)
            if handle.tell() > 0:
                handle.write("\n")
            handle.write(canonical(entry))
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            return entry

    def verify(self) -> list[str]:
        entries = self._entries()
        errors: list[str] = []
        previous = GENESIS
        for index, entry in enumerate(entries, 1):
            if entry.get("seq") != index:
                errors.append(f"line {index}: seq is {entry.get('seq')!r}, expected {index}")
            if entry.get("prev") != previous:
                errors.append(f"line {index}: prev hash does not match previous entry")
            expected = hash_entry(entry)
            if entry.get("hash") != expected:
                errors.append(f"line {index}: hash mismatch")
            previous = entry.get("hash", "")
        return errors

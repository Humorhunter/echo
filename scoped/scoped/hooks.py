from __future__ import annotations

from typing import Any

from .audit import AuditLog
from .policy import Policy

TOOL_MAP = {
    "Bash": "shell",
    "Read": "read_file",
    "Write": "write_file",
    "Edit": "write_file",
    "MultiEdit": "write_file",
    "NotebookEdit": "write_file",
    "WebFetch": "http",
    "WebSearch": "http",
    "Glob": "glob",
    "Grep": "grep",
}


def map_claude_call(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    name = str(payload.get("tool_name", ""))
    raw = payload.get("tool_input") or {}
    if not isinstance(raw, dict):
        raw = {"value": raw}
    if name.startswith("mcp__"):
        parts = name.split("__", 2)
        if len(parts) == 3:
            return f"{parts[1]}.{parts[2]}", dict(raw)
    tool = TOOL_MAP.get(name, name)
    if name == "Bash":
        return tool, {"command": str(raw.get("command", ""))}
    if name in {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}:
        path = raw.get("file_path") or raw.get("notebook_path") or raw.get("path") or ""
        return tool, {"path": str(path)}
    if name in {"WebFetch", "WebSearch"}:
        return tool, {"url": str(raw.get("url") or raw.get("query") or "")}
    return tool, dict(raw)


def claude_pre_tool_use(payload: dict[str, Any], policy: Policy, audit: AuditLog) -> dict[str, Any]:
    tool, args = map_claude_call(payload)
    decision = policy.decide(tool, args)
    audit.append(
        agent=policy.agent,
        tool=tool,
        args=args,
        decision=decision.action,
        policy_decision=decision.action,
        rule=decision.rule,
        reason=decision.reason,
        approval=None,
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision.action,
            "permissionDecisionReason": decision.reason,
        }
    }


def invalid_payload(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"scoped: {reason}",
        }
    }

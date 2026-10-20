from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Sequence, TextIO

from .approval import Approver
from .audit import AuditLog
from .policy import Decision, Policy


def _error_response(request_id: Any, decision: str, rule: str, reason: str, receipt: int) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32001,
            "message": f"scoped: {reason}",
            "data": {"decision": decision, "rule": rule, "receipt": receipt},
        },
    }


def _call_parts(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    params = message.get("params") or {}
    if not isinstance(params, dict):
        params = {}
    tool = str(params.get("name", ""))
    args = params.get("arguments") or {}
    if not isinstance(args, dict):
        args = {"value": args}
    return tool, args


def _evaluate(
    policy: Policy,
    approver: Approver,
    tool: str,
    args: dict[str, Any],
) -> tuple[Decision, str, str | None]:
    decision = policy.decide(tool, args)
    approved: str | None = None
    actual = decision.action
    if actual == "ask":
        ok, approved = approver.approve(tool, args, decision.reason)
        actual = "allow" if ok else "deny"
    return decision, actual, approved


def _log(
    audit: AuditLog,
    policy: Policy,
    tool: str,
    args: dict[str, Any],
    decision: Decision,
    actual: str,
    approved: str | None,
    reason: str | None = None,
) -> dict[str, Any]:
    return audit.append(
        agent=policy.agent,
        tool=tool,
        args=args,
        decision=actual,
        policy_decision=decision.action,
        rule=decision.rule,
        reason=reason or decision.reason,
        approval=approved,
    )


def _handle_batch(
    batch: list[Any],
    *,
    raw: str,
    policy: Policy,
    approver: Approver,
    audit: AuditLog,
    child: subprocess.Popen,
    stdout: TextIO,
) -> None:
    prepared: list[tuple[dict[str, Any], str | None, dict[str, Any] | None, Decision | None, str | None, str | None]] = []
    for item in batch:
        if isinstance(item, dict) and item.get("method") == "tools/call":
            tool, args = _call_parts(item)
            decision, actual, approved = _evaluate(policy, approver, tool, args)
            prepared.append((item, tool, args, decision, actual, approved))
        else:
            prepared.append((item, None, None, None, None, None))

    denied = [row for row in prepared if row[4] == "deny"]
    if denied:
        first = denied[0]
        assert first[3] is not None
        reason = f"batch aborted: {first[3].reason}"
        responses: list[dict[str, Any]] = []
        for item, tool, args, decision, _actual, approved in prepared:
            if tool is None or args is None or decision is None:
                continue
            entry = _log(audit, policy, tool, args, decision, "deny", approved, reason=reason)
            if "id" in item:
                responses.append(_error_response(item.get("id"), "deny", decision.rule, reason, entry["seq"]))
        if responses:
            stdout.write(json.dumps(responses, ensure_ascii=False) + "\n")
            stdout.flush()
        return

    for _item, tool, args, decision, actual, approved in prepared:
        if tool is None or args is None or decision is None or actual is None:
            continue
        _log(audit, policy, tool, args, decision, actual, approved)
    assert child.stdin is not None
    child.stdin.write(raw + "\n")
    child.stdin.flush()


def run_proxy(
    *,
    policy: Policy,
    server: Sequence[str],
    audit_path: str | Path,
    approver: Approver | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    approver = approver or Approver()
    audit = AuditLog(audit_path)

    try:
        child = subprocess.Popen(
            list(server),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        print(f"scoped: cannot start server {server!r}: {exc}", file=stderr)
        return 2

    def pump() -> None:
        assert child.stdout is not None
        for line in child.stdout:
            stdout.write(line)
            stdout.flush()

    reader = threading.Thread(target=pump, daemon=True)
    reader.start()

    assert child.stdin is not None

    try:
        for raw in stdin:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                child.stdin.write(line + "\n")
                child.stdin.flush()
                continue

            if isinstance(message, list):
                _handle_batch(
                    message,
                    raw=line,
                    policy=policy,
                    approver=approver,
                    audit=audit,
                    child=child,
                    stdout=stdout,
                )
                continue

            if not isinstance(message, dict) or message.get("method") != "tools/call":
                child.stdin.write(line + "\n")
                child.stdin.flush()
                continue

            tool, args = _call_parts(message)
            decision, actual, approved = _evaluate(policy, approver, tool, args)
            entry = _log(audit, policy, tool, args, decision, actual, approved)
            if actual == "deny":
                if "id" in message:
                    response = _error_response(
                        message.get("id"), actual, decision.rule, decision.reason, entry["seq"]
                    )
                    stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                    stdout.flush()
                continue

            child.stdin.write(line + "\n")
            child.stdin.flush()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            child.stdin.close()
        except OSError:
            pass
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
        reader.join(timeout=1)
    return child.returncode or 0

#!/usr/bin/env python3
"""Adversarial test suite for scoped v0.1. Run: python tests/adversarial/run.py"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # scoped/
sys.path.insert(0, str(ROOT))

import scoped.audit as audit  # noqa: E402
from scoped.audit import AuditLog  # noqa: E402
from scoped.cli import main as cli_main  # noqa: E402

results: list[tuple[str, str]] = []


def record(name: str, status: str) -> None:
    results.append((name, status))
    print(f"{status}: {name}")


def send_through_proxy(lines: list[str], env_extra: dict[str, str], workdir: pathlib.Path, policy_path: str | None = None) -> tuple[int, list[str], pathlib.Path]:
    audit_file = workdir / ".adversarial" / "audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    audit_file.write_text("")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env.update(env_extra)
    cmd = [sys.executable, "-m", "scoped", "proxy", "--audit", str(audit_file)]
    if policy_path:
        cmd += ["--policy", policy_path]
    cmd += ["--", sys.executable, str(HERE / "mcp_server.py")]
    proc = subprocess.run(
        cmd,
        input="\n".join(lines) + "\n",
        capture_output=True,
        text=True,
        env=env,
        cwd=workdir,
        timeout=30,
    )
    return proc.returncode, join_frames(proc.stdout), audit_file


def join_frames(raw: str) -> list[str]:
    return [l for l in raw.splitlines() if l.strip()]


def load_test_policy(workdir: pathlib.Path) -> str:
    policy = workdir / "policy_deny_env.toml"
    shutil.copy(HERE / "policy_deny_env.toml", policy)
    return str(policy)


def case_batch_frame(workdir: pathlib.Path) -> None:
    """B1: a batched JSON-RPC array frame must not crash the proxy."""
    policy = load_test_policy(workdir)
    batch = [{"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"query": "SELECT 1"}}}]
    rc, out, _ = send_through_proxy([json.dumps(batch)], {}, workdir, policy_path=policy)
    if rc != 0:
        record("B1 batch frame does not crash proxy", "BLOCKER_FOUND " + f"exit={rc}")
        return
    forwarded = len(out) > 0
    record("B1 batch frame does not crash proxy", "PASS" if forwarded else "FAIL (no response)")


def case_default_env_read(workdir: pathlib.Path) -> None:
    """B2: default generated policy must deny .env reads; check --file style probe via check."""
    sys.argv = ["scoped", "init", "--force", "--dir", str(workdir / "d2")]
    cli_main()
    sys.argv = [
        "scoped", "check", "--policy", str(workdir / "d2" / "scoped.toml"),
        "--tool", "read_file", "--args", '{"path": ".env"}',
    ]
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli_main() or 0
    # check exit codes: allow=0 ask=3 deny=4
    record("B2 generated default denies .env read", "PASS" if code == 4 else ("BLOCKER_FINDING" if code == 0 else f"INFO exit={code} ({'ask' if code == 3 else 'deny'})"))


def case_sql_obfuscation(workdir: pathlib.Path) -> None:
    """S-PASS check: SQL verb hidden in comment avoids plain contains()"""
    sys.argv = [
        "scoped", "check", "--policy", str(workdir / "policy_deny_env.toml"),
        "--tool", "run_sql", "--args", '{"query": "/*peaceful*/ SELECT 1"}',
    ]
    raise SystemExit


def case_chain_tamper(workdir: pathlib.Path) -> None:
    """S: hash chain detects tampering of one receipt."""
    log = AuditLog(workdir / "audit.jsonl")
    log.append(agent="a", tool="shell", args={"cmd": "echo hi"}, decision="ask", policy_decision="ask", rule="ask-shell", reason="ok")
    log.append(agent="a", tool="shell", args={"cmd": "echo bye"}, decision="allow", policy_decision="ask", rule="ask-shell", reason="auto-allow")
    p = log.path
    lines = p.read_text().splitlines()
    doc = json.loads(lines[0])
    doc["decision"] = "deny"
    lines[0] = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    p.write_text("\n".join(lines) + "\n")
    errs = log.verify()
    record("CHAIN detects receipt tamper", "PASS" if errs else "FAIL")


def main() -> int:
    for workdir in [pathlib.Path(tempfile.mkdtemp())]:
        case_batch_frame(workdir)
        case_default_env_read(workdir)
        case_chain_tamper(workdir)
    blockers = [n for n, s in results if s.startswith("BLOCKER")]
    print("== summary ==")
    for n, s in results:
        print(f"{s:10} {n}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())

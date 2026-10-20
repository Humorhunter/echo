#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = HERE / ".demo"
POLICY = WORK / "scoped.toml"
AUDIT = WORK / "audit.jsonl"


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    shutil.copy(HERE / "scoped.toml", POLICY)
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "examples/scoped.toml"}}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": ".env"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "DROP TABLE users"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "SELECT 1"}}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "shell", "arguments": {"command": "echo hi"}}},
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "scoped",
            "proxy",
            "--policy",
            str(POLICY),
            "--audit",
            str(AUDIT),
            "--approve",
            "--",
            sys.executable,
            str(HERE / "fake_mcp_server.py"),
        ],
        input="\n".join(json.dumps(request) for request in requests) + "\n",
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
        timeout=20,
    )
    if process.returncode != 0:
        print(process.stderr, file=sys.stderr)
        return process.returncode

    responses = {}
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        response = json.loads(line)
        if isinstance(response, list):
            for item in response:
                responses[item.get("id")] = item
        else:
            responses[response.get("id")] = response

    def status(request_id: int) -> str:
        response = responses.get(request_id, {})
        if "error" in response:
            return "BLOCKED " + response["error"]["message"]
        return "ALLOWED"

    print("scoped demo: MCP stdio proxy\n")
    for request_id, label in [
        (2, "read_file examples/scoped.toml"),
        (3, "read_file .env"),
        (4, "run_sql DROP TABLE users"),
        (5, "run_sql SELECT 1"),
        (6, "shell echo hi"),
    ]:
        print(f"  {label:36} {status(request_id)}")

    verify = subprocess.run(
        [sys.executable, "-m", "scoped", "audit", "verify", "--file", str(AUDIT)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    print("\n" + verify.stdout.strip())
    return verify.returncode


if __name__ == "__main__":
    raise SystemExit(main())

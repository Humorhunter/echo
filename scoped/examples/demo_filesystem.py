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
WORK = HERE / ".demo-root"
AUDIT = HERE / ".demo" / "fs-audit.jsonl"
POLICY = HERE / "scoped.toml"


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    (WORK / "src").mkdir(parents=True)
    (WORK / ".env").write_text("API_KEY=demo-secret\n", encoding="utf-8")
    (WORK / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    AUDIT.parent.mkdir(exist_ok=True)
    AUDIT.unlink(missing_ok=True)

    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "src/main.py"}}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": ".env"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "../../README.md"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "write_file", "arguments": {"path": "src/generated.txt", "content": "made by demo\n"}}},
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
            str(HERE / "filesystem_mcp_server.py"),
            str(WORK),
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
        responses[response.get("id")] = response

    def status(request_id: int) -> str:
        response = responses.get(request_id, {})
        if "error" in response:
            return "BLOCKED " + response["error"]["message"]
        result = response.get("result", {})
        if result.get("isError"):
            return "SERVER-ERROR " + result["content"][0]["text"]
        return "ALLOWED"

    print("scoped demo: real filesystem MCP server under policy\n")
    for request_id, label in [
        (2, "read_file src/main.py"),
        (3, "read_file .env"),
        (4, "read_file ../../README.md"),
        (5, "write_file src/generated.txt"),
    ]:
        print(f"  {label:34} {status(request_id)}")
    print(f"\n  generated file exists: {(WORK / 'src' / 'generated.txt').exists()}")

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

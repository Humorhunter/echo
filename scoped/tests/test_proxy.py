from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "examples" / "scoped.toml"
SERVER = ROOT / "examples" / "fake_mcp_server.py"
TMP = Path(__file__).parent / ".tmp"
TMP.mkdir(exist_ok=True)


def parse(raw: str) -> list:
    parsed = []
    for line in raw.splitlines():
        if line.strip():
            parsed.append(json.loads(line))
    return parsed


class ProxyTest(unittest.TestCase):
    def run_proxy(self, requests, *extra):
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        audit = Path(tmp.name) / "audit.jsonl"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        command = [
            sys.executable,
            "-m",
            "scoped",
            "proxy",
            "--policy",
            str(POLICY),
            "--audit",
            str(audit),
            *extra,
            "--",
            sys.executable,
            str(SERVER),
        ]
        payload = "\n".join(json.dumps(request) for request in requests) + "\n"
        process = subprocess.run(
            command,
            input=payload,
            capture_output=True,
            text=True,
            cwd=ROOT,
            env=env,
            timeout=20,
        )
        return process, audit, parse(process.stdout)

    def test_allow_deny_and_audit(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "README.md"}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": ".env"}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "DROP TABLE users"}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "SELECT 1"}}},
        ]
        process, audit, messages = self.run_proxy(requests)
        self.assertEqual(process.returncode, 0, process.stderr)
        by_id = {message.get("id"): message for message in messages if isinstance(message, dict)}
        self.assertIn("result", by_id[2])
        self.assertIn("error", by_id[3])
        self.assertIn("error", by_id[4])
        self.assertIn("result", by_id[5])
        from scoped.audit import AuditLog
        self.assertEqual(AuditLog(audit).verify(), [])
        self.assertEqual(len(AuditLog(audit)._entries()), 4)

    def test_ask_auto_approve(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "shell", "arguments": {"command": "echo hi"}}},
        ]
        process, audit, messages = self.run_proxy(requests, "--approve")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("result", messages[0])
        from scoped.audit import AuditLog
        entry = AuditLog(audit)._entries()[0]
        self.assertEqual(entry["decision"], "allow")
        self.assertEqual(entry["approval"], "auto-allow")

    def test_mixed_batch_fails_closed_without_crash(self):
        batch = [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "SELECT 1"}}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "run_sql", "arguments": {"sql": "DROP TABLE users"}}},
        ]
        process, audit, messages = self.run_proxy([batch])
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(len(messages), 1)
        self.assertIsInstance(messages[0], list)
        self.assertEqual(len(messages[0]), 2)
        self.assertTrue(all("error" in item for item in messages[0]))
        from scoped.audit import AuditLog
        entries = AuditLog(audit)._entries()
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(entry["decision"] == "deny" for entry in entries))
        self.assertEqual(AuditLog(audit).verify(), [])

    def test_malformed_frame_does_not_crash(self):
        process, _audit, messages = self.run_proxy(["not json"])
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()

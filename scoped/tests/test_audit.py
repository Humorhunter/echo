from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scoped.audit import AuditLog, redact  # noqa: E402

TMP = Path(__file__).parent / ".tmp"
TMP.mkdir(exist_ok=True)


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.path = Path(self.tmp.name) / "audit.jsonl"
        self.log = AuditLog(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def append(self, tool="shell", decision="allow", payload=None):
        return self.log.append(
            agent="a",
            tool=tool,
            args=payload or {"command": "echo hi"},
            decision=decision,
            policy_decision="ask",
            rule="ask-shell",
            reason="test",
            approval="user" if decision == "allow" else None,
        )

    def test_verify_ok_and_chain(self):
        first = self.append()
        second = self.append()
        self.assertEqual(first["prev"], "0" * 64)
        self.assertEqual(second["prev"], first["hash"])
        self.assertEqual(self.log.verify(), [])

    def test_tamper_detected(self):
        self.append()
        self.append()
        lines = self.path.read_text().splitlines()
        entry = json.loads(lines[0])
        entry["decision"] = "deny"
        lines[0] = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        self.path.write_text("\n".join(lines) + "\n")
        self.assertTrue(self.log.verify())

    def test_redact_secret_keys(self):
        value = redact({
            "authorization": "Bearer abc",
            "authorization2": "x",
            "bearer": "abc",
            "pwd": "hunter2",
            "credentials": {"user": "u"},
            "session_key": "k",
            "path": "src/main.py",
        })
        for key in ["authorization", "authorization2", "bearer", "pwd", "credentials", "session_key"]:
            self.assertEqual(value[key], "***")
        self.assertEqual(value["path"], "src/main.py")

    def test_redact_truncates_long_strings(self):
        value = redact({"text": "x" * 1000})
        self.assertIn("truncated", value["text"])


if __name__ == "__main__":
    unittest.main()

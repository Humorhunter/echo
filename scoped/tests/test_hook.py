from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scoped.audit import AuditLog  # noqa: E402
from scoped.hooks import claude_pre_tool_use, invalid_payload, map_claude_call  # noqa: E402
from scoped.policy import load_policy  # noqa: E402

TMP = Path(__file__).parent / ".tmp"
TMP.mkdir(exist_ok=True)
POLICY = ROOT / "examples" / "scoped.toml"


class HookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.audit = AuditLog(Path(self.tmp.name) / "audit.jsonl")
        self.policy = load_policy(POLICY)

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, tool, tool_input):
        payload = {"session_id": "s1", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
        output = claude_pre_tool_use(payload, self.policy, self.audit)
        return output["hookSpecificOutput"]["permissionDecision"]

    def test_read_secret_denied(self):
        self.assertEqual(self.run_hook("Read", {"file_path": ".env"}), "deny")

    def test_read_normal_allowed(self):
        self.assertEqual(self.run_hook("Read", {"file_path": "src/main.py"}), "allow")

    def test_write_asks(self):
        self.assertEqual(self.run_hook("Write", {"file_path": "src/main.py", "content": "x"}), "ask")

    def test_shell_asks(self):
        self.assertEqual(self.run_hook("Bash", {"command": "rm -rf build"}), "ask")

    def test_mcp_tool_defaults_ask(self):
        self.assertEqual(self.run_hook("mcp__postgres__query", {"sql": "select 1"}), "ask")

    def test_mapping(self):
        tool, args = map_claude_call({"tool_name": "Read", "tool_input": {"file_path": "a.txt"}})
        self.assertEqual((tool, args), ("read_file", {"path": "a.txt"}))
        tool, args = map_claude_call({"tool_name": "mcp__pg__query", "tool_input": {"sql": "select 1"}})
        self.assertEqual((tool, args), ("pg.query", {"sql": "select 1"}))

    def test_audit_chain(self):
        self.run_hook("Read", {"file_path": "src/main.py"})
        self.run_hook("Read", {"file_path": ".env"})
        self.assertEqual(self.audit.verify(), [])
        self.assertEqual(len(self.audit._entries()), 2)

    def test_invalid_payload_shape(self):
        output = invalid_payload("bad")
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()

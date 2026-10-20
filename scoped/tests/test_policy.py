from __future__ import annotations

import tomllib
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scoped.cli import DEFAULT_POLICY  # noqa: E402
from scoped.policy import PolicyError, policy_from_dict  # noqa: E402


class PolicyTest(unittest.TestCase):
    def policy(self):
        return policy_from_dict(tomllib.loads(DEFAULT_POLICY))

    def test_default_denies_secret_paths(self):
        policy = self.policy()
        for path in [".env", ".env.local", "config/.env", ".ssh/id_rsa", "credentials", "authorized_keys", ".aws/credentials"]:
            with self.subTest(path=path):
                self.assertEqual(policy.decide("read_file", {"path": path}).action, "deny")

    def test_default_allows_normal_file(self):
        policy = self.policy()
        self.assertEqual(policy.decide("read_file", {"path": "src/main.py"}).action, "allow")

    def test_destructive_sql_denied_even_obfuscated(self):
        policy = self.policy()
        for sql in ["DROP TABLE users", "/* calm */ DELETE FROM users", "with x as (select 1) delete from users"]:
            with self.subTest(sql=sql):
                self.assertEqual(policy.decide("run_sql", {"sql": sql}).action, "deny")

    def test_select_allowed(self):
        policy = self.policy()
        self.assertEqual(policy.decide("run_sql", {"sql": "SELECT * FROM users"}).action, "allow")

    def test_unknown_tool_default_ask(self):
        policy = self.policy()
        self.assertEqual(policy.decide("unknown_tool", {}).action, "ask")

    def test_invalid_decision_rejected(self):
        with self.assertRaises(PolicyError):
            policy_from_dict({"default": "maybe"})


if __name__ == "__main__":
    unittest.main()

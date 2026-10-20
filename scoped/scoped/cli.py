from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .approval import Approver
from .audit import AuditLog
from .policy import PolicyError, load_policy
from .proxy import run_proxy

DEFAULT_POLICY = r'''agent = "claude"
default = "ask"
audit = ".scoped/audit.jsonl"

[[rules]]
name = "deny-destructive-sql"
tool = "run_sql"
decision = "deny"
[rules.match]
sql_verbs = ["drop", "delete", "truncate", "alter", "grant"]

[[rules]]
name = "allow-select"
tool = "run_sql"
decision = "allow"
[rules.match]
sql_verbs = ["select"]

[[rules]]
name = "deny-secret-paths"
tool = "read_file"
decision = "deny"
[rules.match.regex]
path = '(?i)(^|/)(\.env(\..*)?|\.ssh(/.*)?|credentials(\..*)?|authorized_keys|id_rsa|id_ed25519|\.aws/credentials)$'

[[rules]]
name = "allow-file-read"
tool = "read_file"
decision = "allow"

[[rules]]
name = "ask-shell"
tool = "shell"
decision = "ask"
'''


def _audit_path(policy, override: str | None) -> Path:
    if override:
        return Path(override)
    path = Path(policy.audit)
    if path.is_absolute():
        return path
    return Path(policy.source).resolve().parent / path


def _load(args) -> tuple[object, Path]:
    policy = load_policy(args.policy)
    return policy, _audit_path(policy, getattr(args, "audit", None))


def cmd_init(args) -> int:
    root = Path(args.dir)
    root.mkdir(parents=True, exist_ok=True)
    policy_path = root / "scoped.toml"
    if policy_path.exists() and not args.force:
        print(f"refusing to overwrite existing {policy_path} (use --force)", file=sys.stderr)
        return 1
    policy_path.write_text(DEFAULT_POLICY, encoding="utf-8")
    scoped_dir = root / ".scoped"
    scoped_dir.mkdir(exist_ok=True)
    gitignore = scoped_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*.jsonl\n", encoding="utf-8")
    print(f"created {policy_path}")
    print(f"created {scoped_dir}/ (audit logs are gitignored)")
    print("next: scoped proxy --policy scoped.toml -- <mcp-server-command>")
    return 0


def cmd_check(args) -> int:
    try:
        policy = load_policy(args.policy)
    except PolicyError as exc:
        print(f"scoped: {exc}", file=sys.stderr)
        return 2
    try:
        values = json.loads(args.args)
    except json.JSONDecodeError as exc:
        print(f"scoped: --args must be JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(values, dict):
        print("scoped: --args must be a JSON object", file=sys.stderr)
        return 2
    decision = policy.decide(args.tool, values)
    payload = {
        "tool": args.tool,
        "decision": decision.action,
        "rule": decision.rule,
        "reason": decision.reason,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{decision.action}: {decision.reason} (rule={decision.rule})")
    return {"allow": 0, "ask": 3, "deny": 4}[decision.action]


def cmd_proxy(args) -> int:
    try:
        policy, audit_path = _load(args)
    except PolicyError as exc:
        print(f"scoped: {exc}", file=sys.stderr)
        return 2
    server = list(args.server)
    if server and server[0] == "--":
        server = server[1:]
    if not server:
        print("scoped: missing MCP server command after --", file=sys.stderr)
        return 2
    approver = Approver(allow_all=args.approve, deny_all=args.deny_ask)
    return run_proxy(policy=policy, server=server, audit_path=audit_path, approver=approver)


def cmd_audit_verify(args) -> int:
    log = AuditLog(args.file)
    if not log.path.exists():
        print(f"scoped: audit log not found: {log.path}", file=sys.stderr)
        return 2
    try:
        errors = log.verify()
    except ValueError as exc:
        print(f"scoped: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(log._entries())} receipts verified: {log.path}")
    return 0


def cmd_audit_tail(args) -> int:
    log = AuditLog(args.file)
    if not log.path.exists():
        print(f"scoped: audit log not found: {log.path}", file=sys.stderr)
        return 2
    entries = log._entries()[-args.lines :]
    for entry in entries:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scoped", description="Least-privilege and auditable receipts for AI agent tool calls")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create scoped.toml and .scoped/")
    init.add_argument("--dir", default=".", help="project directory")
    init.add_argument("--force", action="store_true", help="overwrite scoped.toml")
    init.set_defaults(func=cmd_init)

    check = sub.add_parser("check", help="evaluate one tool call against a policy")
    check.add_argument("--policy", default="scoped.toml")
    check.add_argument("--tool", required=True)
    check.add_argument("--args", default="{}", help="JSON object of tool arguments")
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=cmd_check)

    proxy = sub.add_parser("proxy", help="wrap an MCP stdio server and enforce policy")
    proxy.add_argument("--policy", default="scoped.toml")
    proxy.add_argument("--audit", default=None, help="override audit log path")
    group = proxy.add_mutually_exclusive_group()
    group.add_argument("--approve", action="store_true", help="auto-allow every ask decision")
    group.add_argument("--deny-ask", action="store_true", help="auto-deny every ask decision")
    proxy.add_argument("server", nargs=argparse.REMAINDER, help="-- <server command>")
    proxy.set_defaults(func=cmd_proxy)

    audit = sub.add_parser("audit", help="inspect audit receipts")
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)
    verify = audit_sub.add_parser("verify", help="verify the hash chain")
    verify.add_argument("--file", default=".scoped/audit.jsonl")
    verify.set_defaults(func=cmd_audit_verify)
    tail = audit_sub.add_parser("tail", help="print the latest receipts")
    tail.add_argument("--file", default=".scoped/audit.jsonl")
    tail.add_argument("-n", "--lines", type=int, default=5)
    tail.set_defaults(func=cmd_audit_tail)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

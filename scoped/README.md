# Scoped

**Least privilege and auditable receipts for AI agent tool calls.**

Scoped sits between an MCP client (Claude Code, Codex, OpenCode, or your own agent) and an MCP stdio server. It answers one question before a tool runs:

> May this agent, in this session, call this tool with these arguments?

It returns **allow / ask / deny**, asks a human when needed, and writes a hash-chained **receipt** for every decision. It is a local-first developer tool — not a sandbox, not a network firewall, and not a security guarantee.

Status: **v0.1 MVP.** Working MCP stdio proxy + Claude Code `PreToolUse` hook adapter. Codex/OpenCode snippets and shell/HTTP/Postgres adapters are next.

## Why

Coding agents can now read repos, run shell commands, query databases, and call MCP tools. Most setups give them all-or-nothing access. One bad tool call can read `.env`, drop a table, or push a destructive commit. Static scanners tell you about risk; they do not stop the call.

Scoped is the missing runtime check: policy-as-code, approval for risky actions, and a receipt you can verify later.

## Quickstart

Requires Python 3.11+ and an MCP stdio server command.

```bash
cd scoped
python3 -m venv .venv
. .venv/bin/activate
pip install -e .

scoped init
scoped check --tool run_sql --args '{"sql":"DROP TABLE users"}'
# deny: deny by deny-destructive-sql ... (exit 4)

scoped proxy --policy scoped.toml -- <your-mcp-server-command>
```

`scoped init` creates `scoped.toml` and `.scoped/` (audit logs are gitignored). Edit the policy, then wrap the server your agent already uses. The client speaks normal MCP JSON-RPC; Scoped forwards everything except calls it blocks.

### Run the demos

```bash
cd scoped
python3 examples/demo.py            # fake MCP server: policy decisions + receipts
python3 examples/demo_filesystem.py # real filesystem MCP server: read/write/deny + sandbox escape
```

Expected for the filesystem demo: `src/main.py` read allowed, `.env` blocked by policy, `../../README.md` blocked by the server's own sandbox, generated write allowed after `--approve`; 4 receipts verify.

### Claude Code hook

Add to `.claude/settings.json` in your project (see `examples/claude-settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read|Write|Edit|MultiEdit|WebFetch|mcp__.*",
        "hooks": [
          {"type": "command", "command": "scoped hook claude --policy scoped.toml"}
        ]
      }
    ]
  }
}
```

The hook maps Claude tools to policy tools (`Bash`→`shell`, `Read`→`read_file`, `Write`/`Edit`→`write_file`, `mcp__server__tool`→`server.tool`) and returns `allow` / `ask` / `deny`. `ask` uses Claude Code's own approval UI. Every decision is receipted.

Test without Claude Code:

```bash
printf '%s\n' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | scoped hook claude --policy scoped.toml
# {"hookSpecificOutput": {"permissionDecision": "deny", ...}}
```

See `docs/claude-hook.md` for behavior and limits.

### Verify receipts

```bash
scoped audit verify --file .scoped/audit.jsonl
scoped audit tail --file .scoped/audit.jsonl -n 3
```

## Policy

TOML by default. JSON and YAML are also accepted (YAML needs `pip install 'scoped-agent[yaml]'`). Rules are evaluated **in order, first match wins**; put deny rules before allow rules.

```toml
agent = "claude"
default = "ask"
audit = ".scoped/audit.jsonl"

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
name = "ask-shell"
tool = "shell"
decision = "ask"
```

Match helpers: `tool` is a glob (`*`, `postgres.*`); `match.equals`, `match.contains`, `match.regex` apply to argument keys; `match.sql_verbs` scans `sql` / `query` / `statement` / `command` for any listed keyword. `decision` is `allow`, `ask`, or `deny`; `default` is used when no rule matches.

Exit codes for `scoped check`: `0` allow, `3` ask, `4` deny, `2` error.

## How it works

1. `scoped proxy` starts the real MCP server as a child process.
2. It reads newline-delimited JSON-RPC from the client.
3. For `tools/call`, it evaluates the policy against the tool name and arguments.
4. `deny` returns a JSON-RPC error and never touches the server; `ask` prompts on `/dev/tty` (non-interactive with no TTY = deny); `allow` forwards the call.
5. Every decision is appended to a hash-chained JSONL receipt log.
6. Batched calls are **fail-closed**: if any call in a batch is denied, the whole batch is not executed and every call gets an error response.

## What Scoped does not do

- It is **not a sandbox**. It does not isolate processes, filesystems, or networks.
- It only sees the MCP stdio boundary. A malicious server can still do anything its own process can do after an allowed call.
- The SQL check is keyword-based, not a SQL parser. Use a read-only DB role as defense in depth.
- A full rewrite of the audit file can rebuild a valid hash chain. Receipts are tamper-evident, not tamper-proof; external anchoring is future work.
- It does not claim SOC2/ISO/EU AI Act compliance.

See `docs/threat-model.md` and `docs/receipts.md`.

## Tests

```bash
cd scoped
python3 -m unittest discover -s tests -v
TMPDIR="$PWD/tests/.tmp" PYTHONPATH="$PWD" python3 tests/adversarial/run.py
```

22 unit/integration tests plus echo2's 3-case adversarial suite: batch frames, secret-path bypass, SQL comment obfuscation, audit tamper detection, secret redaction, Claude hook mapping, and a real filesystem MCP server.

## Roadmap (concrete, not commitments)

- Codex/OpenCode config snippets (the Claude Code `PreToolUse` adapter is in `scoped hook claude`).
- PostToolUse outcome receipts (so an `ask` receipt can record the final allow/deny).
- Shell command wrapper with an allowlist and approval, sharing the same policy/audit engine.
- HTTP egress allowlist and Postgres read-only adapter.
- External append-only receipt anchor (e.g., GitHub release/asset or a user-provided sink).
- `scoped audit replay` with a local HTML view.

## License

Apache-2.0. See `LICENSE` and `NOTICE`.

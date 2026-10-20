# Scoped threat model (v0.1)

## What Scoped protects

Scoped is a runtime permission and receipt layer for MCP tool calls. It aims to prevent an agent from performing a small set of high-impact actions without an explicit policy decision or human approval:

- reading known secret paths (`.env`, `.ssh`, credentials);
- destructive SQL (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `GRANT`);
- unapproved shell commands;
- any tool call that a policy marks `deny` or `ask`.

It also produces a hash-chained receipt for each decision so a human can review what happened after the fact.

## Assets

- Repository files, including `.env`, `.ssh`, credentials, and source code.
- Databases reachable by MCP servers.
- Cloud credentials available to the agent/server process.
- The audit trail itself (integrity and availability).
- User attention (approval fatigue is a security failure).

## Adversaries and failure modes

1. **Prompt injection**: untrusted content tells the agent to call a dangerous tool.
2. **Malicious or overprivileged MCP server**: a server exposes dangerous tools or performs side effects after an allowed call.
3. **Agent mistake**: wrong tool, wrong path, wrong SQL, wrong environment.
4. **Misconfiguration**: policy allows too much, wrong tool name, missing rule.
5. **Insider/compromised account**: someone edits the policy or audit file.
6. **Bypass**: the client talks to the server without going through the proxy.

## Trust boundaries

- **Trusted**: the Scoped code, the policy file, and the human approving.
- **Untrusted**: the MCP client's intent, tool arguments, the MCP server, and any content the agent reads.
- **Observed boundary**: MCP stdio JSON-RPC. Scoped only sees calls that pass through it.

## What Scoped does not protect

- **Not a sandbox.** An allowed process can still read/write anything its OS user can.
- **Not a network firewall.** Direct HTTP from the server or shell is not intercepted in v0.1.
- **Not a SQL parser.** Keyword matching can be bypassed by obfuscation, stored procedures, or server-specific syntax; use a read-only DB role.
- **Not complete coverage.** A client that bypasses the proxy, or a server that performs side effects on `tools/list`, is outside the boundary.
- **Not tamper-proof.** A full rewrite of the audit file can rebuild a valid chain. Receipts are tamper-evident only against partial edits unless externally anchored.

## Security properties

- Default policy denies secret paths and destructive SQL, and asks for shell/unknown tools.
- Denied calls never reach the MCP server.
- Batched calls fail closed: one denied call aborts the batch.
- Non-interactive `ask` denies (no TTY => no approval).
- Receipts redact keys containing secret/token/password/credential markers and truncate long values.
- Audit entries are hash-chained; `scoped audit verify` detects edits, reordering, and missing entries.

## Operational guidance

- Run the MCP server with the least OS privileges possible.
- Use a read-only database role for read-only tools.
- Keep the policy in the repo and review changes.
- Do not rely on Scoped as the only control for production credentials.
- Treat approval fatigue as a real risk: use narrow allow rules and short-lived approvals.
- Pin the server command and version; do not let the agent choose arbitrary server commands.

## Disclosure

Report security issues privately to the maintainers. Do not test against systems you do not own. This is a best-effort tool provided under Apache-2.0 without warranty.

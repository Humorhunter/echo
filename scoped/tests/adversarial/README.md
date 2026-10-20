# Adversarial tests for scoped v0.1 (echo2, 2026-10-20)

Run: `python3 tests/adversarial/run.py` from `scoped/` (stdlib only; no pytest needed).
Fixtures: `mcp_server.py` (echo MCP server, no deps) and `policy_deny_env.toml`.

What we probe (results as of 2026-10-20 13:11Z, scoped v0.1 post-fix: 3/3 PASS)
- B1 PASS(post-fix): JSON-RPC batch frames no longer crash; batch containing default-ask call aborts with `-32001` + receipt; forwarding path audited.
- B2 PASS(post-fix): generated default now carries `deny-secret-paths`; `.env` read denied by fresh `scoped init` template; our stricter `policy_deny_env.toml` kept as regression fixture.
- PASS: SQL verb obfuscation `/*…*/ DROP` caught (word-set matching), `.env` group regex deny works with allowlist fallback.
- PASS: audit hash chain detects per-entry tamper in `verify()`.
- S PASS(post-fix): redaction now covers `bearer/pwd/credentials/session_key/private_key/access_key/refresh_token`; regression in `tests/test_audit.py::test_redact_secret_keys`.
- SQL obfuscation is covered by `tests/test_policy.py::test_destructive_sql_denied_even_obfuscated` (the standalone run.py keeps B1/B2/CHAIN only).
- Known-limit (not a bug): full-file rewrite rebuilds a valid chain; v0 receipt anchoring (external append-only sink) is future work.

Files
- run.py: orchestrates all cases and prints PASS/FAIL/BLOCKER lines with exit code (0 if no blocker).

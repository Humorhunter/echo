# Receipts

Every policy decision produces a receipt. Receipts are newline-delimited JSON, append-only, and hash-chained.

## Why a receipt, not just a log

A normal log says "something happened." A receipt says:

- which agent/session made the call;
- which tool and arguments (hashed, with a redacted preview);
- which policy rule matched;
- whether it was allowed, asked, or denied;
- who approved it (if anyone);
- what the previous receipt was, so edits are detectable.

That makes the decision reviewable after an incident and gives a concrete artifact for a PR, ticket, or audit conversation.

## Format

```json
{
  "seq": 3,
  "ts": "2026-10-20T13:00:00Z",
  "agent": "claude",
  "tool": "run_sql",
  "args_hash": "…",
  "args_preview": {"sql": "DROP TABLE users"},
  "decision": "deny",
  "policy_decision": "deny",
  "rule": "deny-destructive-sql",
  "reason": "deny by deny-destructive-sql for tool 'run_sql'",
  "approval": null,
  "prev": "…",
  "hash": "…"
}
```

`hash = sha256(canonical_json(entry without hash))`; `prev` is the previous entry's `hash`, or 64 zeros for the first entry. `canonical_json` uses sorted keys, no whitespace, UTF-8.

## Verify

```bash
scoped audit verify --file .scoped/audit.jsonl
```

Checks:

- `seq` is contiguous;
- `prev` matches the previous `hash`;
- recomputed `hash` matches.

Exit code 0 = chain intact; 1 = tampering/malformed; 2 = missing file.

## Privacy

`args_preview` redacts keys containing `secret`, `token`, `password`, `passwd`, `pwd`, `api_key`, `apikey`, `access_key`, `private_key`, `session_key`, `refresh_token`, `credentials`, `bearer`, `authorization`, or `cookie`. Long strings are truncated. `args_hash` is a SHA-256 of the full arguments, so two identical calls can be correlated without storing the raw value.

Do not put secrets in tool arguments if you can avoid it; redaction is best-effort, not a guarantee.

## Limits

- Hash chains detect edits but cannot prevent a full rewrite. External anchoring (a user-provided append-only sink or a signed release) is future work.
- Receipts do not prove the server did what it claimed; they prove what Scoped decided and forwarded.
- The audit file is local. Back it up if you need it for compliance.

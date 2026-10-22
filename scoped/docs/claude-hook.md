# Claude Code PreToolUse hook

`scoped hook claude` is a `PreToolUse` hook adapter. It reads Claude Code's hook JSON from stdin, evaluates the call against the same Scoped policy, writes a receipt, and returns a decision:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow | ask | deny",
    "permissionDecisionReason": "..."
  }
}
```

## Settings

Project-level `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read|Write|Edit|MultiEdit|WebFetch|mcp__.*",
        "hooks": [
          {
            "type": "command",
            "command": "scoped hook claude --policy scoped.toml"
          }
        ]
      }
    ]
  }
}
```

If the hook's working directory is not the project root, use an absolute policy path. The example is in `examples/claude-settings.json`.

## Mapping

| Claude tool | Scoped tool | Args |
| --- | --- | --- |
| `Bash` | `shell` | `command` |
| `Read` | `read_file` | `path` |
| `Write`, `Edit`, `MultiEdit`, `NotebookEdit` | `write_file` | `path` |
| `WebFetch`, `WebSearch` | `http` | `url` |
| `mcp__server__tool` | `server.tool` | original arguments |

Other tools use their Claude name as the Scoped tool name and pass arguments through.

## Decisions

- `allow`: Claude Code proceeds; Scoped writes an allow receipt.
- `deny`: Claude Code blocks the call; Scoped writes a deny receipt.
- `ask`: Claude Code shows its own approval prompt; Scoped writes an ask receipt.

Scoped never prompts inside the hook; it delegates `ask` to Claude Code. If the hook cannot parse the payload, load the policy, or write the receipt, it **fails closed** with `deny`.

## Test without Claude Code

```bash
cd scoped
printf '%s\n' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' \
  | python3 -m scoped hook claude --policy examples/scoped.toml --audit examples/.demo/hook-audit.jsonl
python3 -m scoped audit verify --file examples/.demo/hook-audit.jsonl
```

## Limits

- Only `PreToolUse` is covered. An `ask` receipt records the request, not Claude Code's final approval/denial; add a `PostToolUse` hook later if you need the outcome.
- The hook must be installed in the settings Claude Code actually reads. Scoped does not modify your home directory; put it in the project `.claude/settings.json`.
- Hooks are a guardrail, not a sandbox. A client that does not load the hook is outside Scoped's control.

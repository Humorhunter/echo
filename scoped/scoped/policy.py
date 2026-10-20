from __future__ import annotations

import fnmatch
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DECISIONS = {"allow", "ask", "deny"}
SQL_KEYS = ("sql", "query", "statement", "command")


class PolicyError(ValueError):
    pass


@dataclass(frozen=True)
class Decision:
    action: str
    rule: str
    reason: str


@dataclass
class Policy:
    default: str
    rules: list[dict[str, Any]] = field(default_factory=list)
    audit: str = ".scoped/audit.jsonl"
    agent: str = "agent"
    source: str = "<memory>"

    def decide(self, tool: str, args: dict[str, Any] | None = None) -> Decision:
        args = args or {}
        for index, rule in enumerate(self.rules):
            if _matches(rule, tool, args):
                name = str(rule.get("name") or f"rule[{index}]")
                return Decision(
                    action=rule["decision"],
                    rule=name,
                    reason=f"{rule['decision']} by {name} for tool {tool!r}",
                )
        return Decision(
            action=self.default,
            rule="default",
            reason=f"{self.default} by default for tool {tool!r}",
        )


def load_policy(path: str | Path) -> Policy:
    path = Path(path)
    if not path.is_file():
        raise PolicyError(f"policy not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".toml":
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise PolicyError(
                "YAML policy requires PyYAML; install with: pip install 'scoped-agent[yaml]'"
            ) from exc
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        raise PolicyError("policy must be .toml, .json, .yaml, or .yml")
    return policy_from_dict(data, source=str(path))


def policy_from_dict(data: dict[str, Any], source: str = "<memory>") -> Policy:
    if not isinstance(data, dict):
        raise PolicyError("policy root must be a mapping")
    default = str(data.get("default", "ask")).lower()
    if default not in DECISIONS:
        raise PolicyError(f"default must be one of {sorted(DECISIONS)}")
    audit = str(data.get("audit", ".scoped/audit.jsonl"))
    agent = str(data.get("agent", "agent"))
    raw_rules = data.get("rules", [])
    if not isinstance(raw_rules, list):
        raise PolicyError("rules must be an array")
    rules: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise PolicyError(f"rules[{index}] must be a table")
        tool = raw.get("tool")
        if not isinstance(tool, str) or not tool:
            raise PolicyError(f"rules[{index}].tool must be a non-empty string")
        decision = str(raw.get("decision", "")).lower()
        if decision not in DECISIONS:
            raise PolicyError(f"rules[{index}].decision must be one of {sorted(DECISIONS)}")
        match = raw.get("match", {})
        if match is None:
            match = {}
        if not isinstance(match, dict):
            raise PolicyError(f"rules[{index}].match must be a table")
        for key in ("equals", "contains", "regex"):
            value = match.get(key, {})
            if value is not None and not isinstance(value, dict):
                raise PolicyError(f"rules[{index}].match.{key} must be a table")
        verbs = match.get("sql_verbs")
        if verbs is not None and not isinstance(verbs, list):
            raise PolicyError(f"rules[{index}].match.sql_verbs must be an array")
        rules.append(
            {
                "tool": tool,
                "decision": decision,
                "name": str(raw.get("name") or f"rule[{index}]"),
                "match": match,
            }
        )
    return Policy(default=default, rules=rules, audit=audit, agent=agent, source=source)


def _matches(rule: dict[str, Any], tool: str, args: dict[str, Any]) -> bool:
    if not fnmatch.fnmatchcase(tool, rule["tool"]):
        return False
    match = rule.get("match") or {}
    for key, value in (match.get("equals") or {}).items():
        if args.get(key) != value:
            return False
    for key, value in (match.get("contains") or {}).items():
        if str(value).lower() not in str(args.get(key, "")).lower():
            return False
    for key, value in (match.get("regex") or {}).items():
        if re.search(str(value), str(args.get(key, ""))) is None:
            return False
    verbs = match.get("sql_verbs")
    if verbs:
        text = " ".join(str(args.get(key, "")) for key in SQL_KEYS)
        words = {word.lower() for word in re.findall(r"[A-Za-z_]+", text)}
        wanted = {str(verb).lower() for verb in verbs}
        if not words & wanted:
            return False
    return True

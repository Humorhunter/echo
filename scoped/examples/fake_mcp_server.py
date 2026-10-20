#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = [
    {"name": "read_file", "description": "Read a text file", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "run_sql", "description": "Run a SQL statement", "inputSchema": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}},
    {"name": "shell", "description": "Run a shell command", "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
]


def result(request_id, value):
    return {"jsonrpc": "2.0", "id": request_id, "result": value}


def error(request_id, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": message}}


def call_tool(name, args):
    if name == "read_file":
        path = Path(str(args.get("path", "")))
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
        return {"content": [{"type": "text", "text": text[:200]}]}
    if name == "run_sql":
        sql = str(args.get("sql", ""))
        first = sql.strip().split(None, 1)[0].lower() if sql.strip() else ""
        if first not in {"select", "with"}:
            return {"isError": True, "content": [{"type": "text", "text": "demo server only executes SELECT"}]}
        return {"content": [{"type": "text", "text": '{"rows":[{"ok":1}]}'}]}
    if name == "shell":
        return {"content": [{"type": "text", "text": f"demo: not executing {args.get('command', '')!r}"}]}
    return {"isError": True, "content": [{"type": "text", "text": f"unknown tool: {name}"}]}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict):
            continue
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            response = result(request_id, {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "fake", "version": "0.1"}})
        elif method == "tools/list":
            response = result(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = message.get("params") or {}
            response = result(request_id, call_tool(str(params.get("name", "")), params.get("arguments") or {}))
        elif request_id is None:
            continue
        else:
            response = error(request_id, f"unknown method: {method}")
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

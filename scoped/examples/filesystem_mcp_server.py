#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
TOOLS = [
    {"name": "read_file", "description": "Read a text file under the sandbox root", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "list_directory", "description": "List a directory under the sandbox root", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write a text file under the sandbox root", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
]


def response(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def failure(request_id, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": message}}


def safe_path(raw: str) -> Path:
    target = (ROOT / raw).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"path escapes sandbox: {raw}")
    return target


def call(name, args):
    try:
        if name == "read_file":
            target = safe_path(str(args.get("path", "")))
            text = target.read_text(encoding="utf-8")
            return {"content": [{"type": "text", "text": text[:2000]}]}
        if name == "list_directory":
            target = safe_path(str(args.get("path", ".")))
            names = sorted(item.name + ("/" if item.is_dir() else "") for item in target.iterdir())
            return {"content": [{"type": "text", "text": "\n".join(names)}]}
        if name == "write_file":
            target = safe_path(str(args.get("path", "")))
            target.parent.mkdir(parents=True, exist_ok=True)
            content = str(args.get("content", ""))
            target.write_text(content, encoding="utf-8")
            return {"content": [{"type": "text", "text": f"wrote {len(content)} bytes to {target}"}]}
    except (OSError, ValueError) as exc:
        return {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
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
            out = response(request_id, {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "filesystem-demo", "version": "0.1"}})
        elif method == "tools/list":
            out = response(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = message.get("params") or {}
            out = response(request_id, call(str(params.get("name", "")), params.get("arguments") or {}))
        elif request_id is None:
            continue
        else:
            out = failure(request_id, f"unknown method: {method}")
        print(json.dumps(out, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue
    rid = msg.get("id")
    if msg.get("method") == "tools/call" and "id" in msg:
        args = (msg.get("params") or {}).get("arguments", {})
        print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"echo": args}}), flush=True)
    elif "id" in msg:
        print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": {}}), flush=True)

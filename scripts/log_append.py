#!/usr/bin/env python3
import argparse
import fcntl
import os
import re
import sys
from datetime import datetime, timezone


def next_seq(text):
    nums = [int(x) for x in re.findall(r"^## \[[^\]]+\]\[#(\d+)\]", text, re.M)]
    return max(nums, default=0) + 1


def read_body(args):
    if args.body_file == "-":
        return sys.stdin.read()
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            return f.read()
    if args.body is not None:
        return args.body
    return sys.stdin.read()


def main():
    ap = argparse.ArgumentParser(description="Append-only task log writer")
    ap.add_argument("path")
    ap.add_argument("--from", dest="sender", required=True, choices=["echo1", "echo2"])
    ap.add_argument("--seq", type=int)
    ap.add_argument("--body")
    ap.add_argument("--body-file")
    ap.add_argument("--no-header", action="store_true")
    args = ap.parse_args()

    body = read_body(args).rstrip()
    if not body:
        raise SystemExit("empty body")

    parent = os.path.dirname(os.path.abspath(args.path))
    os.makedirs(parent, exist_ok=True)
    fd = os.open(args.path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
    with os.fdopen(fd, "a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.seek(0)
        text = f.read()
        seq = args.seq or next_seq(text)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        header = "" if args.no_header else f"## [{ts}][#{seq}] {args.sender}\n\n"
        f.seek(0, os.SEEK_END)
        if text and not text.endswith("\n"):
            f.write("\n")
        if text and header:
            f.write("\n")
        f.write(header + body + "\n")
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    main()

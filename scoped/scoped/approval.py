from __future__ import annotations

import os
import sys
from typing import Any


class Approver:
    def __init__(self, *, allow_all: bool = False, deny_all: bool = False):
        self.allow_all = allow_all
        self.deny_all = deny_all

    def approve(self, tool: str, args: dict[str, Any], reason: str) -> tuple[bool, str]:
        if self.allow_all:
            return True, "auto-allow"
        if self.deny_all:
            return False, "auto-deny"
        if os.environ.get("SCOPED_APPROVE", "").lower() in {"1", "yes", "true", "allow"}:
            return True, "env-allow"
        try:
            tty = open("/dev/tty", "r+", encoding="utf-8")
        except OSError:
            return False, "no-tty"
        try:
            tty.write(f"\n[scoped] approval required: {tool}\n")
            tty.write(f"  reason: {reason}\n")
            tty.write(f"  args: {args}\n")
            tty.write("  allow once? [y/N] ")
            tty.flush()
            answer = tty.readline().strip().lower()
        finally:
            tty.close()
        if answer in {"y", "yes", "allow", "a"}:
            return True, "user"
        return False, "user-deny"

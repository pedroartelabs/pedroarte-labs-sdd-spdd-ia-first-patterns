"""Shared utilities for Claude Code hooks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load_hook_input() -> dict[str, Any]:
    """Read the JSON hook payload from stdin."""
    return json.loads(sys.stdin.read())  # type: ignore[no-any-return]


def block(reason: str) -> None:
    """Exit with a blocking response."""
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def allow() -> None:
    """Exit with an allowing response."""
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


def project_root() -> Path:
    """Find the repository root by walking up from this script."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists() or (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path.cwd()

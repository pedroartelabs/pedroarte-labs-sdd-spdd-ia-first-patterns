"""PreToolUse hook: block destructive commands and secret exposure.

Runs before every Bash/PowerShell tool call. Checks the command against the
deny list from security-policy.yaml and blocks known-dangerous patterns.
"""

from __future__ import annotations

import re

from common import allow, block, load_hook_input

DESTRUCTIVE_PATTERNS: list[str] = [
    r"git\s+push\s+(-f|--force)",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+-fdx",
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"Remove-Item\s+-Recurse\s+-Force\s+C:\\",
    r"git\s+filter-branch",
    r"gh\s+repo\s+delete",
    r"gh\s+release\s+delete",
    r"DROP\s+DATABASE",
    r"DROP\s+TABLE",
    r"truncate\s+-s\s+0",
    r"mkfs",
    r"chmod\s+-R\s+777",
]

SECRET_PATTERNS: list[str] = [
    r"ghp_[A-Za-z0-9_]{36}",
    r"gho_[A-Za-z0-9_]{36}",
    r"ghs_[A-Za-z0-9_]{36}",
    r"sk-[A-Za-z0-9]{48}",
    r"AKIA[A-Z0-9]{16}",
    r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
    r"xoxb-[0-9]+-[A-Za-z0-9]+",
    r"AIza[A-Za-z0-9_-]{35}",
]


def main() -> None:
    data = load_hook_input()
    tool_name = data.get("tool_name", "")

    if tool_name not in ("Bash", "PowerShell"):
        allow()
        return

    command = data.get("tool_input", {}).get("command", "")

    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            block(
                f"Blocked destructive command matching pattern: {pattern}. "
                "See governance/policies/security-policy.yaml THR-004."
            )
            return

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, command):
            block(
                "Blocked command containing what appears to be a secret or token. "
                "See governance/policies/security-policy.yaml SEC-001."
            )
            return

    allow()


if __name__ == "__main__":
    main()

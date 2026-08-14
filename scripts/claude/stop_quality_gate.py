"""PreToolUse hook: block edits that weaken quality gates.

Checks for patterns that indicate a quality gate is being weakened:
- Lowering coverage thresholds
- Disabling or skipping tests
- Suppressing lint rules without justification
"""

from __future__ import annotations

import re

from common import allow, block, load_hook_input

WEAKENING_PATTERNS: list[tuple[str, str]] = [
    (
        r"@pytest\.mark\.skip",
        "Skipping a test without a linked issue violates TEST-001.",
    ),
    (
        r"pytest\.skip\(",
        "Skipping a test without a linked issue violates TEST-001.",
    ),
    (
        r"@Disabled",
        "Disabling a test without a linked issue violates TEST-001.",
    ),
    (
        r"@Ignore",
        "Ignoring a test without a linked issue violates TEST-001.",
    ),
    (
        r"#\s*noqa(?!:)",
        "Bare noqa without a specific code suppresses all warnings. Use noqa: CODE.",
    ),
    (
        r"#\s*type:\s*ignore(?!\[)",
        "Bare type: ignore without a specific error code. Use type: ignore[code].",
    ),
    (
        r"@SuppressWarnings\s*\(\s*\"all\"\s*\)",
        "SuppressWarnings(\"all\") suppresses every warning. Be specific.",
    ),
]


def main() -> None:
    data = load_hook_input()
    tool_name = data.get("tool_name", "")

    if tool_name not in ("Edit", "Write"):
        allow()
        return

    content = data.get("tool_input", {}).get("content", "")
    if not content:
        content = data.get("tool_input", {}).get("new_string", "")

    if not content:
        allow()
        return

    for pattern, message in WEAKENING_PATTERNS:
        if re.search(pattern, content):
            block(
                f"{message} "
                "If this is intentional, add a justification comment and a linked issue."
            )
            return

    allow()


if __name__ == "__main__":
    main()

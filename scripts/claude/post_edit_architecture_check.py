"""PostToolUse hook: warn when an edit touches a domain or application file.

Runs after every Edit/Write tool call. If the edited file is in a domain or
application layer, reminds the agent to verify architecture rules.
"""

from __future__ import annotations

import json
import sys

from common import load_hook_input

DOMAIN_MARKERS = [
    "/domain/",
    "\\domain\\",
    "/application/",
    "\\application\\",
]

GENERATED_FILE_MARKERS = [
    "DO NOT EDIT",
    "Generated from governance/policies",
]


def main() -> None:
    data = load_hook_input()
    tool_name = data.get("tool_name", "")

    if tool_name not in ("Edit", "Write"):
        print(json.dumps({}))
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")

    warnings: list[str] = []

    for marker in DOMAIN_MARKERS:
        if marker in file_path:
            warnings.append(
                f"Edited a file in the {marker.strip('/').strip(chr(92))} layer. "
                "Run `lint-imports` or `make verify-architecture` to confirm no "
                "architecture violation was introduced."
            )
            break

    content = data.get("tool_input", {}).get("content", "")
    if not content:
        content = data.get("tool_input", {}).get("new_string", "")

    for marker in GENERATED_FILE_MARKERS:
        if marker in file_path or (content and marker in content[:500]):
            warnings.append(
                "This file appears to be generated from canonical policy. "
                "Edit governance/policies/ instead, then run `make generate-agent-rules`."
            )
            break

    if warnings:
        print(json.dumps({"warnings": warnings}))
    else:
        print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()

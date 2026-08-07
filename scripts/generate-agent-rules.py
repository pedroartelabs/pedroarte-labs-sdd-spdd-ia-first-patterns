#!/usr/bin/env python3
"""Generate agent instruction files from the canonical policies.

One source of truth (`governance/policies/`), many generated representations
(`CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, Copilot, Cursor). Editing a
generated file by hand is a mistake the drift checker will catch; edit the
policy and regenerate instead.

Usage:
    python scripts/generate-agent-rules.py            # write the files
    python scripts/generate-agent-rules.py --check    # report drift, write nothing
    python scripts/generate-agent-rules.py --list     # list generated paths
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy_lib import (  # noqa: E402  (path shim must run first)
    GENERATED_FILES,
    REPO_ROOT,
    load_policies,
    read_existing,
    render_all,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero when any generated file is out of date",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print the generated file paths and exit",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root (defaults to the parent of scripts/)",
    )
    args = parser.parse_args()

    if args.list:
        for rel in GENERATED_FILES:
            print(rel)
        return 0

    policies = load_policies(args.repo_root / "governance" / "policies")
    rendered = render_all(policies)

    changed: list[str] = []
    created: list[str] = []

    for rel, content in rendered.items():
        existing = read_existing(args.repo_root, rel)
        if existing is None:
            created.append(rel)
        elif existing != content:
            changed.append(rel)

    if args.check:
        if not changed and not created:
            print(f"OK: {len(rendered)} generated files match policy "
                  f"(sha256:{policies.checksum[:16]}…)")
            return 0
        for rel in created:
            print(f"MISSING: {rel}")
        for rel in changed:
            print(f"OUT OF DATE: {rel}")
        print("\nRun `make generate-agent-rules` and commit the result.")
        return 1

    for rel, content in rendered.items():
        path = args.repo_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" keeps generated output byte-identical on Windows and
        # Linux, which is what makes the drift check trustworthy in CI.
        path.write_text(content, encoding="utf-8", newline="\n")

    total = len(rendered)
    if created or changed:
        for rel in created:
            print(f"created  {rel}")
        for rel in changed:
            print(f"updated  {rel}")
        print(f"\n{total} files generated from policy sha256:{policies.checksum[:16]}…")
    else:
        print(f"{total} files already up to date (sha256:{policies.checksum[:16]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

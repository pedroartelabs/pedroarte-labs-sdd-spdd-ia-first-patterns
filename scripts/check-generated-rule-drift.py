#!/usr/bin/env python3
"""Fail when generated agent instructions no longer match canonical policy.

This is the control that stops the most dangerous silent failure in the whole
repository: rules that agents read having quietly diverged from the rules the
project actually approved.

It catches three distinct situations, and reports them differently because the
fix differs:

1. A canonical policy changed and the generated files were not regenerated.
2. A generated file was edited by hand.
3. A generated file is missing entirely.

Cases 1 and 2 look identical from a pure content diff, so we additionally
compare the policy checksum embedded in each generated header against the
checksum of the policies on disk. That tells the two apart and lets the message
point at the right fix.

Usage:
    python scripts/check-generated-rule-drift.py
    python scripts/check-generated-rule-drift.py --verbose
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy_lib import (  # noqa: E402  (path shim must run first)
    REPO_ROOT,
    load_policies,
    read_existing,
    render_all,
)

CHECKSUM_RE = re.compile(r"Policy checksum: sha256:([0-9a-f]{64})")


def embedded_checksum(content: str) -> str | None:
    match = CHECKSUM_RE.search(content)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="print a unified diff for each drifted file")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    policies = load_policies(args.repo_root / "governance" / "policies")
    rendered = render_all(policies)

    missing: list[str] = []
    stale_policy: list[str] = []
    hand_edited: list[str] = []

    for rel, expected in rendered.items():
        actual = read_existing(args.repo_root, rel)
        if actual is None:
            missing.append(rel)
            continue
        if actual == expected:
            continue

        found = embedded_checksum(actual)
        if found is None or found != policies.checksum:
            # The file was generated from a different policy revision.
            stale_policy.append(rel)
        else:
            # Same policy revision, different content: a human typed in it.
            hand_edited.append(rel)

        if args.verbose:
            diff = difflib.unified_diff(
                actual.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=f"{rel} (on disk)",
                tofile=f"{rel} (expected from policy)",
                n=2,
            )
            sys.stdout.writelines(diff)
            print()

    if not (missing or stale_policy or hand_edited):
        print(f"OK: {len(rendered)} generated files match governance/policies/ "
              f"(sha256:{policies.checksum[:16]}…)")
        return 0

    print("Generated agent instructions have drifted from canonical policy.\n")

    if missing:
        print("Missing generated files:")
        for rel in missing:
            print(f"  - {rel}")
        print()

    if stale_policy:
        print("Policy changed but these files were not regenerated:")
        for rel in stale_policy:
            print(f"  - {rel}")
        print("  Fix: run `make generate-agent-rules` and commit the result.\n")

    if hand_edited:
        print("These files were edited by hand (their checksum matches the current")
        print("policy, but their content does not match what the policy renders):")
        for rel in hand_edited:
            print(f"  - {rel}")
        print("  Fix: revert the manual edit, change governance/policies/ instead,")
        print("       then run `make generate-agent-rules`.\n")

    print("Canonical source: governance/policies/")
    print("Rationale: docs/decisions/ADR-0002-canonical-machine-readable-policies.md")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

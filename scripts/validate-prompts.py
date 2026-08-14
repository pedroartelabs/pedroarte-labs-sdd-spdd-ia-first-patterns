"""Validate SPDD REASONS prompts against the schema and completeness rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROMPT_ID_PATTERN = re.compile(r"^PROMPT-(?:\d{4}-\d{3}|EXAMPLE-\d{3})$")

REQUIRED_FRONTMATTER = [
    "prompt_id", "spec_id", "version", "status",
    "created_at",
]

REASONS_SECTIONS = [
    "Requirements", "Entities", "Approach",
    "Structure", "Operations", "Norms", "Safeguards",
]

MANDATORY_SAFEGUARD_KEYWORDS = [
    ["modify files outside", "declared scope"],
    ["domain logic", "adapter"],
    ["framework", "domain"],
    ["disable", "skip", "test"],
    ["weaken", "quality gate"],
]


def extract_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def validate_prompt(path: Path) -> list[str]:
    errors: list[str] = []
    name = path.name

    fm = extract_frontmatter(path)
    if fm is None:
        errors.append(f"{name}: no YAML frontmatter found")
        return errors

    for field in REQUIRED_FRONTMATTER:
        if field not in fm or fm[field] is None:
            errors.append(f"{name}: missing required field '{field}'")

    prompt_id = fm.get("prompt_id", "")
    if not PROMPT_ID_PATTERN.match(str(prompt_id)):
        errors.append(f"{name}: invalid PROMPT-ID format '{prompt_id}'")

    status = fm.get("status", "")
    if status == "APPROVED":
        approved_by = fm.get("approved_by", "pending")
        if approved_by == "pending":
            errors.append(f"{name}: APPROVED status requires non-pending approved_by")

    text = path.read_text(encoding="utf-8")
    for section in REASONS_SECTIONS:
        letter = section[0]
        patterns = [f"## {section}", f"## {letter} — {section}", f"## {letter} - {section}"]
        if not any(p in text for p in patterns):
            errors.append(f"{name}: missing REASONS section '{section}'")

    text_lower = text.lower()
    for keywords in MANDATORY_SAFEGUARD_KEYWORDS:
        if not any(all(kw in line for kw in keywords) for line in text_lower.split("\n")):
            errors.append(f"{name}: missing mandatory safeguard containing: {keywords}")

    return errors


def main() -> None:
    all_errors: list[str] = []

    for prompt_file in sorted(PROJECT_ROOT.rglob("prompt.reasons.md")):
        if "templates" in str(prompt_file):
            continue
        all_errors.extend(validate_prompt(prompt_file))

    if all_errors:
        print("Prompt validation FAILED:")
        for e in all_errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("Prompt validation PASSED.")


if __name__ == "__main__":
    main()

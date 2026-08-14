"""Validate SDD specifications against lifecycle rules and schema."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = PROJECT_ROOT / "specs"

REQUIRED_FRONTMATTER = [
    "id", "title", "status", "type", "owner",
    "created_at", "updated_at", "languages",
    "bounded_context", "risk_level",
]

VALID_STATUSES = {
    "DRAFT", "IN_REVIEW", "APPROVED", "IMPLEMENTING",
    "VERIFIED", "RELEASED", "REJECTED", "SUPERSEDED",
    "DEPRECATED", "CANCELLED", "HOTFIX",
}

SPEC_ID_PATTERN = re.compile(r"^SPEC-(?:\d{4}-\d{3}|EXAMPLE-\d{3})$")


def extract_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def validate_spec(spec_dir: Path) -> list[str]:
    errors: list[str] = []
    spec_file = spec_dir / "spec.md"

    if not spec_file.exists():
        errors.append(f"{spec_dir.name}: missing spec.md")
        return errors

    fm = extract_frontmatter(spec_file)
    if fm is None:
        errors.append(f"{spec_dir.name}: no YAML frontmatter found")
        return errors

    for field in REQUIRED_FRONTMATTER:
        if field not in fm or fm[field] is None or fm[field] == "":
            errors.append(f"{spec_dir.name}: missing required field '{field}'")

    spec_id = fm.get("id", "")
    if not SPEC_ID_PATTERN.match(str(spec_id)):
        errors.append(f"{spec_dir.name}: invalid SPEC-ID format '{spec_id}'")

    status = fm.get("status", "")
    if status not in VALID_STATUSES:
        errors.append(f"{spec_dir.name}: invalid status '{status}'")

    if status in ("IMPLEMENTING", "VERIFIED", "RELEASED"):
        prompts = fm.get("prompt_artifacts", [])
        if not prompts:
            errors.append(f"{spec_dir.name}: status {status} requires prompt_artifacts")

    if status in ("VERIFIED", "RELEASED"):
        if not (spec_dir / "evidence.md").exists():
            errors.append(f"{spec_dir.name}: status {status} requires evidence.md")

    if status == "RELEASED":
        if not (spec_dir / "traceability.yaml").exists():
            errors.append(f"{spec_dir.name}: status RELEASED requires traceability.yaml")

    return errors


def main() -> None:
    all_errors: list[str] = []

    for spec_dir in sorted(SPECS_DIR.rglob("spec.md")):
        parent = spec_dir.parent
        if "templates" in str(parent):
            continue
        all_errors.extend(validate_spec(parent))

    if all_errors:
        print("Specification validation FAILED:")
        for e in all_errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("Specification validation PASSED.")


if __name__ == "__main__":
    main()
